# InventoryService.py - Fixed by Chronos with proper synchronization
import threading
from datetime import datetime
from contextlib import contextmanager
import logging

class InventoryService:
    def __init__(self, product_cache, db_connection):
        self.product_cache = product_cache
        self.db = db_connection
        self.pending_updates = {}
        # Added: Thread-safe synchronization
        self._locks = {}  # Product-level locks
        self._locks_lock = threading.RLock()  # Lock for managing locks
        self._pending_lock = threading.Lock()  # Lock for pending updates
        self.logger = logging.getLogger(__name__)
        
    @contextmanager
    def _get_product_lock(self, product_id):
        """Get or create a lock for a specific product"""
        with self._locks_lock:
            if product_id not in self._locks:
                self._locks[product_id] = threading.RLock()
            lock = self._locks[product_id]
        
        lock.acquire()
        try:
            yield
        finally:
            lock.release()
    
    def update_stock(self, product_id, quantity_change):
        """Update product stock level - THREAD-SAFE"""
        # Use product-specific lock to allow concurrent updates to different products
        with self._get_product_lock(product_id):
            # All operations on this product are now atomic
            
            # Get current stock from cache
            current_stock = self.product_cache.get_stock(product_id)
            
            if current_stock is None:
                # Load from database if not in cache
                current_stock = self.db.get_product_stock(product_id)
                self.product_cache.set_stock(product_id, current_stock)
            
            # Calculate new stock
            new_stock = current_stock + quantity_change
            
            # Validation
            if new_stock < 0:
                self.logger.warning(
                    f"Insufficient stock for product {product_id}: "
                    f"current={current_stock}, change={quantity_change}"
                )
                raise ValueError(f"Insufficient stock for product {product_id}")
            
            # Update cache atomically
            self.product_cache.set_stock(product_id, new_stock)
            
            # Track pending updates with separate lock
            with self._pending_lock:
                if product_id not in self.pending_updates:
                    self.pending_updates[product_id] = 0
                self.pending_updates[product_id] += quantity_change
            
            # Persist to database (still within product lock)
            try:
                self.db.update_product_stock(product_id, new_stock)
            except Exception as e:
                # Rollback cache on DB failure
                self.product_cache.set_stock(product_id, current_stock)
                with self._pending_lock:
                    self.pending_updates[product_id] -= quantity_change
                raise
            
            self.logger.debug(
                f"Stock updated: product={product_id}, "
                f"old={current_stock}, new={new_stock}"
            )
            
            return new_stock
    
    def process_order(self, order):
        """Process order with multiple items - with rollback support"""
        completed_updates = []
        
        try:
            # Sort items by product_id to prevent deadlocks
            sorted_items = sorted(order.items, key=lambda x: x.product_id)
            
            for item in sorted_items:
                self.update_stock(item.product_id, -item.quantity)
                completed_updates.append((item.product_id, item.quantity))
                
        except ValueError as e:
            # Rollback completed updates
            self.logger.error(f"Order failed, rolling back: {e}")
            for product_id, quantity in completed_updates:
                try:
                    self.update_stock(product_id, quantity)  # Restore stock
                except Exception as rollback_error:
                    self.logger.critical(
                        f"Rollback failed for product {product_id}: {rollback_error}"
                    )
            raise OrderFailedException(f"Order failed: {e}")
        
        return len(completed_updates)


# ProductCache.py - Thread-safe implementation
import threading
from collections import OrderedDict

class ProductCache:
    def __init__(self, max_size=1000):
        self._lock = threading.RLock()
        self._cache = OrderedDict()  # For LRU eviction
        self._last_updated = {}
        self._max_size = max_size
        
    def get_stock(self, product_id):
        """Get stock level from cache - thread-safe"""
        with self._lock:
            if product_id in self._cache:
                # Move to end for LRU
                self._cache.move_to_end(product_id)
                return self._cache[product_id]
            return None
    
    def set_stock(self, product_id, stock_level):
        """Set stock level in cache - thread-safe"""
        with self._lock:
            # Add or update
            self._cache[product_id] = stock_level
            self._cache.move_to_end(product_id)
            self._last_updated[product_id] = datetime.now()
            
            # Evict oldest if over capacity
            if len(self._cache) > self._max_size:
                oldest = next(iter(self._cache))
                del self._cache[oldest]
                del self._last_updated[oldest]
    
    def invalidate(self, product_id):
        """Remove product from cache - thread-safe"""
        with self._lock:
            self._cache.pop(product_id, None)
            self._last_updated.pop(product_id, None)
    
    def get_all_stocks(self):
        """Get snapshot of all cached stocks"""
        with self._lock:
            return dict(self._cache)


# OrderProcessor.py - Improved concurrent processing
import concurrent.futures
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class OrderResult:
    order_id: str
    success: bool
    error: str = None
    items_processed: int = 0

class OrderProcessor:
    def __init__(self, inventory_service, max_workers=10):
        self.inventory_service = inventory_service
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers
        )
        self.logger = logging.getLogger(__name__)
        
    def process_orders_batch(self, orders) -> List[OrderResult]:
        """Process multiple orders concurrently with proper error handling"""
        futures = {}
        
        # Submit all orders for processing
        for order in orders:
            future = self.executor.submit(self._process_single_order, order)
            futures[future] = order
        
        # Collect results
        results = []
        for future in concurrent.futures.as_completed(futures):
            order = futures[future]
            try:
                items_processed = future.result()
                results.append(OrderResult(
                    order_id=order.id,
                    success=True,
                    items_processed=items_processed
                ))
            except Exception as e:
                self.logger.error(f"Order {order.id} failed: {e}")
                results.append(OrderResult(
                    order_id=order.id,
                    success=False,
                    error=str(e)
                ))
        
        return results
    
    def _process_single_order(self, order):
        """Process a single order with monitoring"""
        start_time = datetime.now()
        try:
            result = self.inventory_service.process_order(order)
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.info(
                f"Order {order.id} processed in {duration:.2f}s"
            )
            return result
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.error(
                f"Order {order.id} failed after {duration:.2f}s: {e}"
            )
            raise
    
    def shutdown(self):
        """Gracefully shutdown the executor"""
        self.executor.shutdown(wait=True)


# Additional utilities for monitoring
class ConcurrencyMonitor:
    """Monitor for detecting potential race conditions"""
    
    def __init__(self):
        self._active_products = {}
        self._lock = threading.Lock()
        
    def track_access(self, product_id, thread_id):
        """Track concurrent access to products"""
        with self._lock:
            if product_id not in self._active_products:
                self._active_products[product_id] = set()
            
            active_threads = self._active_products[product_id]
            if len(active_threads) > 0 and thread_id not in active_threads:
                # Potential race condition detected
                logging.warning(
                    f"Concurrent access to product {product_id} by threads: "
                    f"{active_threads} and {thread_id}"
                )
            
            active_threads.add(thread_id)
    
    def release_access(self, product_id, thread_id):
        """Release tracking for a product"""
        with self._lock:
            if product_id in self._active_products:
                self._active_products[product_id].discard(thread_id)
                if not self._active_products[product_id]:
                    del self._active_products[product_id]