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
