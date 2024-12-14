import requests

class APIFetchException(Exception):
    def __init__(self,message, base_exception: Exception, response: requests.Response, traceback=None):
        super().__init__(message)
        self.base_exception = base_exception
        self.response = response
        # Extract the HTTP status code and server error code/message
        self.http_code = self.response.status_code
        self.server_error_code = self.response.json().get("code")
        self.server_error_message = self.response.json().get("error")
        self.traceback = traceback
