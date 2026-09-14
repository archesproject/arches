import os

#: Root of this application's test package. Some CLI tests write export
#: artifacts here before reading them back.
PROJECT_TEST_ROOT = os.path.dirname(os.path.abspath(__file__))

#: An Arches package used by the CLI and view tests to load reference data.
TEST_PACKAGE_DIR = os.path.join(PROJECT_TEST_ROOT, "fixtures", "pkg")
