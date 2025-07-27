// DashboardManager.js - Fixed by Chronos with proper cleanup
class DashboardManager {
    constructor(eventBus, widgetFactory) {
        this.eventBus = eventBus;
        this.widgetFactory = widgetFactory;
        this.widgets = new Map();
        this.updateCallbacks = new Map(); // Changed to Map for easier cleanup
        this.dataCache = new Map(); // Use Map with size limit
        this.maxCacheSize = 100;
        
        // Store references for cleanup
        this.eventListeners = [];
        this.boundHandlers = {
            dataUpdate: this.handleDataUpdate.bind(this),
            widgetRequest: this.createWidget.bind(this)
        };
        
        // Register listeners with cleanup tracking
        this.eventListeners.push(
            this.eventBus.on('data-update', this.boundHandlers.dataUpdate),
            this.eventBus.on('widget-request', this.boundHandlers.widgetRequest)
        );
        
        // Store interval for cleanup
        this.refreshInterval = setInterval(() => {
            this.refreshAllWidgets();
        }, 5000);
        
        // Auto-cleanup on page unload
        window.addEventListener('beforeunload', () => this.destroy());
    }
    
    createWidget(config) {
        const widget = this.widgetFactory.create(config);
        
        // Store widget with cleanup info
        const widgetInfo = {
            widget: widget,
            listeners: [],
            updateCallback: null
        };
        
        // Create update callback with weak reference
        const updateCallback = (data) => {
            // Check if widget still exists
            if (!this.widgets.has(widget.id)) {
                return;
            }
            
            widget.update(data);
            
            // Cache with size limit and no circular reference
            this.setCache(widget.id, {
                data: data,
                timestamp: Date.now()
                // Removed widget reference
            });
        };
        
        widgetInfo.updateCallback = updateCallback;
        this.updateCallbacks.set(widget.id, updateCallback);
        
        // Store listener reference for cleanup
        const refreshListener = () => {
            this.fetchDataForWidget(widget);
        };
        widget.on('refresh', refreshListener);
        widgetInfo.listeners.push({ event: 'refresh', handler: refreshListener });
        
        this.widgets.set(widget.id, widgetInfo);
        
        return widget;
    }
    
    removeWidget(widgetId) {
        const widgetInfo = this.widgets.get(widgetId);
        if (!widgetInfo) return;
        
        // Clean up event listeners
        widgetInfo.listeners.forEach(({ event, handler }) => {
            widgetInfo.widget.off(event, handler);
        });
        
        // Remove update callback
        this.updateCallbacks.delete(widgetId);
        
        // Clear cache entries
        this.dataCache.delete(widgetId);
        
        // Destroy widget (triggers DOM cleanup)
        this.widgetFactory.destroy(widgetInfo.widget);
        
        // Remove from widgets map
        this.widgets.delete(widgetId);
    }
    
    handleDataUpdate(data) {
        // Use weak references for processors
        const processors = new WeakMap();
        
        this.widgets.forEach((widgetInfo, id) => {
            const processor = new DataProcessor(widgetInfo.widget);
            processors.set(widgetInfo.widget, processor);
            
            processor.process(data);
            
            // Explicit cleanup
            processor.destroy();
        });
        
        // Processors eligible for GC after scope
    }
    
    refreshAllWidgets() {
        const activeWidgets = Array.from(this.widgets.values())
            .filter(info => info.widget.isActive);
        
        // Limit concurrent operations
        const batchSize = 10;
        const batches = [];
        
        for (let i = 0; i < activeWidgets.length; i += batchSize) {
            batches.push(activeWidgets.slice(i, i + batchSize));
        }
        
        // Process in batches to avoid memory spike
        return batches.reduce((promise, batch) => {
            return promise.then(() => {
                const batchPromises = batch.map(widgetInfo =>
                    this.fetchDataForWidget(widgetInfo.widget)
                        .catch(error => {
                            console.error(`Widget ${widgetInfo.widget.id} update failed:`, error);
                            return null; // Don't retain error references
                        })
                );
                return Promise.all(batchPromises);
            });
        }, Promise.resolve());
    }
    
