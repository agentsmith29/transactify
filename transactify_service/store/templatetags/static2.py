from django import template
from django.templatetags.static import static
from django.conf import settings
from urllib.parse import urlparse
from config.Config import Config
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def static2(context, path):
    request = context.get('request')
    config: Config = settings.CONFIG
    static_webserver = config.django.STATIC_WEBSERVER
    
    if static_webserver and static_webserver.strip():
        static_webserver = static_webserver.rstrip('/')  # Remove trailing slash if present
        static_url = static(path)
        
        if request:
            request_host = f"{request.scheme}://{request.get_host()}"
            request_port = request.get_port()
            request_host = f"{request_host}:{request_port}" if request_port else request_host
        
            
            if request_host == static_webserver:
                return mark_safe(static_url)  # Return relative path if host matches
        
        return mark_safe(f"{static_webserver}{static_url}")
    
    return mark_safe(static(path))
