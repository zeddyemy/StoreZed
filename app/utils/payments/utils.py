"""
Contains Utility Functions to assist with payment operations

@author Emmanuel Olowu
@link: https://github.com/zeddyemy
"""


def format_currency(value) -> str:
    """format Decimal with commas"""
    return f"{value:,.2f}"

def format_price(amount, currency="NGN", num_decimals=2, thousand_sep=",", decimal_sep="."):
    """
    Utility function for formatting prices.
    """
    formatted_amount = "{:,.{}f}".format(amount, num_decimals)
    formatted_amount = formatted_amount.replace(",", thousand_sep).replace(".", decimal_sep)
    
    if currency == "NGN":
        return f"₦{formatted_amount}"
    else:
        return f"{formatted_amount} {currency}"