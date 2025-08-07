function processData(data) {
    const results = {};
    data.forEach(item => {
        if (item.id && validateItem(item)) {
            results[item.id] = transformItem(item);
        }
    });
    return results;
}

class DataManager {
    constructor(config) {
        this.config = config;
        this.cache = new Map();
    }
    
    getData(key) {
        return this.cache.get(key);
    }
}