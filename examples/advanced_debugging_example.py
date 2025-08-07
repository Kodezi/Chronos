#!/usr/bin/env python3
"""
Advanced Example: Using Kodezi Chronos with Multiple Input Types
Demonstrates debugging with various error sources and async operations
"""

import asyncio
from chronos_integration import create_chronos_system, InputType
import json

async def main():
    """Advanced debugging examples with multiple scenarios"""
    
    # Initialize Chronos
    chronos = create_chronos_system(
        repository_path="/path/to/your/repository",
        use_docker_sandbox=True,  # Full isolation
        max_iterations=15,  # Allow more iterations for complex bugs
        confidence_threshold=0.8,  # Higher confidence requirement
        memory_db_path="chronos_memory_prod.db"
    )
    
    print("🚀 Kodezi Chronos Advanced Debugging Examples")
    print("=" * 60)
    
    # Example 1: Debug test failure
    test_failure = {
        "failures": [
            {
                "test_name": "test_concurrent_user_creation",
                "error": "AssertionError: Race condition detected",
                "stack_trace": """
                File 'tests/test_concurrency.py', line 45, in test_concurrent_user_creation
                    assert len(created_users) == expected_count
                AssertionError: Expected 100 but got 98
                """
            }
        ],
        "test_suite": "concurrency_tests",
        "total_tests": 50,
        "passed": 49,
        "failed": 1
    }
    
    print("\n1️⃣ Debugging Concurrency Test Failure")
    print("-" * 60)
    
    result1 = await chronos.debug_async(
        error_input=test_failure,
        input_type=InputType.TEST_OUTPUT,
        metadata={
            'source': 'pytest',
            'test_type': 'concurrency',
            'priority': 'high'
        }
    )
    
    print_result_summary("Concurrency Bug", result1)
    
    # Example 2: Debug performance issue
    performance_profile = {
        "cpu_usage": 95.5,
        "memory_usage": 2048,
        "hotspots": [
            {
                "function": "calculate_recommendations",
                "file": "services/recommendation_engine.py",
                "cpu_percent": 73.2,
                "calls": 1000000
            }
        ],
        "slow_queries": [
            {
                "query": "SELECT * FROM users WHERE ...",
                "avg_time": 2.5,
                "count": 1000
            }
        ]
    }
    
    print("\n2️⃣ Debugging Performance Bottleneck")
    print("-" * 60)
    
    result2 = await chronos.debug_async(
        error_input=performance_profile,
        input_type=InputType.PERFORMANCE_PROFILE,
        metadata={
            'source': 'profiler',
            'environment': 'production',
            'load': 'high'
        }
    )
    
    print_result_summary("Performance Issue", result2)
    
    # Example 3: Debug from monitoring alert
    monitoring_alert = {
        "alert_name": "High Error Rate",
        "message": "Error rate exceeded 5% threshold",
        "severity": "critical",
        "metrics": {
            "error_rate": 7.3,
            "response_time_p99": 3500,
            "requests_per_second": 1000
        },
        "service": "payment_service",
        "recent_errors": [
            "ConnectionTimeout: Database connection timed out",
            "ValidationError: Invalid payment method"
        ]
    }
    
    print("\n3️⃣ Debugging from Monitoring Alert")
    print("-" * 60)
    
    result3 = await chronos.debug_async(
        error_input=monitoring_alert,
        input_type=InputType.MONITORING_ALERT,
        metadata={
            'source': 'datadog',
            'severity': 'critical',
            'auto_triggered': True
        }
    )
    
    print_result_summary("Monitoring Alert", result3)
    
    # Example 4: Debug CI/CD failure
    ci_log = """
    [GitHub Actions] Build #1234 started
    [INFO] Running tests...
    [ERROR] Build failed: 
    
    ======================== FAILURES ========================
    _________________ test_database_migration _________________
    
    E   psycopg2.errors.UndefinedTable: relation "users_v2" does not exist
    E   LINE 1: SELECT * FROM users_v2 WHERE ...
    
    tests/test_migrations.py:78: UndefinedTable
    ===================== 1 failed, 99 passed ==================
    ##[error]Process completed with exit code 1.
    """
    
    print("\n4️⃣ Debugging CI/CD Pipeline Failure")
    print("-" * 60)
    
    result4 = await chronos.debug_async(
        error_input=ci_log,
        input_type=InputType.CI_CD_LOG,
        metadata={
            'source': 'github_actions',
            'branch': 'feature/database-upgrade',
            'commit': 'abc123def',
            'pull_request': '#456'
        }
    )
    
    print_result_summary("CI/CD Failure", result4)
    
    # Display overall system performance
    print("\n📊 Overall System Performance")
    print("=" * 60)
    status = chronos.get_system_status()
    print(json.dumps(status, indent=2))

def print_result_summary(bug_type: str, result: dict):
    """Pretty print debugging result summary"""
    if result['success']:
        print(f"✅ {bug_type} fixed successfully!")
        print(f"   • Confidence: {result['fix']['confidence']*100:.1f}%")
        print(f"   • Iterations: {result['iterations']}")
        print(f"   • Time: {result['total_time']:.2f}s")
        
        # Show root cause
        if result['error_info']:
            print(f"   • Root Cause: {result['error_info']['type']}")
        
        # Show fix summary
        if result['fix']['files']:
            print(f"   • Files Modified: {len(result['fix']['files'])}")
            for file in list(result['fix']['files'].keys())[:3]:
                print(f"     - {file}")
        
        # Show validation results
        if result['validation']:
            print(f"   • Test Validation: {'✓ PASS' if result['validation']['tests_pass'] else '✗ FAIL'}")
    else:
        print(f"❌ {bug_type} could not be fixed automatically")
        print(f"   • Iterations attempted: {result['iterations']}")
        print(f"   • Consider manual debugging")

if __name__ == "__main__":
    asyncio.run(main())