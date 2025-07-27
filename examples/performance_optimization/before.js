// AnalyticsProcessor.js - Contains performance bottlenecks
class AnalyticsProcessor {
    constructor(database, dataAggregator) {
        this.db = database;
        this.aggregator = dataAggregator;
        this.processedData = [];
    }
    
    async processUserActivity(startDate, endDate) {
        console.time('Total Processing');
        
        // BOTTLENECK 1: Loading all data into memory
        const allUsers = await this.db.query(
            'SELECT * FROM users'
        );
        
        const allActivities = await this.db.query(
            'SELECT * FROM activities WHERE timestamp >= ? AND timestamp <= ?',
            [startDate, endDate]
        );
        
        console.log(`Processing ${allUsers.length} users and ${allActivities.length} activities`);
        
        // BOTTLENECK 2: O(n²) nested loops
        const results = [];
        for (const user of allUsers) {
            const userActivities = [];
            
            // Inner loop through all activities for each user
            for (const activity of allActivities) {
                if (activity.user_id === user.id) {
                    userActivities.push(activity);
                }
            }
            
            // BOTTLENECK 3: Synchronous processing per user
            if (userActivities.length > 0) {
                const metrics = await this.calculateUserMetrics(user, userActivities);
                results.push(metrics);
            }
        }
        
        // BOTTLENECK 4: Inefficient aggregation
        const aggregated = await this.aggregator.aggregate(results);
        
        console.timeEnd('Total Processing');
        return aggregated;
    }
    
    async calculateUserMetrics(user, activities) {
        const metrics = {
            userId: user.id,
            totalActivities: activities.length,
            uniqueDays: new Set(),
            activityByType: {},
            hourlyDistribution: new Array(24).fill(0)
        };
        
        // BOTTLENECK 5: Individual queries in a loop
        for (const activity of activities) {
            // Fetch additional data for each activity
            const details = await this.db.query(
                'SELECT * FROM activity_details WHERE activity_id = ?',
                [activity.id]
            );
            
            // BOTTLENECK 6: String parsing for dates
            const date = new Date(activity.timestamp);
            const dateStr = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
            metrics.uniqueDays.add(dateStr);
            
            // BOTTLENECK 7: Inefficient object updates
            if (!metrics.activityByType[activity.type]) {
                metrics.activityByType[activity.type] = 0;
            }
            metrics.activityByType[activity.type]++;
            
            // Hour calculation
            const hour = date.getHours();
            metrics.hourlyDistribution[hour]++;
            
            // BOTTLENECK 8: Redundant calculations
            const dayOfWeek = date.getDay();
            const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
            if (isWeekend) {
                if (!metrics.weekendActivities) {
                    metrics.weekendActivities = 0;
                }
                metrics.weekendActivities++;
            }
        }
        
        metrics.uniqueDays = metrics.uniqueDays.size;
        metrics.averagePerDay = activities.length / metrics.uniqueDays;
        
        return metrics;
    }
}

// DataAggregator.js - Inefficient aggregation logic
class DataAggregator {
    async aggregate(userMetrics) {
        console.time('Aggregation');
        
        const aggregated = {
            totalUsers: userMetrics.length,
            totalActivities: 0,
            activityTypes: {},
            hourlyTrends: new Array(24).fill(0),
            topUsers: []
        };
        
        // BOTTLENECK 9: Multiple passes through data
        // First pass: count activities
        for (const metrics of userMetrics) {
            aggregated.totalActivities += metrics.totalActivities;
        }
        
        // Second pass: aggregate by type
        for (const metrics of userMetrics) {
            for (const [type, count] of Object.entries(metrics.activityByType)) {
                if (!aggregated.activityTypes[type]) {
                    aggregated.activityTypes[type] = 0;
                }
                aggregated.activityTypes[type] += count;
            }
        }
        
        // Third pass: hourly distribution
        for (const metrics of userMetrics) {
            for (let hour = 0; hour < 24; hour++) {
                aggregated.hourlyTrends[hour] += metrics.hourlyDistribution[hour];
            }
        }
        
        // BOTTLENECK 10: Inefficient sorting for top users
        const sortedUsers = userMetrics.slice();
        for (let i = 0; i < sortedUsers.length; i++) {
            for (let j = i + 1; j < sortedUsers.length; j++) {
                if (sortedUsers[j].totalActivities > sortedUsers[i].totalActivities) {
                    const temp = sortedUsers[i];
                    sortedUsers[i] = sortedUsers[j];
                    sortedUsers[j] = temp;
                }
            }
        }
        
        aggregated.topUsers = sortedUsers.slice(0, 10).map(m => ({
            userId: m.userId,
            activities: m.totalActivities
        }));
        
        // BOTTLENECK 11: Calculate percentiles inefficiently
        const activityCounts = userMetrics.map(m => m.totalActivities);
        aggregated.percentiles = {
            p50: this.calculatePercentile(activityCounts, 50),
            p90: this.calculatePercentile(activityCounts, 90),
            p99: this.calculatePercentile(activityCounts, 99)
        };
        
        console.timeEnd('Aggregation');
        return aggregated;
    }
    
    calculatePercentile(values, percentile) {
        // BOTTLENECK 12: Sorting entire array for each percentile
        const sorted = values.slice().sort((a, b) => a - b);
        const index = Math.ceil((percentile / 100) * sorted.length) - 1;
        return sorted[index];
    }
}

// DatabaseQueries.js - Unoptimized database access
class DatabaseQueries {
    constructor(connection) {
        this.conn = connection;
    }
    
    async getUserActivityReport(userId, startDate, endDate) {
        // BOTTLENECK 13: No index on user_id + timestamp
        const activities = await this.conn.query(
            'SELECT * FROM activities WHERE user_id = ? AND timestamp BETWEEN ? AND ?',
            [userId, startDate, endDate]
        );
        
        const report = {
            activities: [],
            summary: {}
        };
        
        // BOTTLENECK 14: N+1 query problem
        for (const activity of activities) {
            // Fetch related data for each activity
            const category = await this.conn.query(
                'SELECT name FROM categories WHERE id = ?',
                [activity.category_id]
            );
            
            const tags = await this.conn.query(
                'SELECT tag_name FROM activity_tags WHERE activity_id = ?',
                [activity.id]
            );
            
            report.activities.push({
                ...activity,
                category: category[0]?.name,
                tags: tags.map(t => t.tag_name)
            });
        }
        
        // BOTTLENECK 15: Complex aggregation in application instead of database
        report.summary = {
            total: activities.length,
            byCategory: {},
            byDay: {}
        };
        
        for (const activity of report.activities) {
            // Count by category
            if (!report.summary.byCategory[activity.category]) {
                report.summary.byCategory[activity.category] = 0;
            }
            report.summary.byCategory[activity.category]++;
            
            // Count by day
            const day = new Date(activity.timestamp).toDateString();
            if (!report.summary.byDay[day]) {
                report.summary.byDay[day] = 0;
            }
            report.summary.byDay[day]++;
        }
        
        return report;
    }
}