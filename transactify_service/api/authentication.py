from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from store.webmodels.APIKey import APIKey

class APIKeyAuthentication(BaseAuthentication):
    """
    Custom authentication class for API key-based access.
    """
    def authenticate(self, request):
        api_key = request.headers.get('Authorization')
        if not api_key:
            return None  # No API key provided, let DRF handle it as unauthenticated

        # Validate API key
        try:
            key = api_key.split(" ")[1]  # Expect "Bearer <API_KEY>"
            api_key_obj = APIKey.objects.get(key=key)
            return (api_key_obj.user, None)
        except (IndexError, APIKey.DoesNotExist):
            raise AuthenticationFailed('Invalid or missing API key.')
