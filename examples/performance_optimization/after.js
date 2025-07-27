// AnalyticsProcessor.js - Optimized by Chronos for performance
class AnalyticsProcessor {
    constructor(database, dataAggregator) {
        this.db = database;
        this.aggregator = dataAggregator;
        this.cache = new Map(); // Added caching
        this.batchSize = 1000; // Process in batches
    }
    
    async processUserActivity(startDate, endDate) {
        console.time('Total Processing');
        
        // OPTIMIZATION 1: Efficient single query with JOIN
        const userActivitiesQuery = `
            SELECT 
                u.id as user_id,
                u.name as user_name,
                a.id as activity_id,
                a.type,
                a.timestamp,
                ad.data as details
            FROM users u
            INNER JOIN activities a ON u.id = a.user_id
            LEFT JOIN activity_details ad ON a.id = ad.activity_id
            WHERE a.timestamp >= ? AND a.timestamp <= ?
            ORDER BY u.id, a.timestamp
        `;
        
        const results = await this.db.query(userActivitiesQuery, [startDate, endDate]);
        
        console.log(`Processing ${results.length} activity records`);
        
        // OPTIMIZATION 2: Group by user efficiently with Map
        const userActivitiesMap = new Map();
        for (const row of results) {
            if (!userActivitiesMap.has(row.user_id)) {
                userActivitiesMap.set(row.user_id, {
                    user: { id: row.user_id, name: row.user_name },
                    activities: []
                });
            }
            
            userActivitiesMap.get(row.user_id).activities.push({
                id: row.activity_id,
                type: row.type,
                timestamp: row.timestamp,
                details: row.details
            });
        }
        
        // OPTIMIZATION 3: Parallel processing with batching
        const userGroups = Array.from(userActivitiesMap.values());
        const processedMetrics = await this.processBatches(userGroups);
        
        // OPTIMIZATION 4: Efficient aggregation
        const aggregated = await this.aggregator.aggregate(processedMetrics);
        
        console.timeEnd('Total Processing');
        return aggregated;
    }
    
    async processBatches(userGroups) {
        const results = [];
        
        // Process users in parallel batches
        for (let i = 0; i < userGroups.length; i += this.batchSize) {
            const batch = userGroups.slice(i, i + this.batchSize);
            const batchPromises = batch.map(({ user, activities }) => 
                this.calculateUserMetrics(user, activities)
            );
            
            const batchResults = await Promise.all(batchPromises);
            results.push(...batchResults);
        }
        
        return results;
    }
    
    async calculateUserMetrics(user, activities) {
        // Check cache first
        const cacheKey = `${user.id}-${activities.length}`;
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey);
        }
        
        // OPTIMIZATION 5: Pre-allocate data structures
        const metrics = {
            userId: user.id,
            totalActivities: activities.length,
            uniqueDays: new Set(),
            activityByType: Object.create(null), // Faster than {}
            hourlyDistribution: new Uint32Array(24), // Typed array
            weekendActivities: 0
        };
        
        // OPTIMIZATION 6: Single pass through activities
        for (const activity of activities) {
            // Use timestamp directly (already parsed from DB)
            const date = new Date(activity.timestamp);
            
            // OPTIMIZATION 7: Efficient date key
            const dateKey = (date.getFullYear() * 10000) + 
                          ((date.getMonth() + 1) * 100) + 
                          date.getDate();
            metrics.uniqueDays.add(dateKey);
            
            // Count by type
            metrics.activityByType[activity.type] = 
                (metrics.activityByType[activity.type] || 0) + 1;
            
            // Hour distribution
            metrics.hourlyDistribution[date.getHours()]++;
            
            // Weekend check
            const day = date.getDay();
            if (day === 0 || day === 6) {
                metrics.weekendActivities++;
            }
        }
        
        // Convert Set size
        metrics.uniqueDaysCount = metrics.uniqueDays.size;
        metrics.averagePerDay = activities.length / metrics.uniqueDaysCount;
        
        // Clean up Set to reduce memory
        metrics.uniqueDays = null;
        
        // Cache the result
        this.cache.set(cacheKey, metrics);
        
        return metrics;
    }
}

// DataAggregator.js - Optimized aggregation logic
class DataAggregator {
    async aggregate(userMetrics) {
        console.time('Aggregation');
        
        // OPTIMIZATION 8: Single pass aggregation
        const aggregated = {
            totalUsers: userMetrics.length,
            totalActivities: 0,
            activityTypes: Object.create(null),
            hourlyTrends: new Uint32Array(24),
            topUsers: [],
            activityCounts: new Float64Array(userMetrics.length)
        };
        
        // OPTIMIZATION 9: Combined aggregation in one pass
        userMetrics.forEach((metrics, index) => {
            // Total activities
            aggregated.totalActivities += metrics.totalActivities;
            aggregated.activityCounts[index] = metrics.totalActivities;
            
            // Activity types
            for (const [type, count] of Object.entries(metrics.activityByType)) {
                aggregated.activityTypes[type] = 
                    (aggregated.activityTypes[type] || 0) + count;
            }
            
            // Hourly trends (using typed array addition)
            for (let hour = 0; hour < 24; hour++) {
                aggregated.hourlyTrends[hour] += metrics.hourlyDistribution[hour];
            }
        });
        
        // OPTIMIZATION 10: Efficient top users using heap
        aggregated.topUsers = this.findTopUsers(userMetrics, 10);
        
        // OPTIMIZATION 11: Efficient percentile calculation
        aggregated.percentiles = this.calculatePercentiles(
            aggregated.activityCounts,
            [50, 90, 99]
        );
        
        console.timeEnd('Aggregation');
        return aggregated;
    }
    
