from django import template
from django.templatetags.static import static
from django.conf import settings

register = template.Library()

@register.simple_tag(takes_context=True)
def static_assets(context, path):
    """
    Custom tag to generate the full URL for static assets, including <ip>:<port>.
    Usage: {% assets 'icons/svg/database-add.svg' %}
    """
    request = context.get('request')  # Get the request object from the template context
    if not request:
        # If the request object is not available, fall back to STATIC_URL
        return f"{settings.STATIC_URL}{path}"
    
    # Construct the full URL using the request's host and port
    host = request.get_host()  # Includes <ip>:<port> from the request
    fixed_ip = "192.168.1.190"  # Replace with your fixed IP
    port = "8000"
    host = f"{fixed_ip}:{port}"
    return f"http://{host}/static/assets_hyper/{path}"
