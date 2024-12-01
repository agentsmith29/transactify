import logging

logger = logging.getLogger(__name__)

class DebugCSRFMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.debug("Incoming CSRF token (header): %s", request.META.get('HTTP_X_CSRFTOKEN'))
        logger.debug("Incoming CSRF token (cookie): %s", request.COOKIES.get('csrftoken'))
        response = self.get_response(request)
        return response
