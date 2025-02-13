from decimal import Decimal

class PaymentProcessor:
    """
    Base class for payment processors.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key

    def process_payment(self, amount: float | Decimal, currency: str, customer_data: dict):
        """
        Abstract method for processing payments.
        Must be implemented by subclasses.
        
        Returns:
            dict: {
                "status": "success" | "failed",
                "message": str,
                "transaction_id": str | None,
                "redirect_url": str | None (if applicable)
            }
        """
        raise NotImplementedError("Subclasses must implement this method.")
