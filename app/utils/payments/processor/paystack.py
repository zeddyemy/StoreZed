import requests
from decimal import Decimal

from . import PaymentProcessor

class PaystackProcessor(PaymentProcessor):
    """
    Handles payments via Paystack API.
    """
    def process_payment(self, amount: float | Decimal, currency: str, customer_data: dict):
        url = "https://api.paystack.co/transaction/initialize"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        data = {
            "email": customer_data["email"],
            "amount": int(amount * 100),
            "currency": currency
        }

        response = requests.post(url, json=data, headers=headers)
        return response.json()
