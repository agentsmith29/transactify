from rest_framework.response import Response

from rest_framework.views import exception_handler
from rest_framework import status

from django.http import JsonResponse


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
                'status': 'success'
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
                'status': 'error'
            },
            status=http_status,
        )


def custom_exception_handler(exc, context):
    """
    Custom exception handler to format error responses using APIResponse.error.
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Extract the default status code and error detail
        status_code = response.status_code
        default_message = response.data.get('detail', str(exc))

        # Customize the response using APIResponse.error
        return APIResponse.error(
            message=default_message,
            code=status_code,
            http_status=status_code,
        )

    # Handle unexpected exceptions
    return APIResponse.error(
        message="An unexpected error occurred.",
        code=500,
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
