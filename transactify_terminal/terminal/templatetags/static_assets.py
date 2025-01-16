from django import template
from django.conf import settings
from django.template.defaulttags import register
from terminal.templatetags.static2 import static2 as static
from config.Config import Config as Config

register = template.Library()



@register.simple_tag()
def static_assets(path):
    """
    Custom tag to generate the full URL for static assets.
    Usage: {% static_assets 'icons/svg/database-add.svg' %}
    """
    config: Config  = settings.CONFIG
    assets_path = config.django.STATIC_ASSETS_PATH
    # Delegate the URL construction to the `static` function
    static_url = static(f"{assets_path}{path}")
    return static_url

