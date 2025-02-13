import requests
from decimal import Decimal

from . import PaymentProcessor

class FlutterwaveProcessor(PaymentProcessor):
    """
    Handles payments via Flutterwave API.
    """
    def process_payment(self, amount: float | Decimal, currency: str, customer_data: dict):
        url = "https://api.flutterwave.com/v3/payments"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        data = {
            "tx_ref": "TX123456789",
            "amount": amount,
            "currency": currency,
            "redirect_url": "https://yourwebsite.com/payment-success",
            "customer": {
                "email": customer_data["email"],
                "name": customer_data["name"]
            }
        }

        response = requests.post(url, json=data, headers=headers)
        return response.json()
