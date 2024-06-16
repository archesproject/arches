import importlib

from arches.app.const import ExtensionType
from arches.app.models.system_settings import settings


def get_module(path, modulename=""):
    module = importlib.machinery.SourceFileLoader(modulename, path).load_module()
    return module


def get_directories(extension_type: ExtensionType):
    core_root_dir = f"arches.app.{extension_type.value}"
    if extension_type is ExtensionType.SEARCH_COMPONENTS:
        core_root_dir = core_root_dir.replace("search_components", "search.components")

    core_and_arches_app_dirs = [core_root_dir]
    for arches_app in settings.ARCHES_APPLICATIONS:
        core_and_arches_app_dirs.append(f"{arches_app}.{extension_type.value}")
        core_and_arches_app_dirs.append(
            f"{arches_app}.pkg.extensions.{extension_type.value}"
        )

    filtered_settings_dirs = [
        setting_dir
        for setting_dir in getattr(
            settings, extension_type.value.upper()[:-1] + "_LOCATIONS"
        )
        if setting_dir not in core_and_arches_app_dirs
    ]

    return core_and_arches_app_dirs + filtered_settings_dirs


def get_class_from_modulename(modulename, classname, extension_type: ExtensionType):
    mod_path = modulename.replace(".py", "")
    module = None
    import_success = False
    import_error = None
    for directory in get_directories(extension_type):
        try:
            module = importlib.import_module(directory + ".%s" % mod_path)
            import_success = True
        except ImportError as e:
            import_error = e
        if module is not None:
            break
    if import_success == False:
        print("Failed to import " + mod_path)
        print(import_error)

    func = getattr(module, classname)
    return func
