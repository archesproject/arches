import importlib


def get_class_from_modulename(modulename, classname, directory_list):
    mod_path = modulename.replace(".py", "")
    module = None
    import_success = False
    import_error = None
    for directory in directory_list:
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
