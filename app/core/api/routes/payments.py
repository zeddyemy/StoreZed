from flask_jwt_extended import jwt_required

from . import api_bp
from ..controllers.payments import PaymentController


@api_bp.route('/payments/initialize', methods=['POST'])
@jwt_required()
def initialize_payment():
    """
    Processes a payment for a user.

    Returns:
        json: A JSON object containing the status of the payment, a status code, and a message.
    """
    return PaymentController.initialize_payment()


@api_bp.route('/payments/verify', methods=['POST'])
@jwt_required()
def verify_payment():
    """
    Verifies a payment for a user.

    Returns:
        json: A JSON object containing the status of the verification, a status code, and a message.
    """
    return PaymentController.verify_payment()


@api_bp.route('/payments/webhook', methods=['POST'])
def handle_webhook():
    """
    Handles a webhook for a payment.

    Returns:
        json: A JSON object containing the status of the webhook handling.
    """
    return PaymentController.handle_webhook()
