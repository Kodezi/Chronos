#!/usr/bin/env python3
"""
Basic Example: Using Kodezi Chronos for Debugging
Demonstrates simple null pointer exception debugging
"""

from chronos_integration import create_chronos_system, InputType
import json

def main():
    """Basic debugging example"""
    
    # Initialize Chronos for your repository
    chronos = create_chronos_system(
        repository_path="/path/to/your/repository",
        use_docker_sandbox=False,  # Set to True for production
        max_iterations=10,
        confidence_threshold=0.75
    )
    
    # Example 1: Debug a Python NullPointerException
    python_error = """
TypeError: 'NoneType' object is not subscriptable
  File "services/user_service.py", line 45, in get_user_name
    return user['name']
  File "api/handlers.py", line 123, in handle_request
    name = get_user_name(user_id)
  File "main.py", line 67, in process_api_call
    result = handle_request(request)
"""
    
    print("🐛 Debugging Python TypeError...")
    print("-" * 60)
    
    # Run Chronos debugging
    result = chronos.debug(
        error_input=python_error,
        input_type=InputType.STACK_TRACE,
        metadata={
            'source': 'python_api',
            'repository': 'user_service',
            'environment': 'production'
        }
    )
    
    # Display results
    if result['success']:
        print(f"✅ Bug fixed successfully!")
        print(f"   Confidence: {result['fix']['confidence']*100:.1f}%")
        print(f"   Iterations: {result['iterations']}")
        print(f"   Time: {result['total_time']:.2f}s")
        
        if result['explanation']:
            print("\n📝 Explanation:")
            print(result['explanation'][:500] + "...")
        
        print("\n💻 Proposed Fix:")
        print(json.dumps(result['fix']['files'], indent=2))
        
        if result['validation']:
            print(f"\n✓ Tests Pass: {result['validation']['tests_pass']}")
            print(f"✓ Coverage Change: {result['validation']['coverage_change']:+.1f}%")
    else:
        print("❌ Unable to fix bug automatically")
        print(f"   Iterations attempted: {result['iterations']}")
    
    # Show system statistics
    stats = result['statistics']
    print(f"\n📊 System Statistics:")
    print(f"   Total sessions: {stats['total_sessions']}")
    print(f"   Success rate: {stats['success_rate']*100:.1f}%")
    print(f"   Avg iterations: {stats['average_iterations']:.1f}")
    print(f"   Cache hit rate: {stats['cache_hit_rate']*100:.1f}%")

if __name__ == "__main__":
    main()