    fetchDataForWidget(widget) {
        // Abort previous request if pending
        if (widget.abortController) {
            widget.abortController.abort();
        }
        
        widget.abortController = new AbortController();
        
        return fetch(widget.dataUrl, {
            signal: widget.abortController.signal
        })
        .then(response => response.json())
        .then(data => {
            widget.abortController = null;
            return data;
        })
        .catch(error => {
            widget.abortController = null;
            if (error.name === 'AbortError') {
                return null; // Ignore abort errors
            }
            throw error;
        });
    }
    
    setCache(key, value) {
        // Implement LRU cache with size limit
        this.dataCache.set(key, value);
        
        // Evict oldest entries if over limit
        if (this.dataCache.size > this.maxCacheSize) {
            const firstKey = this.dataCache.keys().next().value;
            this.dataCache.delete(firstKey);
        }
    }
    
    destroy() {
        // Clear interval
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
        
        // Remove all widgets
        const widgetIds = Array.from(this.widgets.keys());
        widgetIds.forEach(id => this.removeWidget(id));
        
        // Remove event listeners
        this.eventListeners.forEach(removeListener => {
            if (typeof removeListener === 'function') {
                removeListener();
            }
        });
        
        // Clear references
        this.widgets.clear();
        this.updateCallbacks.clear();
        this.dataCache.clear();
        this.eventListeners = [];
    }
}

// WidgetFactory.js - Fixed with proper cleanup
class WidgetFactory {
    constructor() {
        this.widgetCount = 0;
        this.templates = new LRUCache(50); // Limited cache
        this.activeWidgets = new WeakMap(); // Weak references
    }
    
    create(config) {
        const widget = new Widget(config);
        widget.id = `widget-${this.widgetCount++}`;
        
        // Create DOM element
        const element = document.createElement('div');
        element.className = 'widget';
        element.dataset.widgetId = widget.id;
        element.innerHTML = this.renderTemplate(config);
        document.body.appendChild(element);
        
        widget.element = element;
        
        // Store cleanup functions
        const cleanup = {
            listeners: [],
            animationFrame: null,
            resizeHandler: null
        };
        
        // Add event listeners with cleanup
        const clickHandler = (e) => widget.handleClick(e);
        const hoverHandler = (e) => widget.handleHover(e);
        
        element.addEventListener('click', clickHandler);
        element.addEventListener('mouseover', hoverHandler);
        
        cleanup.listeners.push(
            () => element.removeEventListener('click', clickHandler),
            () => element.removeEventListener('mouseover', hoverHandler)
        );
        
        // Animation with cleanup
        let animationActive = true;
        const animate = () => {
            if (animationActive && widget.isActive) {
                widget.animate();
                cleanup.animationFrame = requestAnimationFrame(animate);
            }
        };
        animate();
        
        // Debounced resize handler
        const resizeHandler = this.debounce(() => {
            if (widget.isActive) {
                widget.resize();
            }
        }, 250);
        
        window.addEventListener('resize', resizeHandler);
        cleanup.resizeHandler = () => window.removeEventListener('resize', resizeHandler);
        
        // Store cleanup info
        this.activeWidgets.set(widget, cleanup);
        
        return widget;
    }
    
    destroy(widget) {
        const cleanup = this.activeWidgets.get(widget);
        if (!cleanup) return;
        
        // Stop animation
        if (cleanup.animationFrame) {
            cancelAnimationFrame(cleanup.animationFrame);
        }
        
        // Remove event listeners
        cleanup.listeners.forEach(remove => remove());
        
        // Remove resize handler
        if (cleanup.resizeHandler) {
            cleanup.resizeHandler();
        }
        
        // Remove DOM element
        if (widget.element && widget.element.parentNode) {
            widget.element.parentNode.removeChild(widget.element);
        }
        
        // Clear widget references
        widget.destroy();
        
        // Remove from tracking
        this.activeWidgets.delete(widget);
    }
    
