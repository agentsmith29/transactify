# INherited static tag from django/templatetags/static.py
from django import template
from django.templatetags.static import static
from django.conf import settings
from config.Config import Config as Config

register = template.Library()

@register.simple_tag()
def static2(path):

    config: Config  = settings.CONFIG
    static_webserver = config.django.STATIC_WEBSERVER
    if  static_webserver and static_webserver != "":
        return f"{static_webserver}{static(path)}"
    return static(path)