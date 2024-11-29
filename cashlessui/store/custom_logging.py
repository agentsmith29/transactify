import logging
from rich.logging import RichHandler


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
            # Log to stdout using RichHandler
            self.rich_handler.emit(record)

            # Log to database
            StoreLog.objects.create(
                loglevel=record.levelname,
                module=record.name,
                message=record.getMessage()
            )
        except Exception as e:
            # Fail gracefully if database logging fails
            print(f"Failed to log to database: {e}")


def setup_custom_logging():
    """Sets up the custom logging handler."""
    logger = logging.getLogger('store')  # Create a new logger
    logger.setLevel(logging.DEBUG)

    db_handler = StoreLogsDBHandler()
    db_handler.setLevel(logging.DEBUG)

    # Add the handler to the logger
    logger.addHandler(db_handler)
    logger.info("Custom logging has been initialized.")