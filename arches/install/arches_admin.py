#!/usr/bin/env python

import arches
import argparse
import codecs
import os
import sys
import subprocess

from django.core.management.templates import TemplateCommand
from django.core.management.base import CommandError
from django.utils.crypto import get_random_string

from arches import __version__
from packaging.version import Version


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "arches.settings")
here = os.path.abspath(os.path.dirname(__file__))
COMMANDS = {}

parser = argparse.ArgumentParser(
    prog="arches",
    description="Manage Arches-based Applications",
    parents=[argparse.ArgumentParser(add_help=False)],
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
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

subparsers = parser.add_subparsers(title="available commands", dest="command")
subparsers.required = True

parser_startproject = subparsers.add_parser(
    "startproject",
    help="Create the scaffolding for a new Arches project",
    aliases=["startapp"],
)
parser_startproject.add_argument("name", type=str, help="name of your new project")
parser_startproject.add_argument(
    "-d",
    "--directory",
    help="destination directory of your new project",
    dest="directory",
    default=None,
)
parser_startproject.add_argument(
    "-t",
    "--template",
    help="The path or URL to load the template from.",
    type=str,
    default=os.path.join(
        os.path.dirname(arches.__file__), "install", "arches-templates"
    ),
)
parser_startproject.add_argument(
    "-e",
    "--extension",
    dest="extensions",
    help="The file extension(s) to render (default: py).",
    type=str,
    default=["py", "txt", "html", "js", "css", "log", "json", "gitignore"],
)
parser_startproject.add_argument(
    "-n",
    "--name",
    dest="files",
    help="name of your new arches project",
    type=str,
    default="",
)
parser_startproject.add_argument(
    "--exclude",
    "-x",
    default=".git",  # defaulting to `.git` here so hidden directories such as `.github` will be copied over
    nargs="?",
    help=(
        "The directory name(s) to exclude, in addition to .git and "
        "__pycache__. Can be used multiple times."
    ),
)

parser_startproject.add_argument(
    "-y",
    "--yes",
    action="store_true",
    dest="yes",
    help='used to force a yes answer to any user input "continue? y/n" prompt',
)


class ArchesProjectCommand(TemplateCommand):
    help = (
        "Creates a Django project directory structure for the given "
        "project or application name in the current directory or "
        "optionally in the given directory."
    )
    missing_args_message = "You must provide a valid name."

    def handle(self, options):
        project_name, target = options.pop("name"), options.pop("directory")

        # Create a random SECRET_KEY to put it in the main settings.
        chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
        options["secret_key"] = "django-insecure-" + get_random_string(50, chars)

        # this is used in the package.json file generated when "arches-admin startproject" is called
        # if this is not a final released version of arches (for developers) then arches_version will be blank
        # and the arches dependency defined in the generated package.json file will point to "master"
        complete_version = Version(__version__)
        if complete_version.is_prerelease:
            options["arches_version"] = (
                f"dev/{complete_version.major}.{complete_version.minor}.x"
            )
        else:
            options["arches_version"] = f"stable/{__version__}"
        options["arches_semantic_version"] = ".".join(
            [
                str(complete_version.major),
                str(complete_version.minor),
                str(complete_version.micro),
            ]
        )
        options["arches_next_minor_version"] = ".".join(
            [str(complete_version.major), str(complete_version.minor + 1), "0"]
        )
        options["project_name_title_case"] = project_name.title().replace("_", "")

        super(ArchesProjectCommand, self).handle(
            "project", project_name, target, **options
        )

        # need to manually replace instances of {{ project_name }} in some files
        path_to_project = target if target else os.path.join(os.getcwd(), project_name)

        for relative_file_path in [
            os.path.join(project_name, "apps.py"),
            ".coveragerc",
            "pyproject.toml",
            ".pre-commit-config.yaml",
            ".github/workflows/main.yml",
            "MANIFEST.in",
        ]:  # relative to app root directory
            file = open(os.path.join(path_to_project, relative_file_path), "r")
            file_data = file.read()
            file.close()

            updated_file_data = (
                file_data.replace(
                    "{{ project_name_title_case }}",
                    options["project_name_title_case"],
                )
                .replace(
                    "{{ project_name_kebab_case }}",
                    options["project_name_kebab_case"],
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


def command_startproject(args):
    options = vars(args)
    name = options["name"]
    make_directory = False

    project_name_kebab_case = name.replace("_", "-")
    options["project_name_kebab_case"] = project_name_kebab_case
    directory_name_will_be_changed = name != project_name_kebab_case

    if not options["directory"] and directory_name_will_be_changed:
        if not options.get("yes"):
            response = input(
                f"The project directory will be renamed from {name} to {project_name_kebab_case}.\n"
                "If this is not desired, use the --directory option to create "
                "a directory with the name you want.\n"
                "Consider using a name distinct from your project name.\n"
                "For more information, see https://github.com/archesproject/arches/issues/12028\n"
                "Continue? (y/N):"
            )
            if response.lower() not in ["y", "yes"]:
                print("Operation cancelled.")
                sys.exit(0)

        make_directory = True
        options["directory"] = project_name_kebab_case

    directory = options["directory"]

    project_path = os.path.join(os.getcwd(), directory if directory else name)

    # TODO: remove manual directory creation when upgrading to Django 6+
    # re. https://github.com/django/django/pull/18387
    if make_directory and not os.path.exists(project_path):
        os.mkdir(project_path)

    cmd = ArchesProjectCommand()
    cmd.handle(options)

    os.chdir(project_path)
    subprocess.call("npm install", shell=True)

    open(os.path.join(os.getcwd(), "arches.log"), "w").close()

    os.chdir(os.path.join(project_path, name))
    if os.path.isdir(os.path.join(os.getcwd(), "logs")) is not True:
        os.mkdir(os.path.join(os.getcwd(), "logs"))

    open(os.path.join(os.getcwd(), "logs", "resource_import.log"), "w").close()


COMMANDS["startproject"] = command_startproject
COMMANDS["startapp"] = command_startproject


class CommandError(Exception):
    pass


try:
    # Python 3
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer)
except AttributeError:
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr)


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