    renderTemplate(config) {
        const key = JSON.stringify(config);
        let template = this.templates.get(key);
        
        if (!template) {
            template = this.compileTemplate(config);
            this.templates.set(key, template);
        }
        
        return template;
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// EventBus.js - Fixed with proper cleanup and limits
class EventBus {
    constructor() {
        this.events = new Map();
        this.maxHistorySize = 100;
        this.eventHistory = []; // Still exists but limited
    }
    
    on(event, callback) {
        if (!this.events.has(event)) {
            this.events.set(event, new Set());
        }
        
        this.events.get(event).add(callback);
        
        // Return unsubscribe function
        return () => this.off(event, callback);
    }
    
    off(event, callback) {
        const callbacks = this.events.get(event);
        if (callbacks) {
            callbacks.delete(callback);
            if (callbacks.size === 0) {
                this.events.delete(event);
            }
        }
    }
    
    emit(event, data) {
        // Limited history with just metadata
        this.addToHistory({
            event: event,
            timestamp: Date.now(),
            listenerCount: this.events.get(event)?.size || 0
            // Removed data and callback references
        });
        
        const callbacks = this.events.get(event);
        if (callbacks) {
            callbacks.forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Event ${event} handler error:`, error.message);
                    // Don't retain error object or data
                }
            });
        }
    }
    
    addToHistory(entry) {
        this.eventHistory.push(entry);
        
        // Maintain size limit
        if (this.eventHistory.length > this.maxHistorySize) {
            this.eventHistory.shift();
        }
    }
    
    clear() {
        this.events.clear();
        this.eventHistory = [];
    }
}

// Widget.js - Fixed base widget class
class Widget extends EventTarget {
    constructor(config) {
        super();
        this.config = config;
        this.data = null;
        this.isActive = true;
        
        // Limited caches
        this.renderCache = new LRUCache(10);
        this.maxStateHistory = 20;
        this.stateHistory = [];
    }
    
    update(data) {
        this.data = data;
        
        // Limited state history
        this.stateHistory.push({
            timestamp: Date.now()
            // Store only necessary metadata, not full data
        });
        
        // Maintain size limit
        if (this.stateHistory.length > this.maxStateHistory) {
            this.stateHistory.shift();
        }
        
        this.render();
    }
    
    render() {
        if (!this.isActive) return;
        
        const cacheKey = this.getCacheKey(this.data);
        let dom = this.renderCache.get(cacheKey);
        
        if (!dom) {
            dom = this.generateDOM();
            this.renderCache.set(cacheKey, dom);
        }
        
        if (this.element) {
            this.element.innerHTML = dom;
        }
    }
    
    getCacheKey(data) {
        // Generate efficient cache key
        return data ? `${data.id}-${data.version}` : 'empty';
    }
    
    destroy() {
        this.isActive = false;
        this.data = null;
        this.renderCache.clear();
        this.stateHistory = [];
        this.config = null;
    }
}

// LRU Cache implementation
class LRUCache {
    constructor(maxSize) {
        this.maxSize = maxSize;
        this.cache = new Map();
    }
    
    get(key) {
        if (!this.cache.has(key)) return undefined;
        
        // Move to end (most recently used)
        const value = this.cache.get(key);
        this.cache.delete(key);
        this.cache.set(key, value);
        return value;
    }
    
    set(key, value) {
        // Remove if exists
        if (this.cache.has(key)) {
            this.cache.delete(key);
        }
        
        // Add to end
        this.cache.set(key, value);
        
        // Evict oldest if over capacity
        if (this.cache.size > this.maxSize) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
    }
    
    clear() {
        this.cache.clear();
    }
}