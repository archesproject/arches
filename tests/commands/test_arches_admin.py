import os
import sys
import shutil
import subprocess
import tempfile
from django.test import SimpleTestCase


class ArchesAdminTestCase(SimpleTestCase):
    def run_test(self, args, settings_file=None, umask=-1, cwd=None):
        base_dir = os.path.dirname(self.test_dir)
        tests_dir = os.path.dirname(os.path.dirname(__file__))
        # The repo root (one level above the tests dir) must be on PYTHONPATH
        # so that `import arches` resolves to the local source tree.
        arches_dir = os.path.dirname(tests_dir)

        test_environ = os.environ.copy()

        if settings_file:
            test_environ["DJANGO_SETTINGS_MODULE"] = settings_file
        elif "DJANGO_SETTINGS_MODULE" in test_environ:
            del test_environ["DJANGO_SETTINGS_MODULE"]

        python_path = [base_dir, arches_dir, tests_dir]
        test_environ["PYTHONPATH"] = os.pathsep.join(python_path)
        test_environ["PYTHONWARNINGS"] = ""

        process = subprocess.run(
            [sys.executable, *args],
            capture_output=True,
            cwd=cwd or self.test_dir,
            env=test_environ,
            text=True,
            umask=umask,
        )
        return process.stdout, process.stderr

    def run_arches_admin(self, args, settings_file=None, umask=-1, cwd=None):
        return self.run_test(
            ["-m", "arches.install.arches_admin", *args],
            settings_file,
            umask=umask,
            cwd=cwd,
        )


class ArchesAdminCommandTests(ArchesAdminTestCase):
    test_dir = os.path.dirname(__file__)

    def test_help(self):
        stdout, stderr = self.run_arches_admin(["--help"])
        self.assertIn("startproject", stdout)

    def test_startproject_uses_kebab_case_directory(self):
        """
        When a project name contains underscores, `arches-admin startproject`
        should create the top-level project directory using the kebab-case
        equivalent of the name (underscores replaced with hyphens), while
        the inner Python package retains the original snake_case name.

        `arches-admin startproject my_project --yes` should produce:
            my-project/          <- top-level directory (kebab-case)
                my_project/      <- inner Python package (snake_case)
                ...
        """
        project_name = "my_project"
        expected_top_level_dir = "my-project"

        temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, temp_dir, ignore_errors=True)

        self.run_arches_admin(
            ["startproject", project_name, "--yes"],
            cwd=temp_dir,
        )

        top_level = os.path.join(temp_dir, expected_top_level_dir)
        self.assertTrue(
            os.path.isdir(top_level),
            msg=f"Expected top-level project directory '{expected_top_level_dir}' was not created.",
        )

        # The original snake_case name should NOT appear as a top-level directory.
        self.assertFalse(
            os.path.isdir(os.path.join(temp_dir, project_name)),
            msg=f"Top-level directory should be '{expected_top_level_dir}', not '{project_name}'.",
        )

        # The inner Python package should retain the snake_case name.
        inner_package = os.path.join(top_level, project_name)
        self.assertTrue(
            os.path.isdir(inner_package),
            msg=f"Expected inner Python package '{project_name}' was not found inside '{expected_top_level_dir}'.",
        )
