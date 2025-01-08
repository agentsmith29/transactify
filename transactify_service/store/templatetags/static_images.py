from django import template
from store.templatetags.static_assets import static_assets
from django.conf import settings

register = template.Library()

@register.simple_tag()
def static_images(path):
    """
    Custom tag to generate the full URL for static assets.
    Usage: {% static_assets 'icons/svg/database-add.svg' %}
    """
    # Delegate the URL construction to the `static` function
    static_url = static_assets(f"images/{path}")
    return static_url