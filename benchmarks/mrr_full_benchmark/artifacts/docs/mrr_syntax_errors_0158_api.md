# API Documentation

## API Reference

### Endpoint: /api/syntax-errors

**Method**: POST

**Description**: Processes syntax errors

**Parameters**:
- `data` (required): Input data to process
- `options` (optional): Processing options

**Returns**:
- `200 OK`: Success response
- `400 Bad Request`: Invalid input
- `500 Internal Server Error`: Processing error

**Known Issues**:
- Missing closing bracket causing SyntaxError: unexpected EOF while parsing
- See bug report: mrr_syntax_errors_0158
