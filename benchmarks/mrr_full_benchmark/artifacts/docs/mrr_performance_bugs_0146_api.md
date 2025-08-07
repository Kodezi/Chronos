# API Documentation

## API Reference

### Endpoint: /api/performance-bugs

**Method**: POST

**Description**: Processes performance bugs

**Parameters**:
- `data` (required): Input data to process
- `options` (optional): Processing options

**Returns**:
- `200 OK`: Success response
- `400 Bad Request`: Invalid input
- `500 Internal Server Error`: Processing error

**Known Issues**:
- O(n²) algorithm where O(n) is possible
- See bug report: mrr_performance_bugs_0146
