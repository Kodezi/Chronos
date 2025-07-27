# PaymentService.py - Migrated to payment-lib v3 API by Chronos
from payment_lib.v3 import PaymentClient, TransactionBuilder, CardValidatorAsync
from payment_lib.v3.errors import PaymentException, ValidationException
from payment_lib.v3.models import PaymentContext, RefundRequest
from payment_lib.v3.retry import RetryPolicy, ExponentialBackoff
import asyncio
from typing import Optional, Dict, Any

class PaymentService:
    def __init__(self, config):
        # NEW: Client-based initialization with context
        self.client = PaymentClient.create(
            context=PaymentContext(
                merchant_id=config['merchant_id'],
                api_credentials=config['api_key'],
                environment=config['environment'],
                # NEW: Structured retry policy
                retry_policy=RetryPolicy(
                    max_attempts=3,
                    backoff=ExponentialBackoff(initial_delay=1.0),
                    retryable_errors=['TIMEOUT', 'NETWORK_ERROR']
                )
            )
        )
        
        # NEW: Async validator
        self.validator = CardValidatorAsync(self.client)
        
        # Compatibility layer for sync interface
        self._loop = asyncio.new_event_loop()
    
    def process_payment(self, order, card_details):
        """Process payment with compatibility wrapper for sync calls"""
        # Run async method in sync context
        return self._run_async(self._process_payment_async(order, card_details))
    
    async def _process_payment_async(self, order, card_details):
        """Async payment processing - NEW API"""
        try:
            # NEW: Async card validation
            validation_result = await self.validator.validate_card_async(
                card_number=card_details['number'],
                cvv=card_details['cvv'],
                expiry=card_details['expiry']
            )
            
            if not validation_result.is_valid:
                raise ValidationException(
                    message="Invalid card details",
                    errors=validation_result.errors
                )
            
            # NEW: Transaction builder pattern
            transaction = (
                TransactionBuilder()
                .with_amount(order.total, order.currency)
                .with_card(
                    number=card_details['number'],
                    cvv=card_details['cvv'],
                    expiry=card_details['expiry']
                )
                # NEW: add_context replaces set_metadata
                .add_context({
                    'order_id': order.id,
                    'customer_id': order.customer_id,
                    'items': [item.sku for item in order.items]
                })
                .build()
            )
            
            # NEW: Async processing with built-in retry
            result = await self.client.process_transaction_async(transaction)
            
            # NEW: Result object structure
            if result.is_successful:
                return {
                    'success': True,
                    'transaction_id': result.transaction.id,
                    'authorization_code': result.transaction.authorization.code,
                    'amount': result.transaction.amount.value
                }
            else:
                return {
                    'success': False,
                    'error': result.error.message,
                    'code': result.error.code
                }
                
        except PaymentException as e:
            # NEW: Exception structure
            return {
                'success': False,
                'error': e.message,
                'code': e.error_code
            }
    
    def refund_payment(self, transaction_id: str, amount: Optional[float] = None):
        """Issue refund with compatibility wrapper"""
        return self._run_async(self._refund_payment_async(transaction_id, amount))
    
    async def _refund_payment_async(self, transaction_id: str, amount: Optional[float] = None):
        """Async refund processing - NEW API"""
        # NEW: Transaction lookup via client
        transaction = await self.client.get_transaction_async(transaction_id)
        
        if not transaction:
            raise PaymentException(
                message="Transaction not found",
                error_code="TRANSACTION_NOT_FOUND"
            )
        
        # NEW: RefundRequest model
        refund_request = RefundRequest(
            transaction_id=transaction_id,
            amount=amount or transaction.amount.value,
            reason="Customer request",
            # NEW: Additional required fields
            initiated_by="system",
            reference_id=f"refund_{transaction_id}_{int(time.time())}"
        )
        
        # NEW: Async refund processing
        result = await self.client.process_refund_async(refund_request)
        
        return {
            'success': result.is_successful,
            'refund_id': result.refund.id if result.is_successful else None,
            'error': result.error.message if not result.is_successful else None
        }
    
    def get_transaction_status(self, transaction_id: str):
        """Check transaction status with compatibility wrapper"""
        return self._run_async(self._get_transaction_status_async(transaction_id))
    
    async def _get_transaction_status_async(self, transaction_id: str):
        """Async status check - NEW API"""
        transaction = await self.client.get_transaction_async(transaction_id)
        return transaction.status.value if transaction else None
    
    def _run_async(self, coro):
        """Helper to run async code in sync context"""
        try:
            return self._loop.run_until_complete(coro)
        except RuntimeError:
            # Create new loop if needed
            self._loop = asyncio.new_event_loop()
            return self._loop.run_until_complete(coro)
    
    # NEW: Async context manager support
    async def __aenter__(self):
        await self.client.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.disconnect()


# CheckoutController.py - Migrated to support both sync and async
from flask import request, jsonify
import asyncio
import logging
from functools import wraps

