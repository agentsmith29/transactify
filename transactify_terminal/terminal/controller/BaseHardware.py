import logging
import threading
from transactify_terminal.settings import CONFIG

class BaseHardware():

    def __init__(self, thread_disabled=False, max_restarts=3):
        self.global_config = CONFIG
        self.logger = logging.getLogger(f"{CONFIG.webservice.SERVICE_NAME}.{self.__class__.__name__}")  
        self.is_initialized = False

        # Thread Management
        self.reading = True  # Control flag for reading process

        self.max_restarts = max_restarts
        

        
        self._thread: threading.Thread = None
        if thread_disabled:
            self.thread_disabled = thread_disabled
            self.restart_counter = 3    # in case, something automatically tries to start the thread
            self.abort_thread = True
        else:
            self.thread_disabled = False
            self.restart_counter = 0
            self.abort_thread = False
           

    @property
    def thread(self):
        return self._thread
    
    def start_thread(self):
        if self.thread and self.thread.is_alive():
            self.logger.debug(f"Thread already running for {self.__class__.__name__}")
            return False
        self.abort_thread = False

        if self.thread_disabled:
            self.logger.debug(f"Thread disabled for {self.__class__.__name__}")
            return False
        
        self.logger.info(f"Creating a new thread for {self.__class__.__name__}")
        return True
    
    def stop_thread(self):
        """Stop the NFC reading thread."""
        self.logger.debug(f"Requesting to stop thread for {self.__class__.__name__}")
        self.reading = False
        if self.thread and self.thread.is_alive():
            self.thread.join()  # Wait for the thread to finish
        self.logger.info(f"Hardware thread stopped for {self.__class__.__name__}")

    def run(self):
        raise NotImplementedError("The run method must be implemented in the subclass.")
    
    def setup():
        raise NotImplementedError("The setup method must be implemented in the subclass.")
    
    def run_thread(self):
        try:
           self.setup()
        except Exception as e:
            self.logger.error(f"Error initializing {self.__class__.__name__}: {e}")
            return
        
        while not self.abort_thread:
            try:
                self.run()
            except Exception as e:
                self.logger.error(f"Error running {self.__class__.__name__}: {e}")
                return
        
        self.logger.info(f"Thread for {self.__class__.__name__} stopped.")
        try:
            self.cleanup()
        except Exception as e:
            self.logger.error(f"Error cleaning up {self.__class__.__name__}: {e}")
            return

    def cleanup(self):
        self.logger.info(f"Cleaning up {self.__class__.__name__}")
        self.stop_thread()
        self.abort_thread = True

    def _check_if_initialized(func):
        def wrapper(self: BaseHardware, *args, **kwargs):
            if not self.is_initialized:
                self.logger.warning(f"{self.__class__.__name__} not initialized. Returning.")
                return
            return func(self, *args, **kwargs)
        return wrapper