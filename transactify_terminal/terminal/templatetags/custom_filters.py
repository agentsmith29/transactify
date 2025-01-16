# your_app/templatetags/custom_filters.py
import re
from django import template

register = template.Library()

@register.filter
def regex_match(value, pattern):
    return bool(re.match(pattern, value))

@register.filter
def multiply(value, arg):
    return value * arg