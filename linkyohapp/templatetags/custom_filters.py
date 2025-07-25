from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to access dictionary values by key.
    Usage: {{ my_dict|get_item:key_variable }}
    """
    return dictionary.get(key, 0)  # Return 0 if key doesn't exist