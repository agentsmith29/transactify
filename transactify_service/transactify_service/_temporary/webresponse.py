from transactify_service.transactify_service.HttpResponses import HTTPResponses
from rest_framework import status
from rest_framework.response import Response
import logging
import traceback

class WebResponse(Response):

    def json_data(self):
        return self.data, self.status_code

class APIResponse:
    """
    Utility class to construct custom API responses with internal codes and HTTP status.
    """

    @staticmethod
    def success(data=None, message="Success", code=0, http_status=200, as_json=True):
        """
        Constructs a success response.

        Args:
            data (dict): The main response payload.
            message (str): A message describing the response.
            code (int): Internal status code (0-999, default: 0).
            http_status (int): HTTP status code (default: 200).

        Returns:
            Response: A DRF Response object.
        """
        return WebResponse(
            {
                "data": data if data is not None else {},
                "message": message,
                "code": code,
                "success": True
            },
            status=http_status,
        )
    

    @staticmethod
    def error(message="Error", code=999, http_status=400, data=None):
        """
        Constructs an error response.

        Args:
            message (str): A message describing the error.
            code (int): Internal status code (0-999, default: 1).
            http_status (int): HTTP status code (default: 400).
            data (dict): Additional error details.

        Returns:
            Response: A DRF Response object.
        """
        return WebResponse(
            {
                "data": data if data is not None else {},
                "message": message,
                "code": code,
                "success": False
            },
            status=http_status,
        )


class HelperException(Exception):
    def __init__(self, message: str, response: APIResponse, logger:logging.Logger, base_exception=None, *args, **kwargs):
        logger.error(message, exc_info=True)
        self.traceback = traceback
        self.message = message
        # pass the arguments to the response object
        self.response = response(*args, **kwargs, error_msg=message)
        self.base_exception = base_exception
        super(HelperException, self).__init__(message)



HTTP_STATUS_UPDATE_BALANCE_FAILED = lambda customer, error_msg: APIResponse.error(
    message=f"Failed to update balance for customer {customer}: {error_msg}",
    code=109,
    http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
)

customer = Customer()
error_msg = f"Invalid deposit amount for customer {customer}"

HelperException(error_msg, 
                HTTPResponses.HTTP_STATUS_UPDATE_BALANCE_FAILED,
                # additional *args and **kwargs used for 
                customer = customer,
                )