def async_route(f):
    """Decorator to run async routes in Flask"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()
    return wrapper

class CheckoutController:
    def __init__(self, payment_service, order_service):
        self.payment_service = payment_service
        self.order_service = order_service
        self.logger = logging.getLogger(__name__)
    
    @async_route
    async def checkout(self):
        """Handle checkout request - NEW Pattern with backward compatibility"""
        try:
            # Get order and card details
            order_id = request.json['order_id']
            card_details = request.json['card']
            
            order = await self._get_order_async(order_id)
            
            # NEW: Async payment processing with compatibility
            if hasattr(self.payment_service, '_process_payment_async'):
                # Use async method directly if available
                result = await self.payment_service._process_payment_async(order, card_details)
            else:
                # Fall back to sync method
                result = self.payment_service.process_payment(order, card_details)
            
            if result['success']:
                # NEW: Async order update
                await self._update_order_async(
                    order,
                    status='paid',
                    transaction_id=result['transaction_id']
                )
                
                # NEW: Standardized response format
                return jsonify({
                    'status': 'success',
                    'data': {
                        'transaction_id': result['transaction_id'],
                        'authorization_code': result.get('authorization_code'),
                        'amount': result['amount']
                    },
                    'message': 'Payment processed successfully'
                })
            else:
                # NEW: Structured error response
                return jsonify({
                    'status': 'error',
                    'error': {
                        'message': result['error'],
                        'code': result['code'],
                        'type': 'payment_failed'
                    }
                }), 400
                
        except Exception as e:
            self.logger.error(f"Checkout failed: {e}", exc_info=True)
            return jsonify({
                'status': 'error',
                'error': {
                    'message': 'Payment processing failed',
                    'type': 'system_error'
                }
            }), 500
    
    async def _get_order_async(self, order_id):
        """Async order retrieval with fallback"""
        if hasattr(self.order_service, 'get_order_async'):
            return await self.order_service.get_order_async(order_id)
        else:
            # Run sync method in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, 
                self.order_service.get_order, 
                order_id
            )
    
    async def _update_order_async(self, order, **updates):
        """Async order update with fallback"""
        for key, value in updates.items():
            setattr(order, key, value)
        
        if hasattr(self.order_service, 'save_order_async'):
            await self.order_service.save_order_async(order)
        else:
            # Run sync method in executor
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.order_service.save_order,
                order
            )


# PaymentConfig.py - New configuration schema with compatibility
import os
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class WebhookConfig:
    """NEW: Structured webhook configuration"""
    success_url: str
    failure_url: str
    refund_url: str
    # NEW: Additional webhook types
    chargeback_url: Optional[str] = None
    dispute_url: Optional[str] = None

class PaymentConfig:
    def __init__(self):
        # NEW: Nested configuration structure
        self.config = {
            'merchant_id': os.getenv('MERCHANT_ID'),
            'api_key': os.getenv('PAYMENT_API_KEY'),
            'environment': os.getenv('PAYMENT_ENV', 'sandbox'),
            # NEW: Nested connection settings
            'connection': {
                'timeout': 30,
                'pool_size': 10,
                'keepalive': True
            },
            # NEW: Separate retry configuration
            'retry': {
                'max_attempts': 3,
                'backoff_factor': 2.0,
                'max_delay': 10.0
            }
        }
        
        # NEW: Structured webhook configuration
        self.webhooks = WebhookConfig(
            success_url='/webhooks/payment/success',
            failure_url='/webhooks/payment/failure',
            refund_url='/webhooks/payment/refund',
            chargeback_url='/webhooks/payment/chargeback',
            dispute_url='/webhooks/payment/dispute'
        )
    
    def get_gateway_config(self) -> Dict[str, Any]:
        """Get gateway configuration - Compatible with old format"""
        # Flatten for backward compatibility
        flat_config = {
            'merchant_id': self.config['merchant_id'],
            'api_key': self.config['api_key'],
            'environment': self.config['environment'],
            'timeout': self.config['connection']['timeout'],
            'retry_count': self.config['retry']['max_attempts']
        }
        return flat_config
    
    def get_client_context(self) -> Dict[str, Any]:
        """NEW: Get configuration for v3 client"""
        return {
            'merchant_id': self.config['merchant_id'],
            'api_credentials': self.config['api_key'],
            'environment': self.config['environment'],
            'connection_config': self.config['connection'],
            'retry_config': self.config['retry']
        }
    
    def validate_config(self):
        """Validate configuration - Enhanced validation"""
        # Check required fields
        required_fields = ['merchant_id', 'api_key']
        for field in required_fields:
            if not self.config.get(field):
                raise ValueError(f"Missing required config: {field}")
        
        # NEW: Validate environment
        valid_environments = ['sandbox', 'staging', 'production']
        if self.config['environment'] not in valid_environments:
            raise ValueError(
                f"Invalid environment: {self.config['environment']}. "
                f"Must be one of: {valid_environments}"
            )
        
        # NEW: Validate connection settings
        if self.config['connection']['timeout'] < 1:
            raise ValueError("Timeout must be at least 1 second")
        
        # NEW: Validate webhook URLs
        for field in ['success_url', 'failure_url', 'refund_url']:
            if not getattr(self.webhooks, field):
                raise ValueError(f"Missing webhook URL: {field}")
    
    # Backward compatibility properties
    @property
    def webhook_urls(self) -> Dict[str, str]:
        """Legacy webhook URLs for backward compatibility"""
        return {
            'success': self.webhooks.success_url,
            'failure': self.webhooks.failure_url,
            'refund': self.webhooks.refund_url
        }