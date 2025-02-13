'''
This module contains the functions for handling conversion rates of currencies

@author Emmanuel Olowu
@link: https://github.com/zeddyemy
'''

import requests
from decimal import Decimal
from cachetools import cached, TTLCache

from config import Config
from .utils import format_currency, format_price
from ..helpers.loggers import console_log, log_exception

# Create a cache with a Time-To-Live (TTL) of 12 hour (43200 seconds)
cache = TTLCache(maxsize=100, ttl=864000)

@cached(cache)
def fetch_exchange_rates(base_currency="NGN") -> dict | None:
    response = requests.get(f"{Config.EXCHANGE_RATE_API_URL}/{base_currency}")
    
    if response.status_code == 200:
        response_data = response.json()
        if response_data.get("result") == "success":
            return response_data.get('conversion_rates')
    return None


def convert_amount(amount_in_usd, target_currency, format=True) -> str | Decimal:
    exchange_rates = fetch_exchange_rates()
    
    converted_amount = amount_in_usd # Default to dollar if no rate is found
    
    if target_currency in exchange_rates:
        converted_amount = Decimal(amount_in_usd) * Decimal(exchange_rates[target_currency])
    
    amount = round(converted_amount, 2)
    amount = format_currency(amount) if format else amount
    return amount

