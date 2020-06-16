def setup_package():
    from .base_test import setUpTestPackage

    setUpTestPackage()


def teardown_package():
    from .base_test import tearDownTestPackage

    tearDownTestPackage()
