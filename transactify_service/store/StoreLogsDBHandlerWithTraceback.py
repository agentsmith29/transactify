import logging
import traceback
from rich.logging import RichHandler
import sys

class StoreLogsDBHandler(logging.Handler):
    """
    Custom logging handler to log messages to the database and stdout.
    """
    def __init__(self):
        super().__init__()
        self.rich_handler = RichHandler()

    def emit(self, record):
        from .webmodels.StoreLogs import StoreLog
        try:
            # Log to database
            StoreLog.objects.create(
                loglevel=record.levelname,
                module=record.name,
                message=record.getMessage(),
                traceback=getattr(record, "traceback", None)  # Save traceback if present
            )
        except Exception as e:
            # Alter the message to include the error
            record.name = f"{record.name} (no DB)"
            # Fail gracefully if database logging fails
            print(f"Failed to log to database: {e}")


class CustomLogger(logging.Logger):
    """
    Custom logger to extend the error method to capture tracebacks.
    """
    def error(self, msg, *args, exc_info=True, **kwargs):
        if exc_info:
            # Capture the exception information and generate the traceback
            exc_type, exc_value, exc_traceback = exc_info if isinstance(exc_info, tuple) else (None, None, None)
            if exc_type is None:
                exc_type, exc_value, exc_traceback = sys.exc_info()

            # Format the traceback
            formatted_traceback = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            # Pass the traceback as an extra field to the log record
            kwargs["extra"] = kwargs.get("extra", {})
            kwargs["extra"]["traceback"] = formatted_traceback

        # Call the parent class's error method
        super().error(msg, *args, exc_info=exc_info, **kwargs)


def setup_custom_logging(name):
    """Sets up the custom logging handler."""
    logging.setLoggerClass(CustomLogger)  # Use the custom logger class
    logger = logging.getLogger(name)  # Create a new logger
    logger.setLevel(logging.DEBUG)

    db_handler = StoreLogsDBHandler()
    db_handler.setLevel(logging.DEBUG)

    # Add the handler to the logger
    logger.addHandler(db_handler)
    return logger
