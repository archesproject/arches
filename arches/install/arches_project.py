#!/usr/bin/env python

import arches
import argparse
import codecs
import os
import sys
import subprocess
import warnings

from django.utils.crypto import get_random_string
from django.core.management.templates import TemplateCommand
from django.core.management.base import CommandError

from arches.version import get_complete_version


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "arches.settings")
here = os.path.abspath(os.path.dirname(__file__))
COMMANDS = {}


class ArchesCommand(TemplateCommand):
    help = (
        "Creates a Django project directory structure for the given "
        "project name in the current directory or optionally in the "
        "given directory."
    )
    missing_args_message = "You must provide a project name."

    def handle(self, options):
        self.stderr.write("DEPRECATION WARNING ⤵️")
        warnings.warn(
            "`arches-project create` was deprecated in 7.6.0 and will be removed in a future version.\n"
            "Call `arches-admin startproject` instead.",
            UserWarning,
        )
        project_name, target = options.pop("name"), options.pop("directory")

        # Create a random SECRET_KEY to put it in the main settings.
        chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
        options["secret_key"] = "django-insecure-" + get_random_string(50, chars)

        # this is used in the package.json file generated when "arches-project create" is called
        # if this is not a final released version of arches (for developers) then arches_version will be blank
        # and the arches dependency defined in the generated package.json file will point to "master"
        complete_version = get_complete_version()
        options["arches_version"] = "master"
        if complete_version[3] == "final":
            options["arches_version"] = f"stable/{arches.__version__}"
        elif complete_version[3] in ["alpha", "beta", "rc"]:
            options["arches_version"] = (
                f"dev/{complete_version[0]}.{complete_version[1]}.x"
            )
        options["arches_semantic_version"] = ".".join(
            [str(arches.VERSION[0]), str(arches.VERSION[1]), str(arches.VERSION[2])]
        )
        options["arches_next_minor_version"] = ".".join(
            [str(arches.VERSION[0]), str(arches.VERSION[1] + 1), "0"]
        )
        options["project_name_title_case"] = project_name.title().replace("_", "")

        super(ArchesCommand, self).handle("project", project_name, target, **options)

        # need to manually replace instances of {{ project_name }} in some files
        path_to_project = target if target else os.path.join(os.getcwd(), project_name)

        for relative_file_path in [
            os.path.join(project_name, "apps.py"),
            ".coveragerc",
            "pyproject.toml",
            ".pre-commit-config.yaml",
            ".github/workflows/main.yml",
            "vitest.config.mts",
            "vitest.setup.mts",
        ]:  # relative to app root directory
            file = open(os.path.join(path_to_project, relative_file_path), "r")
            file_data = file.read()
            file.close()

            updated_file_data = (
                file_data.replace(
                    "{{ project_name_title_case }}", options["project_name_title_case"]
                )
                .replace("{{ project_name }}", project_name)
                .replace(
                    "{{ arches_semantic_version }}", options["arches_semantic_version"]
                )
                .replace(
                    "{{ arches_next_minor_version }}",
                    options["arches_next_minor_version"],
                )
            )

            file = open(os.path.join(path_to_project, relative_file_path), "w")
            file.write(updated_file_data)
            file.close()


def command_create_app(args):
    options = vars(args)
    name = options["name"]
    directory = options["directory"]

    cmd = ArchesCommand()
    cmd.handle(options)

    project_path = os.path.join(os.getcwd(), (directory if directory else name))

    os.chdir(project_path)
    subprocess.call("npm install", shell=True)

    open(os.path.join(os.getcwd(), "arches.log"), "w").close()

    os.chdir(os.path.join(project_path, name))
    if os.path.isdir(os.path.join(os.getcwd(), "logs")) is not True:
        os.mkdir(os.path.join(os.getcwd(), "logs"))

    open(os.path.join(os.getcwd(), "logs", "resource_import.log"), "w").close()


parent_parser = argparse.ArgumentParser(add_help=False)

parser = argparse.ArgumentParser(
    prog="arches",
    description="DEPRECATED: Manage Arches-based Applications",
    parents=[parent_parser],
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

subparsers = parser.add_subparsers(title="available commands", dest="command")
subparsers.required = True

parser_start = subparsers.add_parser(
    "create",
    help="Create the scaffolding for a new Arches project",
)

parser_start.add_argument("name", type=str, help="name of your new app")

parser_start.add_argument(
    "-d",
    "--directory",
    help="destination directory of your new project",
    dest="directory",
    default=None,
)

parser_start.add_argument(
    "-t",
    "--template",
    help="The path or URL to load the template from.",
    type=str,
    default=os.path.join(
        os.path.dirname(arches.__file__), "install", "arches-templates"
    ),
)

parser_start.add_argument(
    "-e",
    "--extension",
    dest="extensions",
    help="The file extension(s) to render (default: py).",
    type=str,
    default=["py", "txt", "html", "js", "css", "log", "json", "gitignore"],
)

parser_start.add_argument(
    "-n",
    "--name",
    dest="files",
    help="name of your new arches application",
    type=str,
    default="",
)

parser_start.add_argument(
    "--exclude",
    "-x",
    default=".git",  # defaulting to `.git` here so hidden directories such as `.github` will be copied over
    nargs="?",
    help=(
        "The directory name(s) to exclude, in addition to .git and "
        "__pycache__. Can be used multiple times."
    ),
)

parser.add_argument(
    "-v",
    "--verbosity",
    action="store",
    dest="verbosity",
    default="1",
    type=int,
    choices=[0, 1, 2, 3],
    help="Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output",
)

try:
    # Python 3
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer)
except AttributeError:
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr)


class CommandError(Exception):
    pass


COMMANDS["create"] = command_create_app


def main(argv=None):
    if argv is not None:
        args = parser.parse_args(argv)
    else:
        args = parser.parse_args()

    try:
        COMMANDS[args.command](args)
    except CommandError as e:
        print(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
