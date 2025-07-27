# PaymentService.py - Using deprecated payment-lib v2 API
from payment_lib import PaymentGateway, Transaction, CardValidator
from payment_lib.errors import PaymentError, ValidationError
import time

class PaymentService:
    def __init__(self, config):
        # DEPRECATED: Constructor-based initialization
        self.gateway = PaymentGateway(
            merchant_id=config['merchant_id'],
            api_key=config['api_key'],
            environment=config['environment']
        )
        
        # DEPRECATED: Synchronous validation
        self.validator = CardValidator()
        
        # DEPRECATED: Manual retry configuration
        self.max_retries = 3
        self.retry_delay = 1
    
    def process_payment(self, order, card_details):
        """Process payment synchronously - OLD API"""
        try:
            # DEPRECATED: validate_card is now async
            if not self.validator.validate_card(card_details['number']):
                raise ValidationError("Invalid card number")
            
            # DEPRECATED: create_transaction replaced with build_transaction
            transaction = Transaction.create_transaction(
                amount=order.total,
                currency=order.currency,
                card_number=card_details['number'],
                card_cvv=card_details['cvv'],
                card_expiry=card_details['expiry']
            )
            
            # DEPRECATED: set_metadata replaced with add_context
            transaction.set_metadata({
                'order_id': order.id,
                'customer_id': order.customer_id,
                'items': [item.sku for item in order.items]
            })
            
            # DEPRECATED: Synchronous processing
            result = self._process_with_retry(transaction)
            
            # DEPRECATED: Access pattern changed
            if result.status == 'success':
                return {
                    'success': True,
                    'transaction_id': result.transaction_id,
                    'authorization_code': result.auth_code,
                    'amount': result.amount
                }
            else:
                return {
                    'success': False,
                    'error': result.error_message,
                    'code': result.error_code
                }
                
        except PaymentError as e:
            # DEPRECATED: Error structure changed
            return {
                'success': False,
                'error': str(e),
                'code': e.code
            }
    
    def _process_with_retry(self, transaction):
        """Manual retry logic - OLD Pattern"""
        for attempt in range(self.max_retries):
            try:
                # DEPRECATED: process() is now process_async()
                result = self.gateway.process(transaction)
                
                # DEPRECATED: Need to check specific error codes
                if result.error_code in ['TIMEOUT', 'NETWORK_ERROR']:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                    
                return result
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(self.retry_delay * (attempt + 1))
    
    def refund_payment(self, transaction_id, amount=None):
        """Issue refund - OLD API"""
        # DEPRECATED: get_transaction is removed
        original = self.gateway.get_transaction(transaction_id)
        
        if not original:
            raise PaymentError("Transaction not found")
        
        # DEPRECATED: Refund API completely changed
        refund = original.create_refund(
            amount=amount or original.amount,
            reason="Customer request"
        )
        
        # DEPRECATED: Synchronous refund
        return self.gateway.process_refund(refund)
    
    def get_transaction_status(self, transaction_id):
        """Check transaction status - OLD API"""
        # DEPRECATED: Direct status check removed
        transaction = self.gateway.get_transaction(transaction_id)
        return transaction.status if transaction else None


# CheckoutController.py - Using old patterns
from flask import request, jsonify
import logging

class CheckoutController:
    def __init__(self, payment_service, order_service):
        self.payment_service = payment_service
        self.order_service = order_service
        self.logger = logging.getLogger(__name__)
    
    def checkout(self):
        """Handle checkout request - OLD Pattern"""
        try:
            # Get order and card details
            order_id = request.json['order_id']
            card_details = request.json['card']
            
            order = self.order_service.get_order(order_id)
            
            # DEPRECATED: Synchronous payment processing
            result = self.payment_service.process_payment(order, card_details)
            
            if result['success']:
                # DEPRECATED: Manual status update
                order.status = 'paid'
                order.transaction_id = result['transaction_id']
                self.order_service.save_order(order)
                
                # DEPRECATED: Response format
                return jsonify({
                    'status': 'success',
                    'transaction_id': result['transaction_id'],
                    'message': 'Payment processed successfully'
                })
            else:
                return jsonify({
                    'status': 'error',
                    'error': result['error'],
                    'code': result['code']
                }), 400
                
        except Exception as e:
            self.logger.error(f"Checkout failed: {e}")
            return jsonify({
                'status': 'error',
                'error': 'Payment processing failed'
            }), 500


# PaymentConfig.py - Old configuration schema
class PaymentConfig:
    def __init__(self):
        # DEPRECATED: Flat configuration structure
        self.config = {
            'merchant_id': os.getenv('MERCHANT_ID'),
            'api_key': os.getenv('PAYMENT_API_KEY'),
            'environment': os.getenv('PAYMENT_ENV', 'sandbox'),
            'timeout': 30,
            'retry_count': 3
        }
        
        # DEPRECATED: Webhook URLs in config
        self.webhook_urls = {
            'success': '/webhooks/payment/success',
            'failure': '/webhooks/payment/failure',
            'refund': '/webhooks/payment/refund'
        }
    
    def get_gateway_config(self):
        """Get gateway configuration - OLD Format"""
        return self.config
    
    def validate_config(self):
        """Validate configuration - OLD Method"""
        required = ['merchant_id', 'api_key']
        for key in required:
            if not self.config.get(key):
                raise ValueError(f"Missing required config: {key}")