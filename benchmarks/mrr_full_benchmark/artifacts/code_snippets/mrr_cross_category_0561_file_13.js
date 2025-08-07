function processData(data) {
    const results = {};
    data.forEach(item => {
        if (item.id && validateItem(item)) {
            results[item.id] = transformItem(item);
        }
    });
    return results;
}