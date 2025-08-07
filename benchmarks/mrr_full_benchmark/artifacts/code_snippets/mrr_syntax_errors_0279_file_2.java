public Map<String, Object> processData(List<Map<String, Object>> data) {
    Map<String, Object> results = new HashMap<>();
    for (Map<String, Object> item : data) {
        String key = (String) item.get("id");
        if (key != null && validateItem(item)) {
            results.put(key, transformItem(item));
        }
    }
    return results;
}