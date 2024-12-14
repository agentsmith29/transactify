class HelperException(Exception):
    def __init__(self, message, response, base_exception=None):
        self.message = message
        self.response = response
        self.base_exception = base_exception
        super(HelperException, self).__init__(message)