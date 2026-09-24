import os

#: Root of this application's test package. Some CLI tests write export
#: artifacts here before reading them back.
PROJECT_TEST_ROOT = os.path.dirname(os.path.abspath(__file__))

#: An Arches package used by the CLI and view tests to load reference data.
TEST_PACKAGE_DIR = os.path.join(PROJECT_TEST_ROOT, "fixtures", "pkg")

#: Directory of the application under test. arches' own test settings set
#: APP_ROOT to "", so tests that need the application's own files on disk --
#: the ETL module registration tests, for instance -- resolve from here.
import arches.extensions.controlled_lists as _controlled_lists

APP_ROOT = os.path.dirname(os.path.abspath(_controlled_lists.__file__))
