import importlib

from arches.app.const import ExtensionType
from arches.app.models.system_settings import settings
from arches.settings_utils import list_arches_app_names


def get_module(path, modulename=""):
    module = importlib.machinery.SourceFileLoader(modulename, path).load_module()
    return module


def get_directories(extension_type: ExtensionType):
    arches_app_dirs = []
    for arches_app in list_arches_app_names():
        arches_app_dirs.append(f"{arches_app}.{extension_type.value}")
        arches_app_dirs.append(f"{arches_app}.pkg.extensions.{extension_type.value}")

    filtered_settings_dirs = [
        setting_dir
        for setting_dir in getattr(
            settings, extension_type.value.upper()[:-1] + "_LOCATIONS"
        )
        if setting_dir not in arches_app_dirs
    ]

    core_root_dir = f"arches.app.{extension_type.value}"
    if extension_type is ExtensionType.SEARCH_COMPONENTS:
        core_root_dir = core_root_dir.replace("search_components", "search.components")

    if core_root_dir in filtered_settings_dirs:
        filtered_settings_dirs.remove(core_root_dir)

    return arches_app_dirs + filtered_settings_dirs + [core_root_dir]


def get_class_from_modulename(modulename, classname, extension_type: ExtensionType):
    mod_path = modulename.replace(".py", "")
    module = None
    import_success = False
    import_error = None
    for directory in get_directories(extension_type):
        try:
            module = importlib.import_module(directory + ".%s" % mod_path)
        except ImportError as e:
            import_error = e
            continue
        try:
            func = getattr(module, classname)
            import_success = True
        except AttributeError as e:
            import_error = e
        if import_success:
            break
    if not import_success:
        raise import_error

    return func
