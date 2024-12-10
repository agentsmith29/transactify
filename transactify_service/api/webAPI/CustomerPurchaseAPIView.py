from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status



from store.webmodels.Customer import Customer
from store.helpers.ManageStockHelper import ManageStockHelper
import json

class CustomerPurchaseAPIView(APIView):
    def post(self, request, *args, **kwargs):
        """
        Handle a customer purchase request.
        """
        try:
            data = json.loads(request.body)
            # we receive json data no post data
            ean = data.get('ean')
            quantity = data.get('quantity')
            card_number = data.get('card_number')
        except Exception as e:
            print(f"Error: {e}")
            print(f"Request: {request}")
            return Response(
                {"error": f"Invalid data format for {request}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate required fields
        if not all([ean, quantity, card_number]):
            return Response(
                {"error": "All fields (ean, quantity, sale_price, customer) are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            quantity = int(quantity)
        except Exception as e:
            return Response(
                {"error": f"Invalid data for quantity. Must be an integer but was {type(quantity)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        #try:
            # Assuming ManageStockHelper handles the logic for the purchase
        response, customer, customer_balance, product, purchase_entry = ManageStockHelper.customer_purchase(ean, quantity, card_number)
        #except Exception as e:
        #    return Response(
        #        {"error": "Product with the given EAN does not exist."},
        #        status=status.HTTP_404_NOT_FOUND,
        #    )

        return response
