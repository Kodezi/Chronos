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

public class DataManager {
    private final Config config;
    private final Map<String, Object> cache;
    
    public DataManager(Config config) {
        this.config = config;
        this.cache = new HashMap<>();
    }
    
    public Object getData(String key) {
        return cache.get(key);
    }
}