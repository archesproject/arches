import json
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


def deserialize_json_like_string(val, depth=2):
    """
    Takes string intended as JSON that cannot be deserialized to a dictionary by `json.loads`
    and returns a dictionary. If a string uses single quotes around keys and values
    e.g. "{'foo':'bar'}", these are converted to double quotes. If a string has escaped
    quotes e.g. "[{\\"foo\\":\\"bar\\"}]", these are recursively deserialized until `json.loads`
    returns a dictionary. This function serves as a more secure alternative to `ast.literal_eval`.
    """
    if isinstance(val, str) and depth >= 0:
        if val.replace(" ", "").startswith("{'") or val.replace(" ", "").startswith(
            "[{'"
        ):
            val = val.replace("'", '"')
        res = json.loads(val)
        return deserialize_json_like_string(res, depth=depth - 1)
    return val
