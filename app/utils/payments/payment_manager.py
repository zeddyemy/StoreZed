from .processor.bitpay import BitPayProcessor
from .processor.flutterwave import FlutterwaveProcessor
from .processor.paystack import PaystackProcessor
from ..helpers.settings import get_active_payment_gateway
from ...enums.payments import PaymentGatewayName

def get_payment_processor():
    """
    Returns an instance of the correct payment processor based on the configured provider.
    
    Returns:
        Instance of a payment processor (BitPayProcessor, FlutterwaveProcessor, or PaystackProcessor).
    """
    payment_gateway = get_active_payment_gateway()
    
    if not payment_gateway:
        return None

    provider = payment_gateway["provider"]
    api_key = payment_gateway["credentials"].get("api_key")

    processors = {
        "bitpay": BitPayProcessor(api_key),
        "flutterwave": FlutterwaveProcessor(api_key),
        "paystack": PaystackProcessor(api_key)
    }

    return processors.get(provider)


def get_payment_providers() -> list[str]:
    providers = []
    for name, member in PaymentGatewayName.__members__.items():
        providers.append(member.value)
    
    return providers
