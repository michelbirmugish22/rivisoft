
#Filtre personnalisé pour effectuer la multiplication sur la template
from django import template
register = template.Library()
@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''
    
