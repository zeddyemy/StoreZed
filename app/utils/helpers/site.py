from .settings import get_general_setting
from .loggers import log_exception


def get_site_info() -> dict[str, str]:
    """
    Returns basic site information from settings.
    """
    try:
        info = {
            "site_name": get_general_setting("site_title", "My Store"),
            "site_tagline": get_general_setting("tagline", ""),
            "currency": get_general_setting("currency", "NGN"),
            "platform_url": get_general_setting("platform_url"),
            "site_url": get_general_setting("site_url"),
        }
    except Exception as e:
        log_exception("An exception occurred getting site information")
        raise e
    
    return info

def get_platform_url() -> str:
    """
    Return URL from General settings
    """
    return get_general_setting("platform_url", "https://defaultplatform.com")


def get_site_url() -> str:
    """
    Return URL from General settings
    """
    return get_general_setting("site_url", "https://defaultsite.com")

