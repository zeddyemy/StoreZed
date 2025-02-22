"""
Author: Emmanuel Olowu
Link: https://eshomonu.com
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
"""

from flask import render_template, request, flash, redirect, abort, url_for
from flask_login import login_required, current_user
from requests.exceptions import RequestException
from sqlalchemy.exc import SQLAlchemyError

from ....extensions import db
from ....enums import PaymentStatus, PaymentMethodSettingKeys, PaymentType, PaymentGatewayName
from ....utils.decorators.auth import login_required
from ....utils.helpers.settings import get_active_payment_gateway, get_payment_method_setting
from ....utils.helpers.loggers import log_exception, console_log
from ....utils.forms import handle_form_errors
from ....utils.forms.web_front.payments import TopUpForm
from ....utils.payments.payment_manager import PaymentManager
from ....models import Payment

from . import web_front_bp

@web_front_bp.route("/payments/verify/", methods=['GET', 'POST'])
@web_front_bp.route("/payments/verify", methods=['GET', 'POST'])
def verify_payment():
    try:
        payment_manager:PaymentManager = PaymentManager()
        
        provider = request.args.get("provider")
        
        # Collect all possible references from request
        references = [
            request.args.get("tx_ref"),  # Flutterwave
            request.args.get("reference"),  # Paystack
            request.args.get("id"),  # BitPay
        ]
        # Filter out None values
        references = [ref for ref in references if ref is not None]
        
        if not references:
            flash("Payment reference missing.", "danger")
            return redirect(url_for("web_front.index"))
        
        # Find payment by any reference (assuming references are unique across providers)
        payment: Payment = Payment.query.filter(Payment.key.in_(references)).first()
        
        if not payment:
            flash("Payment record is missing", "danger")
            return redirect(url_for("web_front.index"))
        
        # Proceed with verifying the payment using the PaymentManager
        verification_response = payment_manager.verify_gateway_payment(payment)
        
        payment_manager.handle_gateway_payment(payment, verification_response)
        payment_type = payment.meta_info.get("payment_type", str(PaymentType.WALLET_TOP_UP))
        
        
        if verification_response['status'] == PaymentStatus.COMPLETED:
            if payment_type == str(PaymentType.WALLET_TOP_UP):
                flash("Your wallet has been credited successfully!", "success")
                return redirect(url_for("web_front.top_up"))
            elif payment_type == str(PaymentType.ORDER_PAYMENT):
                flash("Your order has been paid for!", "success")
                order_id = payment.meta_info.get("order_id")
                return redirect(url_for("web_front.order", order_id=order_id))
            else:
                flash("Payment successful!", "success")
                return redirect(url_for("web_front.index"))
        else:
            flash("Payment failed. Please try again.", "danger")
            return redirect(url_for("web_front.index"))
        
    except Exception as e:
        log_exception("Unexpected Error occurred Verifying payment", e)
        flash("An unexpected error occurred", "danger")
        return redirect(url_for("web_front.index"))
    