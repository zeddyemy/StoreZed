from decimal import Decimal
from flask import request, jsonify, json
from sqlalchemy.exc import ( IntegrityError, DataError, DatabaseError, InvalidRequestError )
from flask_jwt_extended import create_access_token, decode_token, get_jwt_identity
from flask_jwt_extended.exceptions import JWTDecodeError

from ....extensions import db
from ....utils.helpers.user import get_current_user
from ....utils.helpers.loggers import log_exception, console_log
from ....utils.helpers.http_response import error_response, success_response
from ....utils.helpers.settings import get_general_setting, get_active_payment_gateway, get_payment_method_setting
from ....utils.payments.exceptions import SignatureError, TransactionMissingError
from ....utils.payments.payment_manager import PaymentManager
from ....enums import PaymentMethods, PaymentType, PaymentStatus, PaymentMethodSettingKeys
from ....models import Payment

class PaymentController:
    
    @staticmethod
    def initialize_payment():
        try:
            current_user = get_current_user()
            payment_manager: PaymentManager = PaymentManager()
            
            active_payment_gateway = get_active_payment_gateway()
            if not active_payment_gateway:
                return error_response("Payment gateway has not been set up.", 400)
            
            gateway = get_payment_method_setting(PaymentMethods.GATEWAY, PaymentMethodSettingKeys.PROVIDER)
            
            # get request data
            data = request.get_json()
            amount = float(str(data.get("amount")).replace(",", ""))
            
            processor = payment_manager.get_payment_processor() # Get the payment processor for the selected gateway
            console_log( "processor", processor )
            
            if not processor:
                error_response("A payment Gateway has not been setup yet. Please contact admin.", 400)
            
            # Start payment processing
            response = payment_manager.initialize_gateway_payment(
                amount=amount,
                currency="NGN",
                user=current_user,
                narration="Wallet top-up"
            )
            
            # On successful initialization
            if response["status"] == "success":
                if response.get("authorization_url", None):
                    return error_response("payment initialized successfully", 200, extra_data=response)
                
                api_response = success_response("payment initialized successfully", 200, extra_data=response)
                
            else:
                api_response = error_response(f"Payment initialization failed: {response.get('message', 'Unknown error')}", 400, extra_data=response)
                
        except Exception as e:
            pass
        
        return api_response
    
    @staticmethod
    def verify_payment():
        """Verify payment status manually."""
        try:
            current_user = get_current_user()
            payment_manager: PaymentManager = PaymentManager()
            
            active_payment_gateway = get_active_payment_gateway()
            if not active_payment_gateway:
                return error_response("Payment gateway has not been set up.", 400)
            
            # get request data
            data = request.get_json()
            reference = data.get("reference", None) # Extract reference from request body
            
            payment: Payment = Payment.query.filter_by(key=reference).first()
            if not payment:
                return error_response("Payment not found", 404)
            
            # Proceed with verifying the payment using the PaymentManager
            verification_response = payment_manager.verify_gateway_payment(payment)
            
            payment_manager.handle_gateway_payment(payment, verification_response)
            
            payment_type = payment.meta_info.get("payment_type", str(PaymentType.WALLET_TOP_UP))
            
            if verification_response['status'] != PaymentStatus.COMPLETED:
                return error_response(
                    "Payment verification failed",
                    400,
                    extra_data=verification_response
                )
            
            if payment_type == str(PaymentType.WALLET_TOP_UP):
                msg = "Wallet has been credited successfully!"
            elif payment_type == str(PaymentType.ORDER_PAYMENT):
                msg = "Order has been paid for!"
            else:
                msg = "Payment verified successfully"
            
            api_response = success_response(msg, 200)
        except (DataError, DatabaseError) as e:
            db.session.rollback()
            log_exception('Database error occurred during payment verification', e)
            api_response = error_response('Error interacting to the database.', 500)
        except Exception as e:
            db.session.rollback()
            log_exception(f"An exception occurred during payment verification", e)
            api_response = error_response('An unexpected error.', 500)
        finally:
            db.session.close()
        
        return api_response
    
    @staticmethod
    def handle_webhook():
        """
        Handle payment gateway webhooks.

        Verifies webhook signature, processes payment status updates, and handles 
        successful payments (wallet top-up, order payment, subscription activation).
        
        This method verifies the signature of the webhook request, checks if the event is a successful payment event, and if so, updates the database and records the payment in the database. If an error occurs at any point, it returns an error response with an appropriate status code and message.

        Returns:
            tuple[Response, int]: Flask response and status code
        """
        try:
            payment_manager: PaymentManager = PaymentManager()
            
            payload = request.get_json() # Get webhook data and headers
            
            console_log("Webhook payload", payload)
            
            processor = payment_manager.get_payment_processor()  # Get the payment processor for the selected gateway
            
            # Verify webhook signature
            if not processor.verify_webhook_signature():
                raise SignatureError("Invalid webhook signature")
            
            # Parse webhook data into standard format based on event type
            webhook_data = processor.parse_webhook_event(payload)
            
            console_log("Parsed Webhook Data", webhook_data)
            
            api_response = payment_manager.handle_gateway_webhook(webhook_data)
            
            console_log("api_response", api_response)
            
        except SignatureError as e:
            log_exception("Invalid webhook signature", e)
            api_response = error_response(str(e), e.status_code)
            
        except TransactionMissingError as e:
            log_exception("Transaction not found", e)
            api_response = error_response(str(e), e.status_code)
            
        except ValueError as e:
            log_exception("Payment validation failed", e)
            api_response = error_response(str(e), 400)
        except Exception as e:
            log_exception("Webhook processing failed", e)
            api_response = error_response("Webhook processing failed", 500)
        
        finally:
            db.session.close()
        
        return api_response