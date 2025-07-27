# InventoryService.py - Contains race condition
import threading
from datetime import datetime

class InventoryService:
    def __init__(self, product_cache, db_connection):
        self.product_cache = product_cache
        self.db = db_connection
        self.pending_updates = {}
        
    def update_stock(self, product_id, quantity_change):
        """Update product stock level - UNSAFE for concurrent access"""
        # Get current stock from cache
        current_stock = self.product_cache.get_stock(product_id)
        
        if current_stock is None:
            # Load from database if not in cache
            current_stock = self.db.get_product_stock(product_id)
            self.product_cache.set_stock(product_id, current_stock)
        
        # RACE CONDITION: Multiple threads can read same value
        new_stock = current_stock + quantity_change
        
        # Validation
        if new_stock < 0:
            raise ValueError(f"Insufficient stock for product {product_id}")
        
        # RACE CONDITION: Time gap between check and update
        # Another thread might have modified stock in between
        
        # Update cache
        self.product_cache.set_stock(product_id, new_stock)
        
        # Track pending updates for batch processing
        if product_id not in self.pending_updates:
            self.pending_updates[product_id] = 0
        
        # RACE CONDITION: Dictionary not thread-safe
        self.pending_updates[product_id] += quantity_change
        
        # Persist to database
        self.db.update_product_stock(product_id, new_stock)
        
        return new_stock
    
    def process_order(self, order):
        """Process order with multiple items"""
        for item in order.items:
            try:
                # Multiple threads processing orders can corrupt inventory
                self.update_stock(item.product_id, -item.quantity)
            except ValueError as e:
                # Rollback? What if some items were already updated?
                raise OrderFailedException(f"Order failed: {e}")


# ProductCache.py - Not thread-safe
class ProductCache:
    def __init__(self):
        self.cache = {}  # Regular dict is not thread-safe
        self.last_updated = {}
        
    def get_stock(self, product_id):
        """Get stock level from cache"""
        return self.cache.get(product_id)
    
    def set_stock(self, product_id, stock_level):
        """Set stock level in cache"""
        # RACE CONDITION: Multiple operations not atomic
        self.cache[product_id] = stock_level
        self.last_updated[product_id] = datetime.now()
        
    def invalidate(self, product_id):
        """Remove product from cache"""
        # RACE CONDITION: Check and delete not atomic
        if product_id in self.cache:
            del self.cache[product_id]
            del self.last_updated[product_id]


# OrderProcessor.py - Concurrent order processing
import concurrent.futures

class OrderProcessor:
    def __init__(self, inventory_service):
        self.inventory_service = inventory_service
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        
    def process_orders_batch(self, orders):
        """Process multiple orders concurrently"""
        futures = []
        
        for order in orders:
            # Each order processed in separate thread
            # PROBLEM: No coordination between threads
            future = self.executor.submit(
                self.inventory_service.process_order, 
                order
            )
            futures.append(future)
        
        # Wait for all orders to complete
        results = []
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                # Some orders might fail due to race conditions
                print(f"Order processing failed: {e}")
                
        return results