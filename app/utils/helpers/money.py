"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
Package: BitnShop
"""

from typing import Dict, TypedDict, NewType, Optional
from decimal import Decimal, ROUND_HALF_UP

from .settings import get_currency_settings
from .loggers import console_log
from ..constants.currencies import CURRENCY_SYMBOLS

# Creates a distinct type for currency values
MoneyDecimal = NewType('MoneyDecimal', Decimal)


def quantize_amount(value: str | float | Decimal) -> Decimal:
    """
    Quantize a monetary value to the appropriate decimal places for the currency.
    Quantize amount using admin's decimal setting with validation.
    Falls back to currency standard if setting is invalid.
    
    Args:
        value: Monetary value to quantize
        
    Returns:
        Decimal: Quantized value with proper decimal places
        
    Raises:
        ValueError: If quantization fails
        
    Example:
        >>> quantize_currency(100.456)
        Decimal('100.46')
    """
    _, decimal_setting, _, _, _ = get_currency_settings()
    
    try:
        decimals = int(decimal_setting)
        if decimals < 0 or decimals > 8:  # Sanity check
            console_log("warning", "Invalid decimal setting detected, falling back to 2")
            raise ValueError
    except ValueError:
        console_log("warning", "Failed to parse decimal setting, falling back to 2")
        decimals = 2  # Fallback to standard
        
    exponent = Decimal(10) ** -decimals
    return Decimal(str(value)).quantize(exponent, rounding=ROUND_HALF_UP)


def format_money(value) -> str:
    """format Decimal with commas"""
    return f"{value:,.2f}"


def format_monetary_value( amount: Decimal ) -> str:
    """
    Formats a monetary value according to admin-defined settings.

    Args:
        amount: The amount to format.

    Returns:
        A formatted string representation of the currency amount.
    """
    amount = Decimal(amount)
    console_log("initial amount", amount)
    
    
    # Retrieve currency settings
    currency, decimal_places, currency_position, thousand_separator, decimal_separator = get_currency_settings()
    decimal_places = int(decimal_places)
    
    # Format the amount using quantize
    amount = quantize_amount(amount)
    
    amount_str = f"{amount:.{decimal_places}f}"
    integer_part, decimal_part = amount_str.split(".")
    
    # Add commas to the integer part
    integer_part = "{:,}".format(int(integer_part.replace(",", "")))
    
    integer_part = integer_part.replace(",", thousand_separator) # replace commas with thousand_separator
    
    #join formatted integers with formatted decimals
    formatted_amount = f"{integer_part}{decimal_separator}{decimal_part}" if decimal_part else integer_part
    
    
    currency_symbol = CURRENCY_SYMBOLS.get(currency, currency)
    
    # Apply currency position
    match currency_position:
        case "left":
            return f"{currency_symbol}{formatted_amount}"
        case "right":
            return f"{formatted_amount}{currency_symbol}"
        case "left_space":
            return f"{currency_symbol} {formatted_amount}"
        case "right_space":
            return f"{formatted_amount} {currency_symbol}"
        case _:
            return formatted_amount



class CurrencyData(TypedDict):
    name: str
    symbol: str
    decimals: int
    symbol_position: str


def validate_currency(value: Decimal) -> MoneyDecimal:
    """Ensure a Decimal is properly quantized for currency."""
    if value != quantize_amount(value):
        raise ValueError(f"Decimal {value} not in money format; expected {quantize_amount(value)}")
    return MoneyDecimal(value)

