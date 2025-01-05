from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView
from django.shortcuts import redirect
import store.StoreLogsDBHandler  # Import your custom logging handler

# Setup the logger



class LoginView(BaseLoginView):
    template_name = 'login.html'
    logger = store.StoreLogsDBHandler.setup_custom_logging('LoginView')

    def form_valid(self, form):
        """Log a message when the user logs in successfully, including IP address."""
        user = form.get_user()
        ip_address = self.get_client_ip()
        LoginView.logger.info(f"User {user.username} logged in from IP {ip_address}.")
        return super().form_valid(form)

    def get_client_ip(self):
        """Extract the client's IP address from the request."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class LogoutView(BaseLogoutView):
    logger = store.StoreLogsDBHandler.setup_custom_logging('LogoutView')

    def dispatch(self, request, *args, **kwargs):
        """Log a message when the user logs out, including IP address."""
        if request.user.is_authenticated:
            ip_address = self.get_client_ip(request)
            LogoutView.logger.info(f"User {request.user.username} logged out from IP {ip_address}.")
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def get_client_ip(request):
        """Extract the client's IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
