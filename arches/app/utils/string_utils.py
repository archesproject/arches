def str_to_bool(value):
    if value in ["y", "yes", "t", "true", "True", "on", "1"]:
        return True
    elif value in ["n", "no", "f", "false", "False", "off", "0"]:
        return False
    raise ValueError
