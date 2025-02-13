from enum import Enum


class PaymentMethods(Enum):
    """
    Enum representing available payment methods.
    """
    BACS = "bacs"
    CHECK = "check"
    COD = "cod"
    GATEWAY = "gateway"

    def __str__(self):
        return self.value  # Returns "bacs", "check", etc.

class PaymentStatus(Enum):
    """ENUMS for the payment status field in Payment Model"""
    SUCCESSFUL = "successful"
    PENDING = "pending"
    ABANDONED = "abandoned"

class TransactionType(Enum):
    """ENUMS for the transaction_type field in Transaction Model"""
    CREDIT = "credit"
    DEBIT = "debit"
    PAYMENT = "payment"
    WITHDRAWAL = "withdrawal"
    

class PaymentGatewayName(Enum):
    """ENUMS for the payment gateway"""
    BITPAY = "BitPay"
    FLUTTERWAVE = "Flutterwave"
    PAYSTACK = "Paystack"
    # COINBASE = "CoinBase"
    # STRIP = "Stripe"
    
    def __str__(self):
        return self.value  # Returns "BitPay", "CoinBase", etc.