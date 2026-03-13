from django import template

register = template.Library()

@register.filter
def get_item(cart, key):
    if isinstance(cart, dict):
        return cart.get(str(key), 0)
    return 0
