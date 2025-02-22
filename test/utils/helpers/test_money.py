import pytest
from decimal import Decimal
from unittest.mock import patch
from app.utils.helpers.money import format_monetary_value

# Helper to mock currency settings
def mock_currency_settings(currency, decimal_places, position, thousand_sep, decimal_sep):
    return (currency, str(decimal_places), position, thousand_sep, decimal_sep)

# Test negative amount
@patch('app.utils.helpers.money.get_currency_settings')
def test_format_monetary_value_negative(mock_get_settings, app_context):
    mock_get_settings.return_value = mock_currency_settings("USD", 2, "left", ",", ".")
    amount = Decimal('-1234.56')
    formatted = format_monetary_value(amount)
    assert formatted == "$-1,234.56"  # Adjust if negative sign placement differs

# Test zero amount
@patch('app.utils.helpers.money.get_currency_settings')
def test_format_monetary_value_zero(mock_get_settings, app_context):
    mock_get_settings.return_value = mock_currency_settings("USD", 2, "left", ",", ".")
    amount = Decimal('0.00')
    formatted = format_monetary_value(amount)
    assert formatted == "$0.00"

# Test large number
@patch('app.utils.helpers.money.get_currency_settings')
def test_format_monetary_value_large_number(mock_get_settings, app_context):
    mock_get_settings.return_value = mock_currency_settings("USD", 2, "left", ",", ".")
    amount = Decimal('123456789.12')
    formatted = format_monetary_value(amount)
    assert formatted == "$123,456,789.12"
    

@patch('app.utils.helpers.money.get_currency_settings')
def test_format_monetary_value_currency_right(mock_get_settings, app_context):
    mock_get_settings.return_value = mock_currency_settings("USD", 2, "right", ",", ".")
    amount = Decimal('1234.56')
    formatted = format_monetary_value(amount)
    assert formatted == "1,234.56$"  # Adjust based on your function's logic