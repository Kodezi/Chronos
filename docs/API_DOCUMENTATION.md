# Kodezi Chronos API Documentation

## Overview

Kodezi Chronos provides a RESTful API for autonomous debugging services. This documentation covers the endpoints, request/response formats, and integration examples.

## Base URL

```
https://api.kodezi.com/chronos/v1
```

## Authentication

All API requests require authentication using an API key:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.kodezi.com/chronos/v1/debug
```

## Endpoints

### 1. Debug Endpoint

**POST** `/debug`

Submit a debugging request.

#### Request Body

```json
{
  "error_input": "string or object",
  "input_type": "stack_trace|error_log|test_output|ci_cd_log|performance_profile|user_report|monitoring_alert|api_response",
  "metadata": {
    "repository": "string",
    "branch": "string",
    "commit": "string",
    "environment": "string",
    "priority": "low|medium|high|critical"
  }
}
```

#### Response

```json
{
  "session_id": "debug_1234567890",
  "success": true,
  "total_time": 4.32,
  "iterations": 3,
  "fix": {
    "confidence": 0.87,
    "files": {
      "src/user_service.py": "# Fixed code content..."
    }
  },
  "explanation": "## Debug Report\n\n### Summary\nIdentified and fixed a null pointer issue...",
  "validation": {
    "tests_pass": true,
    "coverage_change": 2.3,
    "performance_impact": {
      "cpu_impact": "negligible",
      "memory_impact": "negligible"
    }
  }
}
```

### 2. Async Debug Endpoint

**POST** `/debug/async`

Submit an asynchronous debugging request for long-running operations.

#### Request

Same as synchronous debug endpoint.

#### Response

```json
{
  "job_id": "debug_job_1234567890",
  "status": "processing",
  "message": "Debug job started. Check status using job_id."
}
```

### 3. Job Status Endpoint

**GET** `/debug/status/{job_id}`

Check the status of an asynchronous debugging job.

#### Response

```json
{
  "job_id": "debug_job_1234567890",
  "status": "completed|processing|failed",
  "result": {
    "success": true,
    "session_id": "debug_1234567890",
    "fix": {
      "confidence": 0.87,
      "files": {}
    }
  }
}
```

### 4. Batch Debug Endpoint

**POST** `/debug/batch`

Debug multiple issues in a single request.

#### Request

```json
{
  "issues": [
    {
      "id": "issue_1",
      "error_input": "...",
      "input_type": "stack_trace",
      "metadata": {}
    },
    {
      "id": "issue_2",
      "error_input": "...",
      "input_type": "test_output",
      "metadata": {}
    }
  ]
}
```

#### Response

```json
{
  "total": 2,
  "successful": 1,
  "results": [
    {
      "id": "issue_1",
      "success": true,
      "session_id": "debug_123",
      "confidence": 0.85
    },
    {
      "id": "issue_2",
      "success": false,
      "error": "Unable to identify issue"
    }
  ]
}
```

### 5. Statistics Endpoint

**GET** `/stats`

Get debugging statistics.

#### Response

```json
{
  "total_sessions": 15420,
  "success_rate": "67.3%",
  "average_iterations": 7.8,
  "cache_hit_rate": "87.0%",
  "memory_sessions": 1000000,
  "system_uptime": "14d 3h 22m"
}
```

### 6. Health Check Endpoint

**GET** `/health`

Check system health.

#### Response

```json
{
  "status": "healthy",
  "chronos": true,
  "layers": {
    "input": "ready",
    "agr": "ready",
    "llm": "ready",
    "orchestrator": "ready",
    "pdm": "ready",
    "sandbox": "ready",
    "explainer": "ready"
  },
  "statistics": {
    "total_sessions": 15420,
    "success_rate": 0.673
  }
}
```

## Input Types

### Stack Trace

```json
{
  "error_input": "TypeError: 'NoneType' object is not subscriptable\n  File \"app.py\", line 45, in process\n    return data['key']",
  "input_type": "stack_trace"
}
```

### Test Output

```json
{
  "error_input": {
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
  },
  "input_type": "test_output"
}
```

### Performance Profile

```json
{
  "error_input": {
    "cpu_usage": 95.5,
    "memory_usage": 2048,
    "hotspots": [
      {
        "function": "calculate_recommendations",
        "file": "services/recommendation_engine.py",
        "cpu_percent": 73.2
      }
    ]
  },
  "input_type": "performance_profile"
}
```

### CI/CD Log

```json
{
  "error_input": "[ERROR] Build failed: \ntest_database_migration FAILED\npsycopg2.errors.UndefinedTable: relation \"users_v2\" does not exist",
  "input_type": "ci_cd_log"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 202 | Accepted (async operations) |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid API key |
| 404 | Not Found - Resource not found |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

## Rate Limiting

- **Default**: 100 requests per minute
- **Burst**: Up to 20 requests
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## SDK Examples

### Python

```python
from kodezi_chronos import ChronosClient

client = ChronosClient(api_key="YOUR_API_KEY")

# Debug a stack trace
result = client.debug(
    error_input="TypeError: 'NoneType' object...",
    input_type="stack_trace",
    metadata={"repository": "my-app"}
)

if result.success:
    print(f"Fixed with {result.confidence*100:.1f}% confidence")
    for file, content in result.fix.items():
        print(f"Update {file}")
```

### JavaScript

```javascript
const ChronosClient = require('@kodezi/chronos-sdk');

const client = new ChronosClient({ apiKey: 'YOUR_API_KEY' });

// Debug test failure
const result = await client.debug({
  errorInput: {
    failures: [{ testName: 'test_login', error: 'AssertionError' }]
  },
  inputType: 'test_output'
});

if (result.success) {
  console.log(`Fixed: ${result.explanation}`);
}
```

### Go

```go
import "github.com/kodezi/chronos-go"

client := chronos.NewClient("YOUR_API_KEY")

result, err := client.Debug(chronos.DebugRequest{
    ErrorInput: "panic: runtime error...",
    InputType:  chronos.StackTrace,
})

if err == nil && result.Success {
    fmt.Printf("Fixed with %.1f%% confidence\n", result.Confidence*100)
}
```

## Webhooks

Configure webhooks to receive debugging results:

```json
{
  "webhook_url": "https://your-app.com/chronos-webhook",
  "events": ["debug.completed", "debug.failed"],
  "secret": "your_webhook_secret"
}
```

## Best Practices

1. **Provide Context**: Include as much metadata as possible
2. **Use Async for Long Operations**: Use async endpoints for complex debugging
3. **Batch Similar Issues**: Group related issues for better performance
4. **Monitor Rate Limits**: Implement exponential backoff
5. **Cache Results**: Store successful fixes for similar issues

## Support

- **Documentation**: https://docs.kodezi.com/chronos
- **Status Page**: https://status.kodezi.com
- **Support**: support@kodezi.com