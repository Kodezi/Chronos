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

// Configuration constants
private static final int MAX_RETRIES = 3;
private static final int TIMEOUT_SECONDS = 30;
private static final int DEFAULT_BATCH_SIZE = 100;

// Runtime variables
private ConnectionPool connectionPool = new ConnectionPool(10);
private Map<String, Session> activeSessions = new ConcurrentHashMap<>();