    findTopUsers(userMetrics, k) {
        // Use partial sort for O(n log k) instead of O(n log n)
        const minHeap = new MinHeap(k);
        
        for (const metrics of userMetrics) {
            minHeap.add({
                userId: metrics.userId,
                activities: metrics.totalActivities
            });
        }
        
        return minHeap.toArray().reverse();
    }
    
    calculatePercentiles(values, percentiles) {
        // OPTIMIZATION 12: Partial sort for percentiles
        const n = values.length;
        const result = {};
        
        // Sort only once
        const sorted = Float64Array.from(values).sort();
        
        for (const p of percentiles) {
            const index = Math.ceil((p / 100) * n) - 1;
            result[`p${p}`] = sorted[index];
        }
        
        return result;
    }
}

// MinHeap implementation for efficient top-k
class MinHeap {
    constructor(maxSize) {
        this.heap = [];
        this.maxSize = maxSize;
    }
    
    add(item) {
        if (this.heap.length < this.maxSize) {
            this.heap.push(item);
            this.bubbleUp(this.heap.length - 1);
        } else if (item.activities > this.heap[0].activities) {
            this.heap[0] = item;
            this.bubbleDown(0);
        }
    }
    
    bubbleUp(index) {
        while (index > 0) {
            const parentIndex = Math.floor((index - 1) / 2);
            if (this.heap[index].activities >= this.heap[parentIndex].activities) break;
            [this.heap[index], this.heap[parentIndex]] = 
                [this.heap[parentIndex], this.heap[index]];
            index = parentIndex;
        }
    }
    
    bubbleDown(index) {
        while (true) {
            let minIndex = index;
            const leftIndex = 2 * index + 1;
            const rightIndex = 2 * index + 2;
            
            if (leftIndex < this.heap.length && 
                this.heap[leftIndex].activities < this.heap[minIndex].activities) {
                minIndex = leftIndex;
            }
            
            if (rightIndex < this.heap.length && 
                this.heap[rightIndex].activities < this.heap[minIndex].activities) {
                minIndex = rightIndex;
            }
            
            if (minIndex === index) break;
            
            [this.heap[index], this.heap[minIndex]] = 
                [this.heap[minIndex], this.heap[index]];
            index = minIndex;
        }
    }
    
    toArray() {
        return [...this.heap].sort((a, b) => a.activities - b.activities);
    }
}

// DatabaseQueries.js - Optimized database access
class DatabaseQueries {
    constructor(connection) {
        this.conn = connection;
        this.preparedStatements = new Map();
    }
    
    async initialize() {
        // OPTIMIZATION 13: Create indexes
        await this.conn.query(`
            CREATE INDEX IF NOT EXISTS idx_activities_user_timestamp 
            ON activities(user_id, timestamp)
        `);
        
        await this.conn.query(`
            CREATE INDEX IF NOT EXISTS idx_activity_tags_activity 
            ON activity_tags(activity_id)
        `);
        
        // OPTIMIZATION 14: Prepare statements
        this.preparedStatements.set('userActivityReport', 
            await this.conn.prepare(`
                WITH activity_summary AS (
                    SELECT 
                        a.id,
                        a.user_id,
                        a.type,
                        a.timestamp,
                        a.category_id,
                        c.name as category_name,
                        GROUP_CONCAT(at.tag_name) as tags,
                        DATE(a.timestamp) as activity_date
                    FROM activities a
                    LEFT JOIN categories c ON a.category_id = c.id
                    LEFT JOIN activity_tags at ON a.id = at.activity_id
                    WHERE a.user_id = ? 
                        AND a.timestamp BETWEEN ? AND ?
                    GROUP BY a.id
                )
                SELECT 
                    *,
                    COUNT(*) OVER (PARTITION BY category_name) as category_count,
                    COUNT(*) OVER (PARTITION BY activity_date) as daily_count
                FROM activity_summary
                ORDER BY timestamp DESC
            `)
        );
    }
    
    async getUserActivityReport(userId, startDate, endDate) {
        // OPTIMIZATION 15: Single query with window functions
        const stmt = this.preparedStatements.get('userActivityReport');
        const activities = await stmt.execute([userId, startDate, endDate]);
        
        if (activities.length === 0) {
            return { activities: [], summary: {} };
        }
        
        // OPTIMIZATION 16: Build report efficiently
        const report = {
            activities: [],
            summary: {
                total: activities.length,
                byCategory: Object.create(null),
                byDay: Object.create(null)
            }
        };
        
        // Process results in single pass
        const categoryMap = new Map();
        const dayMap = new Map();
        
        for (const activity of activities) {
            // Format activity
            report.activities.push({
                id: activity.id,
                type: activity.type,
                timestamp: activity.timestamp,
                category: activity.category_name,
                tags: activity.tags ? activity.tags.split(',') : []
            });
            
            // Use pre-calculated counts
            categoryMap.set(activity.category_name, activity.category_count);
            dayMap.set(activity.activity_date, activity.daily_count);
        }
        
        // Convert maps to objects
        report.summary.byCategory = Object.fromEntries(categoryMap);
        report.summary.byDay = Object.fromEntries(dayMap);
        
        return report;
    }
    
    async close() {
        // Clean up prepared statements
        for (const stmt of this.preparedStatements.values()) {
            await stmt.close();
        }
    }
}