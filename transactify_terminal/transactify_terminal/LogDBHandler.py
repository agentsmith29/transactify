import logging
from rich.logging import RichHandler


class LogDBHandler(logging.Handler):
    """
    Custom logging handler to log messages to the database and stdout.
    """
    def __init__(self):
        super().__init__()
        self.rich_handler = RichHandler()

    def emit(self, record):
        from terminal.webmodels.StoreLogs import StoreLog
        try:
            # Log to database
            StoreLog.objects.create(
                loglevel=record.levelname,
                module=record.name,
                message=record.getMessage()
            )
        except Exception as e:
            # alter the message to include the error
            record.name = f"{record.name} (no DB)"
            #print(f"Messsage: {record.message}")
            # Fail gracefully if database logging fails
            #print(f"Failed to log to database: {e}")

def setup_custom_logging(name):
    """Sets up the custom logging handler."""
    logger = logging.getLogger(name)  # Create a new logger
    logger.setLevel(logging.DEBUG)

    db_handler = StoreLogsDBHandler()
    db_handler.setLevel(logging.DEBUG)

    # Add the handler to the logger
    logger.addHandler(db_handler)
    return logger