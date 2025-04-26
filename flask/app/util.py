def str_to_bool(s):
    if isinstance(s, bool):
        return s
    elif isinstance(s, str) and s.lower() == 'true':
        return True
    elif isinstance(s, str) and s.lower() == 'false':
        return False
    else:
        raise ValueError(f"Cannot convert {s} to boolean")