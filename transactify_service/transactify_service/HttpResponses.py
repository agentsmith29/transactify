from rest_framework import status
from transactify_service.APIResponse import APIResponse

class HTTPResponses():

    # === Customer related responses (0-100) ===
    HTTP_STATUS_CUSTOMER_NOT_FOUND = lambda card_number: APIResponse.error(
        message=f"Customer with card number {card_number} does not exist.", 
        code=1,
        http_status=status.HTTP_404_NOT_FOUND
    )

    HTTP_STATUS_CUSTOMER_CREATE_FAILED = lambda username, error_msg: APIResponse.error(
        message=f"Failed to create customer {username}: {error_msg}",
        code=2,
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    HTTP_STATUS_GROUP_CREATE_FAILED = lambda group, error_msg: APIResponse.error(
        message=f"Failed to create group {group}: {error_msg}",
        code=12,
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    HTTP_STATUS_CUSTOMER_CREATE_SUCCESS = lambda username: APIResponse.success(
        message=f"Customer {username} created successfully.",
        code=0,
        http_status=status.HTTP_201_CREATED
    )
    HTTP_STATUS_CUSTOMER_DELETED = lambda username: APIResponse.success(
        message=f"Customer with card number {username} deleted", 
        code=4,
        http_status=status.HTTP_200_OK
    )

    HTTP_STATUS_CUSTOMER_DELETE_FAILED = lambda username, error_msg: APIResponse.error(
        message=f"Error while deleting customer with username {username} deleted: {error_msg}", 
        code=5,
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )




    # === Product related responses (100-200) ===
    HTTP_STATUS_PRODUCT_NOT_FOUND = lambda ean: APIResponse.error(
        message=f"Product with EAN {ean} does not exist.",
        code=100,
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    HTTP_STATUS_PRODUCT_STOCK_UPDATE_FAILED = lambda error_msg: APIResponse.error(
        message=f"Error updating stock quantity: {error_msg}",
        code=101,
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    HTTP_STATUS_PRODUCT_CREATE_FAILED = lambda ean, error_msg: APIResponse.error(
        message=f"Failed to create product with EAN {ean}: {error_msg}",
        code=101,
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    HTTP_STATUS_PRODUCT_CREATE_SUCCESS = lambda ean: APIResponse.success(
        message=f"Product with EAN {ean} created successfully.",
        code=103,
        http_status=status.HTTP_201_CREATED
    )

    HTTP_STATUS_PRODUCT_UPDATE_SUCCESS = lambda ean: APIResponse.success(
        message=f"Product with EAN {ean} updated successfully.",
        code=104,
        http_status=status.HTTP_200_OK
    )

    HTTP_STATUS_INSUFFICIENT_BALANCE = lambda card_number, required, available: APIResponse.error(
        message=f"Insufficient balance for card number. Required: {required}, Available: {available}",
        code=105,
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    HTTP_STATUS_INSUFFICIENT_STOCK = lambda product_name, available, requested: APIResponse.error(
        message=f"Insufficient stock for product {product_name}. Available: {available}, Requested: {requested}",
        code=106,
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    HTTP_STATUS_PURCHASE_FAILED = lambda error_msg: APIResponse.error(
        message=f"Purchase failed due to error: {error_msg}",
        code=107,
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    HTTP_STATUS_PURCHASE_SUCCESS = lambda product_name: APIResponse.success(
        message=f"Purchase of {product_name} successful.",
        code=108,
        http_status=status.HTTP_200_OK
    )

    HTTP_STATUS_UPDATE_BALANCE_FAILED = lambda customer, error_msg: APIResponse.error(
        message=f"Failed to update balance for customer {customer}: {error_msg}",
        code=109,
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    HTTP_STATUS_UPDATE_DEPOSIT_SUCCESS = lambda customer: APIResponse.success(
        message=f"Deposit successful. Balance update for customer {customer} successful.",
        code=110,
        http_status=status.HTTP_200_OK
    )

    HTTP_STATUS_UPDATE_DEPOSIT_FAILED = lambda error_msg: APIResponse.error(
        message=f"Deposit failed. Failed to update balance: {error_msg}",
        code=111,
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    HTTP_STATUS_BALANCE_MISMATCH = lambda customer: APIResponse.error(
        message=f"Balance mismatch for customer {customer}",
        code=112,
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    HTTP_STATUS_UPDATE_PURCHASE_SUCCESS = lambda customer: APIResponse.success(
        message=f"Purchase successful. Balance update for customer {customer} successful.",
        code=113,
        http_status=status.HTTP_200_OK
    )

    HTTP_STATUS_UPDATE_PURCHASE_FAILED = lambda error_msg: APIResponse.error(
        message=f"Purchase failed. Failed to update balance: {error_msg}",
        code=114,
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    HTTP_STATUS_RESTOCK_FAILED = lambda error_msg: APIResponse.error(
        message=f"Restock failed due to error: {error_msg}",
        code=115,
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    HTTP_STATUS_RESTOCK_SUCCESS = lambda product_name: APIResponse.success(
        message=f"Restock of {product_name} successful.",
        code=116,
        http_status=status.HTTP_201_CREATED
    )

    # === Log Respnses ===
    HTTP_STATUS_LOG_CLEAR_FAILED = lambda error_msg: APIResponse.error(
        message=f"Failed to clear logs: {error_msg}",
        code=115,
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    HTTP_STATUS_LOG_CLEAR_SUCCESS = lambda: APIResponse.success(
        message=f"Clear logs successfuly.",
        code=116,
        http_status=status.HTTP_200_OK
    )


    # === Generic responses (900) ===
    HTTP_STATUS_NOT_DECIMAL = lambda field_name, field_type, error_msg: APIResponse.error(
        message=f"Invalid data for {field_name}. Must be a decimal not {field_type}: Error: {error_msg}",
        code=900,
        http_status=status.HTTP_400_BAD_REQUEST
    )

    HTTP_STATUS_JSON_PARSE_ERROR = lambda error_msg: APIResponse.error(
        message=f"Error parsing JSON data: {error_msg}",
        code=901,
        http_status=status.HTTP_400_BAD_REQUEST
    )
