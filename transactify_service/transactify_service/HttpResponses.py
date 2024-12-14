from rest_framework.response import Response
from rest_framework import status
from transactify_service.APIResponse import APIResponse

class HTTPResponses():
     
    # === Customer related responses (0-100) ===
    HTTP_STATUS_CUSTOMER_NOT_FOUND = lambda card_number: APIResponse.error(
                message = f"Customer with card number {card_number} does not exist.", 
                code=10,
                http_status=status.HTTP_404_NOT_FOUND)
    
    HTTP_STATUS_CUSTOMER_CREATE_FAILED = lambda username, error_msg: Response(
                {"error": f"Failed to create customer {username}: {error_msg}", "code": 11},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    HTTP_STATUS_GROUP_CREATE_FAILED = lambda group, error_msg: Response(
                {"error": f"Failed to create group {group}: {error_msg}", "code": 12},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    HTTP_STATUS_CUSTOMER_CREATE_SUCCESS = lambda username: Response(
                {"message": f"Customer {username} created successfully.", "code": 13},
                status=status.HTTP_200_OK
            )

    # === Product related responses (100-200) ===
    HTTP_STATUS_PRODUCT_NOT_FOUND =  lambda ean: Response(
                    {"error": f"Product with EAN {ean} does not exist.", "code": 100},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
    
    HTTP_STATUS_PRODUCT_STOCK_UPDATE_FAILED = lambda erro_msg: Response(
                    {"error": f"Error updating stock quantity: {erro_msg}", "code": 101},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    HTTP_STATUS_PRODUCT_CREATE_FAILED = lambda ean, error_msg: Response(
                {"error": f"Failed to create product with EAN {ean}: {error_msg}", "code": 102},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    HTTP_STATUS_PRODUCT_CREATE_SUCCESS = lambda ean: Response(
                {"message": f"Product with EAN {ean} created successfully.", "code": 103},
                status=status.HTTP_200_OK
            )

    # === Purchase related responses (200-300) ===
    HTTP_STATUS_INSUFFICIENT_BALANCE = lambda card_number, required, available: Response(
                    {"error": f"Insufficient balance for card_number. Required: {required}, Available: {available}",
                     "code": 200},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
    
    HTTP_STATUS_INSUFFICIENT_STOCK = lambda product_name, available, requested: Response(
                    {"warning": f"Insufficient stock for product {product_name}. Available: {available}, Requested: {requested}",
                     "code": 201},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
    
    HTTP_STATUS_PURCHASE_FAILED = lambda error_msg: Response(
                {"error": f"Purchase failed due to error: {error_msg}", "code": 202},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    HTTP_STATUS_PURCHASE_SUCCESS = lambda product_name: Response(
                {"message": f"Purchase of {product_name} successful.", "code": 203},
                status=status.HTTP_200_OK
            )

    # === Deposit related responses (300-400) ===
    HTTP_STATUS_UPDATE_BALANCE_FAILED = lambda customer, error_msg: Response(
                {"error": f"Failed to update balance for customer {customer}: {error_msg}", "code": 300},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    HTTP_STATUS_UPDATE_DEPOSIT_SUCCESS = lambda customer: Response(
                {"message": f"Deposit successfull. Balance update for customer {customer} successful.", "code": 301},
                status=status.HTTP_200_OK
            )
    
    HTTP_STATUS_UPDATE_DEPOSIT_FAILED = lambda error_msg: Response(
                {"error": f"Deposit failed. Failed to update balance: {error_msg}", "code": 302},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    HTTP_STATUS_BALANCE_MISMATCH = lambda customer: Response(
                {"error": f"Balance mismatch for customer {customer}", "code": 303},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    HTTP_STATUS_UPDATE_PURCHASE_SUCCESS = lambda customer: Response(
                {"message": f"Purchase successfull. Balance update for customer {customer} successful.", "code": 304},
                status=status.HTTP_200_OK
            )
    
    HTTP_STATUS_UPDATE_PURCHASE_FAILED = lambda error_msg: Response(
                {"error": f"Purchase failed Failed to update balance: {error_msg}", "code": 305},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    HTTP_STATUS_RESTOCK_FAILED = lambda error_msg: Response(
                {"error": f"Restock failed due to error: {error_msg}", "code": 306},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    HTTP_STATUS_RESTOCK_SUCCESS = lambda product_name: Response(
                {"message": f"Restock of {product_name} successful.", "code": 307},
                status=status.HTTP_200_OK
            )

    # === Generic responses (900) ===
    HTTP_STATUS_NOT_DECIAML = lambda field_name, field_type, error_msg: Response(
            {"error": f"Invalid data for {field_name}. Must be a decimal not {field_type}: Error: {error_msg}",
             "code": 900},
            status=status.HTTP_400_BAD_REQUEST
        )