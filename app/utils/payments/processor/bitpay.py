import requests
from decimal import Decimal
from typing import Optional, Any

from . import PaymentProcessor
from ..types import PaymentProcessorResponse, PaymentWebhookData, TransferWebhookData

class BitPayProcessor(PaymentProcessor):
    """
    Handles payments via BitPay API.
    """
    reference_prefix = "btp_"
    
    def initialize_payment(self, amount: float | Decimal, currency: str, customer_data: dict, redirect_url: Optional[str] = None) -> PaymentProcessorResponse:
        url = "https://bitpay.com/api/v2/invoice"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {
            "price": amount,
            "currency": currency,
            "buyerEmail": customer_data["email"]
        }

        response = requests.post(url, json=data, headers=headers)
        return response.json()
