#!/usr/bin/env python3
"""
API Usage Example: Building a debugging service with Kodezi Chronos
Shows how to integrate Chronos into a web service
"""

from flask import Flask, request, jsonify
from chronos_integration import create_chronos_system, InputType
import logging
import json
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize Chronos globally
chronos = create_chronos_system(
    repository_path="/var/repositories/main",
    use_docker_sandbox=True,
    max_iterations=10,
    confidence_threshold=0.75,
    memory_db_path="/var/chronos/memory.db",
    enable_caching=True
)

# Thread pool for async operations
executor = ThreadPoolExecutor(max_workers=10)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    status = chronos.get_system_status()
    return jsonify({
        'status': 'healthy',
        'chronos': status['initialized'],
        'layers': status['layers'],
        'statistics': status['statistics']
    })

@app.route('/debug', methods=['POST'])
def debug_endpoint():
    """Main debugging endpoint"""
    try:
        data = request.json
        
        # Validate input
        if not data.get('error_input'):
            return jsonify({'error': 'error_input is required'}), 400
        
        if not data.get('input_type'):
            return jsonify({'error': 'input_type is required'}), 400
        
        # Map string to InputType enum
        input_type_map = {
            'stack_trace': InputType.STACK_TRACE,
            'error_log': InputType.ERROR_LOG,
            'test_output': InputType.TEST_OUTPUT,
            'ci_cd_log': InputType.CI_CD_LOG,
            'performance_profile': InputType.PERFORMANCE_PROFILE,
            'user_report': InputType.USER_REPORT,
            'monitoring_alert': InputType.MONITORING_ALERT,
            'api_response': InputType.API_RESPONSE
        }
        
        input_type = input_type_map.get(data['input_type'])
        if not input_type:
            return jsonify({'error': 'Invalid input_type'}), 400
        
        # Extract metadata
        metadata = data.get('metadata', {})
        metadata['api_request_id'] = request.headers.get('X-Request-ID', 'unknown')
        metadata['timestamp'] = datetime.now().isoformat()
        
        # Run debugging
        result = chronos.debug(
            error_input=data['error_input'],
            input_type=input_type,
            metadata=metadata
        )
        
        # Format response
        response = {
            'session_id': result['session_id'],
            'success': result['success'],
            'total_time': result['total_time'],
            'iterations': result['iterations']
        }
        
        if result['success']:
            response['fix'] = {
                'confidence': result['fix']['confidence'],
                'files': result['fix']['files']
            }
            response['explanation'] = result.get('explanation', '')
            response['validation'] = result.get('validation', {})
        else:
            response['error'] = 'Unable to automatically fix the issue'
            response['suggestions'] = [
                'Review the error manually',
                'Provide more context',
                'Check similar issues in the codebase'
            ]
        
        return jsonify(response)
        
    except Exception as e:
        logging.error(f"Error in debug endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/debug/async', methods=['POST'])
async def debug_async_endpoint():
    """Async debugging endpoint for non-blocking operations"""
    try:
        data = request.json
        
        # Validate input (same as sync endpoint)
        if not data.get('error_input') or not data.get('input_type'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Start async debugging
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(
            executor,
            lambda: chronos.debug(
                error_input=data['error_input'],
                input_type=InputType[data['input_type'].upper()],
                metadata=data.get('metadata', {})
            )
        )
        
        # Return job ID immediately
        job_id = f"debug_job_{int(datetime.now().timestamp() * 1000)}"
        
        # Store job for later retrieval (in production, use Redis/database)
        app.config.setdefault('JOBS', {})[job_id] = future
        
        return jsonify({
            'job_id': job_id,
            'status': 'processing',
            'message': 'Debug job started. Check status using job_id.'
        }), 202
        
    except Exception as e:
        logging.error(f"Error in async debug endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/debug/status/<job_id>', methods=['GET'])
def check_job_status(job_id):
    """Check status of async debugging job"""
    jobs = app.config.get('JOBS', {})
    
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    future = jobs[job_id]
    
    if future.done():
        try:
            result = future.result()
            return jsonify({
                'job_id': job_id,
                'status': 'completed',
                'result': {
                    'success': result['success'],
                    'session_id': result['session_id'],
                    'fix': result.get('fix') if result['success'] else None
                }
            })
        except Exception as e:
            return jsonify({
                'job_id': job_id,
                'status': 'failed',
                'error': str(e)
            }), 500
    else:
        return jsonify({
            'job_id': job_id,
            'status': 'processing'
        }), 202

@app.route('/debug/batch', methods=['POST'])
def batch_debug_endpoint():
    """Debug multiple issues in batch"""
    try:
        data = request.json
        
        if not data.get('issues') or not isinstance(data['issues'], list):
            return jsonify({'error': 'issues array is required'}), 400
        
        results = []
        
        for issue in data['issues']:
            try:
                result = chronos.debug(
                    error_input=issue['error_input'],
                    input_type=InputType[issue['input_type'].upper()],
                    metadata=issue.get('metadata', {})
                )
                
                results.append({
                    'id': issue.get('id', 'unknown'),
                    'success': result['success'],
                    'session_id': result['session_id'],
                    'confidence': result['fix']['confidence'] if result['success'] else 0
                })
            except Exception as e:
                results.append({
                    'id': issue.get('id', 'unknown'),
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'total': len(results),
            'successful': sum(1 for r in results if r['success']),
            'results': results
        })
        
    except Exception as e:
        logging.error(f"Error in batch debug endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/stats', methods=['GET'])
def get_statistics():
    """Get debugging statistics"""
    status = chronos.get_system_status()
    stats = status['statistics']
    
    return jsonify({
        'total_sessions': stats['total_sessions'],
        'success_rate': f"{stats['success_rate']*100:.1f}%",
        'average_iterations': stats['average_iterations'],
        'cache_hit_rate': f"{stats['cache_hit_rate']*100:.1f}%",
        'memory_sessions': status['memory_sessions'],
        'system_uptime': 'N/A'  # Would calculate in production
    })

# Example client code
def example_client():
    """Example of how to use the API"""
    import requests
    
    # Example 1: Simple debugging request
    response = requests.post('http://localhost:5000/debug', json={
        'error_input': """
        TypeError: 'NoneType' object is not subscriptable
          File "app.py", line 45, in process
            return data['key']
        """,
        'input_type': 'stack_trace',
        'metadata': {
            'user_id': '12345',
            'environment': 'production'
        }
    })
    
    print("Debug Response:", response.json())
    
    # Example 2: Async debugging
    response = requests.post('http://localhost:5000/debug/async', json={
        'error_input': {
            'failures': [{'test_name': 'test_login', 'error': 'AssertionError'}]
        },
        'input_type': 'test_output'
    })
    
    job_data = response.json()
    job_id = job_data['job_id']
    
    # Poll for results
    import time
    while True:
        status_response = requests.get(f'http://localhost:5000/debug/status/{job_id}')
        status_data = status_response.json()
        
        if status_data['status'] == 'completed':
            print("Async Debug Result:", status_data['result'])
            break
        elif status_data['status'] == 'failed':
            print("Debug Failed:", status_data['error'])
            break
        
        time.sleep(1)  # Wait 1 second before polling again

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)