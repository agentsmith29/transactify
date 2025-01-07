from django import template
from django.templatetags.static import static
from django.conf import settings

register = template.Library()

@register.simple_tag()
def ws_server():
    # Check if a valid url outherwise convert it
    terminal_url = settings.TERMINAL_SERVICES
    if terminal_url.startswith('http'):
        return f"{terminal_url}/ws".replace('http://', 'ws://').replace('https://', 'wss://')
    else:
        return f"ws://{terminal_url}/ws"
