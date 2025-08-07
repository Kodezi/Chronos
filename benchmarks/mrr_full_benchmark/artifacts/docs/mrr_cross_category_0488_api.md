# API Documentation

## API Reference

### Endpoint: /api/cross-category

**Method**: POST

**Description**: Processes cross category

**Parameters**:
- `data` (required): Input data to process
- `options` (optional): Processing options

**Returns**:
- `200 OK`: Success response
- `400 Bad Request`: Invalid input
- `500 Internal Server Error`: Processing error

**Known Issues**:
- API client not thread-safe causing data corruption
- See bug report: mrr_cross_category_0488
