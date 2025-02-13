"""
Author: Emmanuel Olowu
Link: https://github.com/zeddyemy
Copyright: © 2024 Emmanuel Olowu <zeddyemy@gmail.com>
License: MIT, see LICENSE for more details.
Package: BitnShop
"""
from flask import request
from typing import List
from functools import lru_cache

from ...extensions import db
from ...enums.payments import PaymentMethods
from ...enums.settings import GeneralSettingsKeys, PaymentMethodSettingKeys
from ...models.settings import GeneralSetting, PaymentMethodSettings
from .loggers import console_log


def get_default_setting(key: GeneralSettingsKeys) -> str:
    """
    Retrieves the default value for a given settings key.

    Args:
        key (GeneralSettingsKeys): The settings key Enum.

    Returns:
        str: The default value for the setting, or an empty string if not explicitly defined.
    """
    
    defaults = {
        GeneralSettingsKeys.SITE_TITLE: "My E-commerce Site",
        GeneralSettingsKeys.TIMEZONE: "UTC",
        GeneralSettingsKeys.THOUSAND_SEPARATOR: ",",
        GeneralSettingsKeys.DECIMAL_SEPARATOR: ".",
        GeneralSettingsKeys.NUMBER_OF_DECIMALS: "2",
    }
    return defaults.get(key, "")  # Default to empty string


def get_all_general_settings() -> dict[str, str]:
    """
    Retrieves all general settings as a dictionary. {key: value}

    Returns:
        dict[str, str]: A dictionary where the keys are setting names and values are their stored values.
    """
    general_settings: list[GeneralSetting] = GeneralSetting.query.all()
    
    return {setting.key: setting.value for setting in general_settings}


@lru_cache(maxsize=1)  # Cache settings to optimize performance
def get_general_setting(key: GeneralSettingsKeys, default=None) -> str | None:
    """
    Retrieves a specific general setting value from the database.

    Args:
        key (GeneralSettingsKeys): The settings key Enum.
        default: Default value if setting is not found.

    Returns:
        str: The stored setting value, or default.
    """
    
    setting: GeneralSetting = GeneralSetting.query.filter_by(key=str(key)).first()
    
    return setting.value if setting else default


def save_general_setting(key: GeneralSettingsKeys, value: str):
    """
    Saves or updates a specific setting in the database.

    Args:
        key (GeneralSettingsKeys): The settings key Enum.
        value (str): The value to store.
    """
    setting: GeneralSetting = GeneralSetting.query.filter_by(key=str(key)).first()
    console_log("setting", setting)
    
    if setting:
        setting.value = value
        db.session.merge(setting)
    else:
        setting = GeneralSetting(key=key, value=value)
        db.session.merge(setting)
        db.session.add(setting)
    
    
    db.session.commit()
    get_general_setting.cache_clear()  # Clears cache to reflect new values


def get_payment_method_settings(method: PaymentMethods) -> dict:
    """
    Retrieve all settings for a specific payment method.

    Args:
        method (PaymentMethods): The payment method key.

    Returns:
        dict: A dictionary of all settings for the method.
    """
    settings: PaymentMethodSettings = PaymentMethodSettings.query.filter_by(method=str(method)).all()
    return {setting.key: setting.value for setting in settings}


def get_payment_method_setting(method: PaymentMethods, key: PaymentMethodSettingKeys) -> str:
    """
    Retrieve a specific payment method setting.

    Args:
        method (PaymentMethods): The payment method key (e.g., 'bacs', 'cod', 'gateway').
        key (PaymentMethodSettingKeys): The setting key (e.g., 'enabled', 'account_number').

    Returns:
        str: The setting value, or None if not found.
    """
    setting: PaymentMethodSettings = PaymentMethodSettings.query.filter_by(method=str(method), key=str(key)).first()
    return setting.value if setting else None

def save_payment_method_setting(method: PaymentMethods, key: PaymentMethodSettingKeys, value: str):
    """
    Save or update a payment setting.

    Args:
        method (PaymentMethods): The payment method key.
        key (PaymentMethodSettingKeys): The setting key.
        value (str): The value to store.
    """
    setting: PaymentMethodSettings = PaymentMethodSettings.query.filter_by(method=str(method), key=str(key)).first()
    
    if setting:
        setting.value = value
    else:
        setting = PaymentMethodSettings(method=str(method), key=str(key), value=value)
        db.session.add(setting)
    
    db.session.commit()


def get_default_payment_method_settings() -> dict[PaymentMethods, dict[PaymentMethodSettingKeys, str]]:
    """
    Returns a dictionary of default payment method settings.

    Returns:
        dict: {PaymentMethods: {PaymentMethodSettingKeys: Default Value}}
    """
    DEFAULT_PAYMENT_SETTINGS = {
        PaymentMethods.BACS: {
            PaymentMethodSettingKeys.ENABLED: "false",
            PaymentMethodSettingKeys.TITLE: "Direct Bank Transfer",
            PaymentMethodSettingKeys.DESCRIPTION: "Make your payment directly into our bank account. Please use your Order ID as the payment reference. Your order will not be shipped until the funds have cleared in our account.",
            PaymentMethodSettingKeys.ACCOUNT_NAME: "",
            PaymentMethodSettingKeys.ACCOUNT_NUMBER: "",
            PaymentMethodSettingKeys.BANK_NAME: "",
            PaymentMethodSettingKeys.SORT_CODE: "",
            PaymentMethodSettingKeys.IBAN: "",
            PaymentMethodSettingKeys.BIC_SWIFT: "",
        },
        PaymentMethods.CHECK: {
            PaymentMethodSettingKeys.ENABLED: "false",
            PaymentMethodSettingKeys.TITLE: "Check Payments",
            PaymentMethodSettingKeys.DESCRIPTION: "Please send a check to Store Name, Store Street, Store Town, Store State / County, Store Postcode.",
        },
        PaymentMethods.COD: {
            PaymentMethodSettingKeys.ENABLED: "false",
            PaymentMethodSettingKeys.TITLE: "Cash on Delivery",
            PaymentMethodSettingKeys.DESCRIPTION: "Pay with cash upon delivery.",
            PaymentMethodSettingKeys.ENABLE_FOR_SHIPPING: "",
            PaymentMethodSettingKeys.ACCEPT_VIRTUAL_ORDERS: "false",
        },
        PaymentMethods.GATEWAY: {
            PaymentMethodSettingKeys.ENABLED: "false",
            PaymentMethodSettingKeys.PROVIDER: "",
            PaymentMethodSettingKeys.BITPAY_API_KEY: "",
            PaymentMethodSettingKeys.FLUTTERWAVE_API_KEY: "",
            PaymentMethodSettingKeys.PAYSTACK_API_KEY: "",
        },
    }
    
    return DEFAULT_PAYMENT_SETTINGS


def get_active_payment_gateway() -> dict:
    """
    Retrieves the currently active payment gateway and its credentials.

    Returns:
        dict: Contains 'provider' and relevant credentials.
    """
    provider = get_payment_method_setting(PaymentMethods.GATEWAY, PaymentMethodSettingKeys.PROVIDER)
    
    if not provider:
        return {}

    credentials = {
        "api_key": get_payment_method_setting(PaymentMethods.GATEWAY, PaymentMethodSettingKeys(f"{provider.upper()}_API_KEY"))
    }

    return {"provider": provider, "credentials": credentials}
