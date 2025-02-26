import logging
from flask import current_app, has_app_context
from typing import Any

# Custom Formatter for dash-style logging
class DashFormatter(logging.Formatter):
    """Custom formatter that adds dashes around the label and message."""
    def format(self, record):
        # Extract the label from the message (assuming first part before colon)
        label, *rest = record.msg.split(":", 1) if ":" in record.msg else (record.msg, "")
        data = rest[0].strip() if rest else ""
        formatted_msg = f"\n\n{label:-^50}\n {data} \n{'//':-^50}\n\n"
        record.msg = formatted_msg
        return super().format(record)

# Initialize a fallback logger for non-Flask contexts (e.g., tests)
_fallback_logger = logging.getLogger(__name__)
if not _fallback_logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(DashFormatter("%(levelname)s: %(message)s"))
    _fallback_logger.addHandler(handler)
    _fallback_logger.setLevel(logging.INFO)


def console_log(label: str = "INFO", data: Any = None, level: str = "INFO") -> None:
    """
    Print a formatted message to the console for visual clarity.

    Args:
        label (str, optional): A label for the message, centered and surrounded by dashes. Defaults to 'INFO'.
        data: The data to be printed. Can be of any type. Defaults to None.
    """
    
    # Use Flask logger if in app context, otherwise fall back to a standalone logger
    if has_app_context():
        logger = current_app.logger
    else:
        logger = logging.getLogger(__name__)
        if not logger.handlers:  # Avoid duplicate handlers in tests
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
            logger.addHandler(handler)
        logger.setLevel(logging.INFO)  # Default level, adjustable
    
    getattr(logger, level.lower(), logger.info)(f"\n\n{label:-^50}\n {data} \n{'//':-^50}\n\n", stacklevel=2)


def log_exception(label: str ="EXCEPTION", data: Any = "Nothing") -> None:
    """
    Log an exception with details to a logging handler for debugging.

    Args:
        label (str, optional): A label for the exception, centered and surrounded by dashes. Defaults to 'EXCEPTION'.
        data: Additional data to be logged along with the exception. Defaults to 'Nothing'.
    """
    
    if has_app_context():
        logger = current_app.logger
    else:
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
            logger.addHandler(handler)
        logger.setLevel(logging.ERROR)  # Default to ERROR for exceptions
    
    logger.exception(f"\n\n{label:-^50}\n {str(data)} \n {'//':-^50}\n\n", stacklevel=2)