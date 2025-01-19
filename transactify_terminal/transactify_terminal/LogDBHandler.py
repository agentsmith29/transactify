import logging
import traceback
import asyncio
from rich.logging import RichHandler
from transactify_terminal.settings import CONFIG

class LogDBHandler(logging.Handler):
    """
    Custom logging handler to log messages to the database and stdout.
    Supports both synchronous and asynchronous contexts.
    """
    def __init__(self):
        super().__init__()
        self.rich_handler = RichHandler()
        self.logger = logging.getLogger(f"{CONFIG.webservice.SERVICE_NAME}.LogDBHandler")

    async def _log_to_db_async(self, record, traceback_obj=None):
        from terminal.webmodels.StoreLogs import StoreLog
        await StoreLog.objects.acreate(
            loglevel=record.levelname,
            module=record.name,
            message=record.getMessage(),
            traceback=traceback_obj
        )

    def _log_to_db_sync(self, record, traceback_obj=None):
        from terminal.webmodels.StoreLogs import StoreLog
        StoreLog.objects.create(
            loglevel=record.levelname,
            module=record.name,
            message=record.getMessage(),
            traceback=traceback_obj
        )

    async def _handle_traceback_async(self, record):
        from terminal.webmodels.LogTraceback import LogTraceback
        return await LogTraceback.objects.acreate(
            traceback=traceback.format_exc(),
            line_no=record.lineno,
            file_name=record.filename
        )

    def _handle_traceback_sync(self, record):
        from terminal.webmodels.LogTraceback import LogTraceback
        return LogTraceback.objects.create(
            traceback=traceback.format_exc(),
            line_no=record.lineno,
            file_name=record.filename
        )

    def emit(self, record):
        if asyncio.iscoroutinefunction(self._emit_async):
            asyncio.run(self._emit_async(record))
        else:
            self._emit_sync(record)

    async def _emit_async(self, record):
        traceback_obj = None
        if record.levelno >= logging.ERROR:
            traceback_obj = await self._handle_traceback_async(record)
        try:
            await self._log_to_db_async(record, traceback_obj)
        except Exception as e:
            record.name = f"{record.name} (no DB)"
            print(f"Failed to log to database: {e}")

    def _emit_sync(self, record):
        traceback_obj = None
        if record.levelno >= logging.ERROR:
            traceback_obj = self._handle_traceback_sync(record)
        try:
            self._log_to_db_sync(record, traceback_obj)
        except Exception as e:
            record.name = f"{record.name} (no DB)"
            print(f"Failed to log to database: {e}")


def setup_custom_logging(name):
    """Sets up the custom logging handler."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    db_handler = LogDBHandler()
    db_handler.setLevel(logging.DEBUG)

    # Add the handler to the logger
    logger.addHandler(db_handler)
    return logger
