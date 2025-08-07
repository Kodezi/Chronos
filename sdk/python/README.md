# Kodezi Chronos Python SDK

Official Python SDK for the Kodezi Chronos Autonomous Debugging System.

## Installation

```bash
pip install kodezi-chronos
```

## Quick Start

```python
from kodezi_chronos import ChronosClient, InputType

# Initialize client
client = ChronosClient(api_key="your-api-key")

# Debug a stack trace
result = client.debug(
    error_input="""
    TypeError: 'NoneType' object is not subscriptable
      File "app.py", line 45, in process
        return data['key']
    """,
    input_type=InputType.STACK_TRACE,
    metadata={"repository": "my-app", "branch": "main"}
)

if result.success:
    print(f"Bug fixed with {result.confidence*100:.1f}% confidence!")
    print(f"Files changed: {result.files_changed}")
    print(f"Explanation: {result.explanation}")
```

## Async Usage

```python
import asyncio
from kodezi_chronos import AsyncChronosClient, InputType

async def debug_async():
    async with AsyncChronosClient(api_key="your-api-key") as client:
        result = await client.debug(
            error_input="Error log content...",
            input_type=InputType.ERROR_LOG
        )
        return result

# Run async
result = asyncio.run(debug_async())
```

## Batch Debugging

```python
# Debug multiple issues at once
issues = [
    {
        "id": "issue_1",
        "error_input": "Stack trace 1...",
        "input_type": "stack_trace"
    },
    {
        "id": "issue_2", 
        "error_input": {"test_failures": [...]},
        "input_type": "test_output"
    }
]

batch_result = client.debug_batch(issues)
print(f"Success rate: {batch_result.success_rate*100:.1f}%")
```

## Input Types

The SDK supports various input types:

- `InputType.STACK_TRACE` - Python/Java/JS stack traces
- `InputType.ERROR_LOG` - Application error logs
- `InputType.TEST_OUTPUT` - Test failures (pytest, Jest, JUnit)
- `InputType.CI_CD_LOG` - CI/CD pipeline logs
- `InputType.PERFORMANCE_PROFILE` - Performance profiling data
- `InputType.USER_REPORT` - User bug reports
- `InputType.MONITORING_ALERT` - Monitoring system alerts
- `InputType.API_RESPONSE` - API error responses

## Environment Variables

- `CHRONOS_API_KEY` - API key for authentication
- `CHRONOS_BASE_URL` - Override base URL (default: https://api.kodezi.com/chronos/v1)

## Error Handling

```python
from kodezi_chronos import ChronosClient, ChronosException, RateLimitError

try:
    result = client.debug(error_input, InputType.STACK_TRACE)
except RateLimitError as e:
    print(f"Rate limited: {e}")
    # Wait and retry
except ChronosException as e:
    print(f"Error: {e}")
```

## CLI Usage

The SDK includes a command-line interface:

```bash
# Debug from file
chronos debug error.log --type error-log

# Quick debug
chronos quick "TypeError: 'NoneType' object..." 

# Check stats
chronos stats

# System status
chronos status
```

## Examples

### Debug Test Failure

```python
test_failure = {
    "failures": [
        {
            "test_name": "test_user_creation",
            "error": "AssertionError: User not created",
            "stack_trace": "File 'tests/test_user.py', line 20"
        }
    ],
    "test_suite": "user_tests",
    "total_tests": 25,
    "passed": 24,
    "failed": 1
}

result = client.debug(
    error_input=test_failure,
    input_type=InputType.TEST_OUTPUT
)
```

### Debug Performance Issue

```python
performance_data = {
    "cpu_usage": 95.5,
    "memory_usage": 2048,
    "hotspots": [
        {
            "function": "calculate_recommendations",
            "file": "recommendation_engine.py",
            "cpu_percent": 73.2
        }
    ]
}

result = client.debug(
    error_input=performance_data,
    input_type=InputType.PERFORMANCE_PROFILE
)
```

## Support

- Documentation: https://docs.kodezi.com/chronos
- Issues: https://github.com/kodezi/chronos-python-sdk/issues
- Support: support@kodezi.com