from typing import Union, Any, Dict
from django.http import QueryDict


def str_to_bool(value):
    match value.lower():
        case "y" | "yes" | "t" | "true" | "on" | "1":
            return True
        case "n" | "no" | "f" | "false" | "off" | "0":
            return False
    raise ValueError


def get_str_kwarg_as_bool(
    key, request_dict: Union[Dict[str, Any], QueryDict], default: bool = False
) -> bool:
    value = request_dict.get(key, str(default))
    if isinstance(value, bool):
        return value
    return str_to_bool(str(value))
