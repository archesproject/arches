import importlib.util
import os
import sys
import codecs


def get_yn_input(msg="are you sure you want to continue?", default="Y"):
    """
    function can be passed a custom message and will use that prompt to get
    a y/n response. default defines what will happen if enter is hit with no
    input.
    """

    if default not in ["Y", "N"]:
        raise Exception("function must be called with default = 'Y' or 'N'")

    if default == "Y":
        o = input(msg + " [Y/n] ")
        if o.lower().startswith("y") or o == "":
            ret = True
        else:
            print("operation cancelled.")
            ret = False

    if default == "N":
        o = input(msg + " [y/N] ")
        if o.lower().startswith("n") or o == "":
            print("operation cancelled.")
            ret = False
        else:
            ret = True

    return ret


def write_to_file(fileName, contents, mode="w", encoding="utf-8", **kwargs):
    ensure_dir(fileName)
    file = codecs.open(fileName, mode=mode, encoding=encoding, **kwargs)
    file.write(contents)
    file.close()


def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)


def get_valid_path(path):
    """
    Takes a relative or absolute path and returns either an absolute path or
    None if the path is invalid.
    """
    result = None
    if os.path.exists(path) and os.path.isabs(path):
        result = path
    elif os.path.exists(os.path.join(os.getcwd(), path)):
        result = os.path.join(os.getcwd(), path)
    return result


def print_message(message):
    border = "*" * 80
    print("{1}\n{0}\n{1}".format(message, border))


def load_source(module_name, file_path):
    """Replacement for deprecated imp.load_source(). Recipe from
    https://docs.python.org/3.12/library/importlib.html#importlib.abc.Loader.exec_module
    """

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
