def int_else_float_except_string(s):
    try:
        f = float(s.replace(",", "."))
        if f.is_integer():
            try:
                return int(f)
            except (OverflowError, ValueError):
                return f
        return f
    except ValueError:
        return s


def get_attr(obj, key):
    """Get attribute from dict or struct."""
    if isinstance(obj, dict):
        return obj.get(key)
    else:
        return getattr(obj, key, None)


def has_attr(obj, key):
    """Check if attribute exists in dict or struct."""
    if isinstance(obj, dict):
        return key in obj
    else:
        return hasattr(obj, key)
