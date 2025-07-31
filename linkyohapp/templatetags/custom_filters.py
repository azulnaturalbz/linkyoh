from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to access dictionary values by key.
    Usage: {{ my_dict|get_item:key_variable }}
    """
    return dictionary.get(key, 0)  # Return 0 if key doesn't exist


# ---------------------------------------------------------------------------
# Icon mapping utilities
# ---------------------------------------------------------------------------


ICON_MAPPING = {
    # Generic business & service related icons – extend as needed.
    # Keys are lower-cased category names for easier matching.
    "plumbing": "fa-solid fa-wrench",
    "plumber": "fa-solid fa-wrench",
    "electrical": "fa-solid fa-bolt",
    "electrician": "fa-solid fa-bolt",
    "cleaning": "fa-solid fa-broom",
    "paint": "fa-solid fa-paint-roller",
    "painting": "fa-solid fa-paint-roller",
    "carpentry": "fa-solid fa-hammer",
    "carpenter": "fa-solid fa-hammer",
    "mechanic": "fa-solid fa-car",
    "automotive": "fa-solid fa-car",
    "delivery": "fa-solid fa-truck",
    "landscaping": "fa-solid fa-tree",
    "gardening": "fa-solid fa-seedling",
    "it": "fa-solid fa-laptop-code",
    "tech": "fa-solid fa-laptop-code",
    "hair": "fa-solid fa-scissors",
    "beauty": "fa-solid fa-spa",
    "photography": "fa-solid fa-camera",
    "photo": "fa-solid fa-camera",
    "construction": "fa-solid fa-hard-hat",
    "tutoring": "fa-solid fa-chalkboard-user",
    "legal": "fa-solid fa-scale-balanced",
    "marketing": "fa-solid fa-bullhorn",
    "design": "fa-solid fa-pen-nib",
    "music": "fa-solid fa-music",
    "fitness": "fa-solid fa-dumbbell",
    "health": "fa-solid fa-heart-pulse",
    "consulting": "fa-solid fa-user-tie",
    "housing & construction": "fa-solid fa-building",
    "autos": "fa-solid fa-car",
    "pets": "fa-solid fa-paw",
    "services": "fa-solid fa-tools",
    "food": "fa-solid fa-utensils",
}


@register.filter(name="get_icon_class")
def get_icon_class(category_obj):
    """Return a Font Awesome class for the given category object.

    The function tries to find a sensible default icon by looking up the
    category name (and its *short* variant) in a predefined mapping. If no
    specific mapping is available it falls back to a generic tag icon so the
    UI never breaks.
    """

    name_candidates = []

    # Handle both Category instance and raw string gracefully – this allows
    # the filter to be used with either.
    if hasattr(category_obj, "category"):
        # Full category name
        name_candidates.append(str(category_obj.category))
        # Short category (if provided)
        short_val = getattr(category_obj, "short_category", None)
        if short_val:
            name_candidates.append(str(short_val))
    else:
        # Fallback to treating the argument as a plain string
        name_candidates.append(str(category_obj))

    for name in name_candidates:
        key = name.lower().strip()
        if key in ICON_MAPPING:
            return ICON_MAPPING[key]

    # Default when no explicit mapping was found.
    return "fa-solid fa-tag"
