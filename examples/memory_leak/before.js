// DashboardManager.js - Contains memory leak
class DashboardManager {
    constructor(eventBus, widgetFactory) {
        this.eventBus = eventBus;
        this.widgetFactory = widgetFactory;
        this.widgets = new Map();
        this.updateCallbacks = [];
        this.dataCache = {};
        
        // LEAK: Global event listeners never removed
        this.eventBus.on('data-update', this.handleDataUpdate.bind(this));
        this.eventBus.on('widget-request', this.createWidget.bind(this));
        
        // LEAK: Interval never cleared
        this.refreshInterval = setInterval(() => {
            this.refreshAllWidgets();
        }, 5000);
    }
    
    createWidget(config) {
        const widget = this.widgetFactory.create(config);
        
        // LEAK: Widget stored but never removed
        this.widgets.set(widget.id, widget);
        
        // LEAK: Callback creates closure over widget
        const updateCallback = (data) => {
            widget.update(data);
            // LEAK: Cache grows indefinitely
            this.dataCache[widget.id] = {
                data: data,
                timestamp: Date.now(),
                widget: widget  // LEAK: Circular reference
            };
        };
        
        // LEAK: Callbacks array grows indefinitely
        this.updateCallbacks.push(updateCallback);
        
        // LEAK: Event listener on widget never removed
        widget.on('refresh', () => {
            this.fetchDataForWidget(widget);
        });
        
        return widget;
    }
    
    removeWidget(widgetId) {
        // INCOMPLETE: Only removes from map, doesn't clean up
        this.widgets.delete(widgetId);
        // Missing: Remove event listeners, callbacks, cache entries
    }
    
    handleDataUpdate(data) {
        // Process all widgets
        this.widgets.forEach((widget, id) => {
            // LEAK: Creates new function on every update
            const processor = new DataProcessor(widget);
            processor.process(data);
            
            // LEAK: Processor not disposed
        });
    }
    
    refreshAllWidgets() {
        const promises = [];
        
        this.widgets.forEach((widget) => {
            // LEAK: Promise references accumulate
            const promise = this.fetchDataForWidget(widget)
                .then(data => {
                    // LEAK: Logging retains references
                    console.log('Updated widget:', widget);
                    return data;
                });
            promises.push(promise);
        });
        
        // LEAK: Promise.all retains all references
        return Promise.all(promises);
    }
    
    fetchDataForWidget(widget) {
        return fetch(widget.dataUrl)
            .then(response => response.json())
            .then(data => {
                // LEAK: Error handler closure retains widget
                window.onerror = (error) => {
                    console.error('Widget error:', widget.id, error);
                };
                
                return data;
            });
    }
}

// WidgetFactory.js - Creates widgets without cleanup
class WidgetFactory {
    constructor() {
        this.widgetCount = 0;
        this.templates = new Map();
        
        // LEAK: Static handlers accumulate
        this.handlers = [];
    }
    
    create(config) {
        const widget = new Widget(config);
        widget.id = `widget-${this.widgetCount++}`;
        
        // LEAK: DOM elements not cleaned up
        const element = document.createElement('div');
        element.className = 'widget';
        element.innerHTML = this.renderTemplate(config);
        document.body.appendChild(element);
        
        widget.element = element;
        
        // LEAK: Event listeners on DOM
        element.addEventListener('click', (e) => {
            widget.handleClick(e);
        });
        
        element.addEventListener('mouseover', (e) => {
            widget.handleHover(e);
        });
        
        // LEAK: Animation frame continues after widget removal
        const animate = () => {
            widget.animate();
            widget.animationFrame = requestAnimationFrame(animate);
        };
        animate();
        
        // LEAK: Global resize handler per widget
        window.addEventListener('resize', () => {
            widget.resize();
        });
        
        return widget;
    }
    
    renderTemplate(config) {
        // LEAK: Template cache grows indefinitely
        const key = JSON.stringify(config);
        if (!this.templates.has(key)) {
            this.templates.set(key, this.compileTemplate(config));
        }
        return this.templates.get(key);
    }
}

// EventBus.js - Global event system with memory issues
class EventBus {
    constructor() {
        this.events = {};
        this.eventHistory = [];  // LEAK: Unbounded growth
    }
    
    on(event, callback) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        
        // LEAK: Callbacks never removed
        this.events[event].push(callback);
        
        // LEAK: No weak references
        return callback;
    }
    
    emit(event, data) {
        // LEAK: History grows forever
        this.eventHistory.push({
            event: event,
            data: data,
            timestamp: Date.now(),
            callbacks: this.events[event] || []  // LEAK: Stores references
        });
        
        if (this.events[event]) {
            this.events[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    // LEAK: Error references retain data
                    console.error('Event error:', error, data);
                }
            });
        }
    }
    
    // Missing: off() method to remove listeners
}

// Widget.js - Base widget class
class Widget extends EventTarget {
    constructor(config) {
        super();
        this.config = config;
        this.data = null;
        this.subscribers = [];  // LEAK: Manual event system
        
        // LEAK: Large data structures retained
        this.renderCache = new Map();
        this.stateHistory = [];
    }
    
    update(data) {
        this.data = data;
        
        // LEAK: State history unbounded
        this.stateHistory.push({
            data: data,
            timestamp: Date.now()
        });
        
        this.render();
    }
    
    render() {
        // LEAK: Cache without eviction
        const cacheKey = JSON.stringify(this.data);
        this.renderCache.set(cacheKey, this.generateDOM());
    }
}