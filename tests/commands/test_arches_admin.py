import argparse
import os
import shutil
import tempfile
from unittest.mock import patch

from django.test import SimpleTestCase
from django.test.utils import captured_stdout

import arches
from arches.install import arches_admin


class ArchesAdminCommandTests(SimpleTestCase):
    def test_help(self):
        with captured_stdout() as stdout:
            try:
                arches_admin.main(["--help"])
            except SystemExit:
                pass
        self.assertIn("startproject", stdout.getvalue())

    @patch("arches.install.arches_admin.subprocess.call")
    def test_startproject_uses_kebab_case_directory(self, mock_npm):
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
        self.addCleanup(os.chdir, os.getcwd())

        # mock command-line arguments for startproject, no defaults populated since
        # we're directly calling the command function
        args = argparse.Namespace(
            name=project_name,
            directory=None,
            template=os.path.join(
                os.path.dirname(arches.__file__), "install", "arches-templates"
            ),
            extensions=["py", "txt", "html", "js", "css", "log", "json", "gitignore"],
            files="",
            exclude=".git",
            yes=True,
            verbosity=1,
            command="startproject",
        )
        os.chdir(temp_dir)
        arches_admin.command_startproject(args)

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

        mock_npm.assert_called_once_with("npm install", shell=True)
