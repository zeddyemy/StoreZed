from typing import Optional
from decimal import Decimal
from flask import url_for

from ...extensions import db
from .exceptions import TransactionMissingError
from .types import PaymentWebhookData, TransferWebhookData
from .utils import record_payment_transaction, safe_compare_amounts
from .wallet import credit_wallet
from .processor import PaymentProcessorResponse, PaymentVerificationResponse, PaymentProcessor
from .processor.bitpay import BitPayProcessor
from .processor.flutterwave import FlutterwaveProcessor
from .processor.paystack import PaystackProcessor
from ..helpers.money import quantize_amount
from ..helpers.http_response import success_response, error_response
from ..helpers.settings import get_active_payment_gateway, get_general_setting
from ..helpers.site import get_site_url, get_platform_url
from ..helpers.loggers import log_exception, console_log
from ..decorators.retry import retry
from ...enums import PaymentGatewayName, PaymentStatus, OrderStatus, PaymentType, GeneralSettingsKeys
from ...models import AppUser, Payment, Transaction, CustomerOrder, Subscription


class PaymentManager:
    def __init__(self):
        self.processors = {
            "bitpay": BitPayProcessor,
            "flutterwave": FlutterwaveProcessor,
            "paystack": PaystackProcessor
        }
        self.payment_gateway = get_active_payment_gateway()


    def get_payment_processor(self) -> Optional[BitPayProcessor | FlutterwaveProcessor | PaystackProcessor]:
        """
        Returns an instance of the correct payment processor based on the configured provider.
        
        Returns:
            Optional[BitPayProcessor | FlutterwaveProcessor | PaystackProcessor]: Instance of a payment processor.
        """
        
        payment_gateway = self.payment_gateway
        
        if not payment_gateway or not payment_gateway.get("credentials"):
            raise ValueError("Payment gateway not properly configured")
        
        provider = payment_gateway["provider"]
        credentials = payment_gateway.get("credentials")
        
        # Convert test_mode to boolean
        test_mode = credentials.get("test_mode", "false").lower() == "true"  # Converts to True/False
        
        # Get keys safely
        api_key = credentials.get("test_api_key" if test_mode else "api_key", "")
        secret_key = credentials.get("test_secret_key" if test_mode else "secret_key", "")
        public_key = credentials.get("test_public_key" if test_mode else "public_key", "")
        
        processors:dict[str, BitPayProcessor | FlutterwaveProcessor | PaystackProcessor] = {
            "bitpay": BitPayProcessor(
                secret_key=secret_key,
                public_key=public_key,
                api_key=api_key
            ),
            "flutterwave": FlutterwaveProcessor(
                secret_key=secret_key,
                public_key=public_key,
                api_key=api_key
            ),
            "paystack": PaystackProcessor(
                secret_key=secret_key,
                public_key=public_key,
                api_key=api_key
            )
        }
        
        return processors.get(provider)


    def initialize_gateway_payment(
        self,
        amount: Decimal,
        currency: str,
        user: AppUser,
        payment_type: PaymentType = PaymentType.WALLET_TOP_UP,
        narration: Optional[str] = None,
        extra_meta: Optional[dict] = None,
        redirect_url: Optional[str] = None) -> PaymentProcessorResponse:
        """
        Initialize payment with any gateway and return standardized response.
        
        Args:
            amount: Payment amount
            currency: Payment currency
            user: AppUser
            payment_type: Type of payment (wallet, order, subscription)
            narration: Payment Narration
            extra_meta: Additional metadata (e.g., order_id, subscription_id)
            redirect_url: URL where users should be redirected to
        
        Returns:
            PaymentProcessorResponse: Standardized payment response
        """
        try:
            processor = self.get_payment_processor()
            
            amount = quantize_amount(amount)
            
            # Create payment and transaction records using processor's reference
            payment, transaction = record_payment_transaction(
                user=user,
                amount=amount,
                payment_method=processor.__class__.__name__.replace('Processor', '').lower(),
                status=PaymentStatus.PENDING,
                narration=narration,
                reference=processor.reference,  # Using the processor's reference
                payment_type=payment_type,
                extra_meta=extra_meta
            )
        
            # Use the passed `redirect_url`, or fall back to default
            if not redirect_url:
                if payment_type == PaymentType.WALLET_TOP_UP:
                    redirect_url = f"{get_platform_url()}/payments/verify/?payment_type={str(PaymentType.WALLET_TOP_UP)}"
                elif payment_type == PaymentType.ORDER_PAYMENT:
                    redirect_url = f"{get_platform_url()}/payments/verify/?payment_type={str(PaymentType.ORDER_PAYMENT)}"
                else:
                    redirect_url = f"{get_platform_url()}/payments/verify"
            
            console_log("redirect_url", redirect_url)
            
            customer_data = {
                "email": user.email,
                "name": user.full_name
            }
            # user system currency
            platform_currency = get_general_setting(GeneralSettingsKeys.CURRENCY, default='NGN')
            
            # Initialize payment with gateway
            response = processor.initialize_payment(amount, platform_currency, customer_data, redirect_url)
            
            return response

        except Exception as e:
            # Log the error with original response
            log_exception(f"Payment initialization failed for {processor.__class__.__name__}", e)
            
            # Return standardized error response
            return PaymentProcessorResponse(
                status="error",
                message="An unexpected error occurred initializing payment",
                payment_id=None,
                authorization_url=None,
                reference=processor.reference  # Using the processor's reference
            )


    def verify_gateway_payment(self, payment: Payment) -> PaymentVerificationResponse:
        """
        Verify payment status with gateway and handle response.
        
        Args:
            processor: Payment processor instance
            payment: Payment record to verify
        
        Returns:
            PaymentVerificationResponse: Standardized verification response
        """
        try:
            processor = self.get_payment_processor()
            
            verification_response = processor.verify_payment(payment.key)
            
            # Validate amount matches
            response_amount = Decimal(verification_response["amount"])
            payment_amount = Decimal(payment.amount)
            if response_amount != payment_amount:
                raise ValueError("Verified amount doesn't match payment record")
            
            return verification_response
        except Exception as e:
            log_exception(f"Payment verification failed for {payment.key}", e)
            return PaymentVerificationResponse(
                status=PaymentStatus.FAILED,
                amount=payment.amount,
                currency=payment.currency_code,
                provider_reference=payment.key,
                meta_info={"error": str(e)}
            )

    def handle_gateway_payment(self, payment: Payment, verification_response: PaymentVerificationResponse):
        # Handle payment completion based on payment type
        if verification_response['status'] == PaymentStatus.COMPLETED:
            self.handle_completed_payment(payment, verification_response)
        elif verification_response['status'] == PaymentStatus.ABANDONED:
            self.handle_abandoned_payment(payment, verification_response)
        elif verification_response["status"] == PaymentStatus.FAILED:
            self.handle_failed_payment(payment, verification_response)
        else:
            self.handle_failed_payment(payment, verification_response)
            
            
        db.session.commit()

    def handle_gateway_webhook(self, webhook_data: PaymentWebhookData | TransferWebhookData):
        event_type = webhook_data.get('event_type')
        
        console_log("event_type", event_type)
    
        if event_type == 'payment':
            return self._handle_payment_webhook(webhook_data)
        elif event_type == 'transfer':
            return self._handle_transfer_webhook(webhook_data)
        else:
            raise ValueError(f"Unknown event type: {event_type}")
    
    def _handle_payment_webhook(self, webhook_data: PaymentWebhookData):
        """
        Handle payment webhook events.
        
        Args:
            webhook_data: Standardized payment webhook data
            
        Returns:
            Flask Response object
            
        Raises:
            TransactionMissingError: If payment record not found
            ValueError: If payment amount mismatch
        """
        
        # Find related order
        # Find payment record
        payment: Payment = Payment.query.filter_by(key=webhook_data["reference"]).first()
        if not payment:
            raise TransactionMissingError(f"Payment not found: {webhook_data['reference']}")
        
        console_log("payment", payment)
        
        # Validate amount matches
        webhook_amount = Decimal(webhook_data["amount"])
        payment_amount = Decimal(payment.amount)
        if safe_compare_amounts(webhook_amount, payment_amount):
            raise ValueError("Verified amount doesn't match payment record")
            
        
        if webhook_data["status"] == PaymentStatus.COMPLETED:
            # Handle successful payment (top-up wallet, update order, etc.)
            self.handle_completed_payment(payment)
        elif webhook_data["status"] == PaymentStatus.ABANDONED:
            self.handle_abandoned_payment(payment)
        elif webhook_data["status"] == PaymentStatus.FAILED:
            self.handle_failed_payment(payment)
        
        db.session.commit()
        
        return success_response("Payment webhook processed successfully", 200)
    
    def _handle_transfer_webhook(self, webhook_data: TransferWebhookData):
        """
        Handle transfer webhook events.
        
        Args:
            webhook_data: Standardized transfer webhook data
            
        Returns:
            Flask Response object
            
        Raises:
            TransactionMissingError: If transfer record not found
            ValueError: If transfer amount mismatch
        """
        
        # TODO: Finish up function to handle transfer webhook
    
        # # Find transfer record
        # transfer = Transfer.query.filter_by(reference=webhook_data["reference"]).first()
        # if not transfer:
        #     raise TransactionMissingError(f"Transfer not found: {webhook_data['reference']}")
        
        # # Validate amount matches
        # if webhook_data["status"] == TransferStatus.COMPLETED:
        #     if webhook_data["amount"] != transfer.amount:
        #         raise ValueError("Transfer amount mismatch")
                
        #     # Handle successful transfer (update recipient balance, etc.)
        #     handle_transfer_completion(transfer)
        
        # # Update transfer status
        # transfer.update(
        #     status=webhook_data["status"],
        #     provider_reference=webhook_data["provider_reference"]
        # )
        
        # return success_response("Transfer webhook processed successfully", 200)


    def handle_completed_payment(self, payment: Payment, verification: PaymentVerificationResponse = {}):
        """
        Handle different types of successful payments.
        
        Args:
            payment: Verified payment record
            verification: Payment verification response
        """
        try:
            payment_type = payment.meta_info.get('payment_type', str(PaymentType.WALLET_TOP_UP))
            
            console_log("payment_type", payment_type)
            
            transaction: Transaction = Transaction.query.filter_by(key=payment.key).first()
            
            if payment.status != str(PaymentStatus.COMPLETED):
                if payment_type == str(PaymentType.WALLET_TOP_UP):
                    user: AppUser = payment.app_user
                    credit_wallet(user.id, payment.amount, commit=False)
                
                elif payment_type == str(PaymentType.ORDER_PAYMENT):
                    order_id = payment.meta_info.get('order_id')
                    if order_id:
                        order: CustomerOrder = CustomerOrder.query.get(order_id)
                        order.update(status=OrderStatus.PAID)
                
                elif payment_type == str(PaymentType.SUBSCRIPTION):
                    subscription_id = payment.meta_info.get('subscription_id')
                    if subscription_id:
                        subscription: Subscription = Subscription.query.get(subscription_id)
                        subscription.extend_validity()
                
                # Update payment status
                payment.update(status=str(PaymentStatus.COMPLETED))
                transaction.update(status=str(PaymentStatus.COMPLETED))
        except Exception as e:
            log_exception("Payment completion handling failed", e)
            raise e

    def handle_abandoned_payment(self, payment: Payment, verification: PaymentVerificationResponse = {}):
        try:
            transaction: Transaction = Transaction.query.filter_by(key=payment.key).first()
            if payment.status != str(PaymentStatus.ABANDONED):
                payment.update(status=str(PaymentStatus.ABANDONED), commit=False)
                transaction.update(status=str(PaymentStatus.ABANDONED), commit=False)
        except Exception as e:
            log_exception("Handling of abandoned payment failed", e)
            raise e
    
    def handle_failed_payment(self, payment: Payment, verification: PaymentProcessorResponse = {}):
        try:
            transaction: Transaction = Transaction.query.filter_by(key=payment.key).first()
            if payment.status != str(PaymentStatus.FAILED):
                payment.update(status=str(PaymentStatus.FAILED), commit=False)
                transaction.update(status=str(PaymentStatus.FAILED), commit=False)
        except Exception as e:
            log_exception("Handling of failed payment failed.", e)
            raise e

