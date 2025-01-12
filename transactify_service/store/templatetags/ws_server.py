from django import template
from django.templatetags.static import static
from django.conf import settings
from config.Config import Config as Config

register = template.Library()

@register.simple_tag()
def ws_server():
    # Check if a valid url outherwise convert it
    config: Config  = settings.CONFIG
    return  config.terminal.TERMINAL_WEBSOCKET_URL
