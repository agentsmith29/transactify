import logging
import traceback
import asyncio
from rich.logging import RichHandler
from common.src.is_running_migration import is_running_migration

class LogDBHandler(logging.Handler):
    """
    Custom logging handler to log messages to the database and stdout.
    Supports both synchronous and asynchronous contexts, including threads.
    """
    def __init__(self):
        super().__init__()
        self.rich_handler = RichHandler()

    async def _log_to_db_async(self, record, traceback_obj=None):
        if is_running_migration():
            return
        from terminal.webmodels.StoreLogs import StoreLog
        await StoreLog.objects.acreate(
            loglevel=record.levelname,
            module=record.name,
            message=record.getMessage(),
            source_file=record.filename,
            source_line=record.lineno,
            traceback=traceback_obj
        )

    def _log_to_db_sync(self, record, traceback_obj=None):
        if is_running_migration():
            return
        from terminal.webmodels.StoreLogs import StoreLog
        StoreLog.objects.create(
            loglevel=record.levelname,
            module=record.name,
            message=record.getMessage(),
            source_file=record.filename,
            source_line=record.lineno,
            traceback=traceback_obj
        )

    async def _handle_traceback_async(self, record):
        if is_running_migration():
            return
        from terminal.webmodels.LogTraceback import LogTraceback
        return await LogTraceback.objects.acreate(
            traceback=traceback.format_exc(),
            line_no=record.lineno,
            file_name=record.filename
        )

    def _handle_traceback_sync(self, record):
        if is_running_migration():
            return
        from terminal.webmodels.LogTraceback import LogTraceback
        return LogTraceback.objects.create(
            traceback=traceback.format_exc(),
            line_no=record.lineno,
            file_name=record.filename
        )

    def emit(self, record: logging.LogRecord):
        # Ensure the current thread has an event loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:  # No event loop in the current thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # Schedule as a task if the event loop is running
            loop.create_task(self._emit_async(record))
        else:
            # Fallback to synchronous emit if no loop is running
            self._emit_sync(record)

    async def _emit_async(self, record: logging.LogRecord):
        traceback_obj = None
        record.name = f"{record.name} (async)"
        if record.levelno >= logging.ERROR:
            traceback_obj = await self._handle_traceback_async(record)
            
        try:
            await self._log_to_db_async(record, traceback_obj)
        except Exception as e:
            record.name = f"{record.name} (no DB)"
            print(f"Failed to log to database (async): {e}")

    def _emit_sync(self, record: logging.LogRecord):
        traceback_obj = None
        if record.levelno >= logging.ERROR:
            # on error append Line number and file name to the message
            traceback_obj = self._handle_traceback_sync(record)
            last_traceback_line = traceback_obj.traceback.splitlines()[-3:-1]
            record.msg = f"\nError on line {record.lineno} in {record.filename}:\n[E] {record.getMessage()}\n[TB] {last_traceback_line}"
        try:
            self._log_to_db_sync(record, traceback_obj)
        except Exception as e:
            record.name = f"{record.name} (no DB)"
            print(f"Failed to log to database (sync): {e}")
