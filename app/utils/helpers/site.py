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
        }
    except Exception as e:
        log_exception("An exception occurred getting site information")
        raise e
    
    return info