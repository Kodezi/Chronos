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

import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;
import com.example.utils.DataValidator;
import com.example.core.BaseProcessor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;