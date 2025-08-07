def process_data(data: List[Dict]) -> Dict[str, Any]:
    """Process input data and return aggregated results."""
    results = {}
    for item in data:
        key = item.get('id')
        if key and validate_item(item):
            results[key] = transform_item(item)
    return results