from django.views.generic import ListView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from ..webmodels.StoreLogs import StoreLog
from transactify_service.HttpResponses import HTTPResponses

from store import StoreLogsDBHandler

from django.core.paginator import Paginator
from django.shortcuts import render
import logging

from transactify_service.settings import CONFIG
import logging

@method_decorator(login_required, name='dispatch')
class StoreLogListView(ListView):
    model = StoreLog
    template_name = 'store/view_logs.html'
    context_object_name = 'logs'

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(f"{CONFIG.webservice.SERVICE_NAME}.webviews.{self.__class__.__name__}")
        super().__init__(**kwargs)

    
    def get_queryset(self):
        """Custom queryset to order logs by timestamp (most recent first)."""
        return StoreLog.objects.all().order_by('-timestamp')
    

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for various commands such as clearing logs or persisting data.
        """
        try:
            # Safely get the command header
            command = request.headers.get("cmd", "").lower()
        except Exception as e:
            response = HTTPResponses.HTTP_STATUS_JSON_PARSE_ERROR(e)
            data, status = response.json_data()
            return JsonResponse(data, status=status)
        
        try:
            if command == "clear_logs":
                # Clear all logs
                StoreLog.objects.all().delete()
                StoreLogListView.logger.warning(f"Logs cleared by user: {request.user.username}")
                response = HTTPResponses.HTTP_STATUS_LOG_CLEAR_SUCCESS()
                data, status = response.json_data()
                return JsonResponse(data, status=status)

            #elif command == "persist":
            #    # Placeholder for persist logic
            #    # Add your logic for persisting data here
            #    return JsonResponse({"status": "success", "message": "Data has been persisted successfully."})

            else:
                # Invalid command
                response = HTTPResponses.HTTP_STATUS_LOG_CLEAR_FAILED(f"Invalid command '{command}'")
                data, status = response.json_data()
                return JsonResponse(data, status=status)

        except Exception as e:
            # Encapsulate exception handling with HTTPResponses
            response = HTTPResponses.HTTP_STATUS_LOG_CLEAR_FAILED(e)
            data, status = response.json_data()
            return JsonResponse(data, status=status)
