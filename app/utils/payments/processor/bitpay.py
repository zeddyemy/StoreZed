import requests
from decimal import Decimal

from . import PaymentProcessor

class BitPayProcessor(PaymentProcessor):
    """
    Handles payments via BitPay API.
    """
    def process_payment(self, amount: float | Decimal, currency: str, customer_data: dict):
        url = "https://bitpay.com/api/v2/invoice"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {
            "price": amount,
            "currency": currency,
            "buyerEmail": customer_data["email"]
        }

        response = requests.post(url, json=data, headers=headers)
        return response.json()
