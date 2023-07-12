"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
import csv
import glob
import json
import os
import shutil
import sys
import urllib.request, urllib.parse, urllib.error
import uuid

# import the basic django settings here, don't use the Arches system_settings module
# because it makes database calls that don't necessarily work at this stage
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand

import arches.app.utils.task_management as task_management

from arches.app.models import models
from arches.app.utils.data_management.resources.formats.format import Reader as RelationImporter
from arches.app.utils.data_management.resources.importer import BusinessDataImporter
from arches.management.commands import utils
from arches.management.commands.utils import get_yn_input
from arches.setup import unzip_file


class Command(BaseCommand):
    """
    Command to load business data.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-y", "--yes", action="store_true", dest="yes", help='used to force a yes answer to any user input "continue? y/n" prompt'
        )
        parser.add_argument("-dev", "--dev", action="store_true", dest="dev", help="Add users for development")

        parser.add_argument(
            "-s", "--source", action="store", dest="source", default="", help="Directory or file for processing",
        )
        parser.add_argument(
            "-di",
            "--defer_indexing",
            action="store",
            default=True,
            dest="defer_indexing",
            help="t/f - True(t) Defer indexing until all data is loaded (default).  Should speed up data load. False(f) to index resources and concepts incrementally during loading which allows users to search data while package load runs.",
        )
        parser.add_argument(
            "-bulk",
            "--bulk_load",
            action="store_true",
            dest="bulk_load",
            help="Bulk load values into the database.  By setting this flag the system will bypass any PreSave \
            functions attached to the resource, as well as prevent some logging statements from printing to console.",
        )


    def handle(self, *args, **options):
        if options["yes"] is False:
            proceed = get_yn_input(msg="Are you sure you want to destroy and rebuild your database?", default="N")
            if not proceed:
                exit()

        package_location = self.handle_source(options["source"])
        if not package_location:
            raise Exception("this is an invalid package source")
        
        celery_worker_running = task_management.check_if_celery_available()

        self.load_business_data(
            package_location, 
            options["defer_indexing"], 
            celery_worker_running, 
            dev=options["dev"], 
            bulk_load=options["bulk_load"], 
            yes=options["yes"]
        )


    def handle_source(source):
        if os.path.isdir(source):
            return source

        package_dir = False

        unzip_into_dir = os.path.join(os.getcwd(), "_pkg_" + datetime.now().strftime("%y%m%d_%H%M%S"))
        os.mkdir(unzip_into_dir)

        if source.endswith(".zip") and os.path.isfile(source):
            unzip_file(source, unzip_into_dir)

        try:
            zip_file = os.path.join(unzip_into_dir, "source_data.zip")
            urllib.request.urlretrieve(source, zip_file)
            unzip_file(zip_file, unzip_into_dir)
        except Exception:
            pass

        for path in os.listdir(unzip_into_dir):
            if os.path.basename(path) != "__MACOSX":
                full_path = os.path.join(unzip_into_dir, path)
                if os.path.isdir(full_path):
                    package_dir = full_path
                    break

        return package_dir


    def import_business_data(
        self,
        data_source,
        config_file=None,
        overwrite=None,
        bulk_load=False,
        create_concepts=False,
        use_multiprocessing=False,
        force=False,
        prevent_indexing=False,
    ):
        """
        Imports business data from all formats. A config file (mapping file) is required for .csv format.
        """

        # messages about experimental multiprocessing and JSONL support.
        if data_source.endswith(".jsonl"):
            print(
                """
                WARNING: Support for loading JSONL files is still experimental. Be aware that
                the format of logging and console messages has not been updated."""
            )
            if use_multiprocessing is True:
                print(
                    """
                    WARNING: Support for multiprocessing files is still experimental. While using
                    multiprocessing to import resources, you will not be able to use ctrl+c (etc.)
                    to cancel the operation. You will need to manually kill all of the processes
                    with or just close the terminal. Also, be aware that print statements
                    will be very jumbled."""
                )
                if not force:
                    confirm = input("continue? Y/n ")
                    if len(confirm) > 0 and not confirm.lower().startswith("y"):
                        exit()
        if use_multiprocessing is True and not data_source.endswith(".jsonl"):
            print("Multiprocessing is only supported with JSONL import files.")

        if overwrite == "":
            utils.print_message("No overwrite option indicated. Please rerun command with '-ow' parameter.")
            sys.exit()

        if data_source == "":
            data_source = settings.BUSINESS_DATA_FILES

        if isinstance(data_source, str):
            data_source = [data_source]

        create_collections = False
        if create_concepts:
            create_concepts = str(create_concepts).lower()
            if create_concepts == "create":
                create_collections = True
                print("Creating new collections . . .")
            elif create_concepts == "append":
                print("Appending to existing collections . . .")
            create_concepts = True

        if len(data_source) > 0:
            transaction_id = uuid.uuid1()
            for source in data_source:
                path = utils.get_valid_path(source)
                if path is not None:
                    print("Importing {0}. . .".format(path))
                    importer = BusinessDataImporter(path, config_file)

                    new_languages = importer.scan_for_new_languages()

                    if new_languages is not None and len(new_languages) > 0:
                        print("\nFound possible new languages while attempting import.")
                        for language in new_languages:
                            print('Do you wish to add the language with code "{language}" to Arches? (y or n):'.format(language=language))
                            create_new_language = input()
                            if create_new_language.lower() == "y":
                                print("\nEnter the human-readable language name:")
                                language_name = input()
                                print("\nIs this language primarily read Left-To-Right (y or n):")
                                lang_is_ltr = input()
                                default_direction = "ltr" if lang_is_ltr.lower() == "y" else "rtl"
                                scope = "data"
                                new_language = models.Language(
                                    code=language, name=language_name, default_direction=default_direction, scope=scope
                                )
                                try:
                                    new_language.save()

                                except Exception as e:
                                    raise Exception("Couldn't save new entry for {language}.".format(language=language)) from e

                    importer.import_business_data(
                        overwrite=overwrite,
                        bulk=bulk_load,
                        create_concepts=create_concepts,
                        create_collections=create_collections,
                        use_multiprocessing=use_multiprocessing,
                        prevent_indexing=prevent_indexing,
                        transaction_id=transaction_id,
                    )
                else:
                    utils.print_message("No file found at indicated location: {0}".format(source))
                    sys.exit()
        else:
            utils.print_message(
                "No BUSINESS_DATA_FILES locations specified in your settings file. \
                Please rerun this command with BUSINESS_DATA_FILES locations specified \
                or pass the locations in manually with the '-s' parameter."
            )
            sys.exit()

    
    def import_business_data_relations(self, data_source):
        """
        Imports business data relations
        """
        if isinstance(data_source, str):
            data_source = [data_source]

        for path in data_source:
            if os.path.isfile(os.path.join(path)):
                relations = csv.DictReader(open(path, "r"))
                RelationImporter().import_relations(relations)
            else:
                utils.print_message("No file found at indicated location: {0}".format(path))
                sys.exit()


    def load_business_data(self, package_dir, prevent_indexing, celery_worker_running, dev=False, bulk_load=False, yes=False):
        config_paths = glob.glob(os.path.join(package_dir, "package_config.json"))
        configs = {}
        if len(config_paths) > 0:
            configs = json.load(open(config_paths[0]))

        business_data = []
        if dev and os.path.isdir(os.path.join(package_dir, "business_data", "dev_data")):
            if "business_data_load_order" in configs and len(configs["business_data_load_order"]) > 0:
                for f in configs["business_data_load_order"]:
                    business_data.append(os.path.join(package_dir, "business_data", "dev_data", f))
            else:
                for ext in ["*.json", "*.jsonl", "*.csv"]:
                    business_data += glob.glob(os.path.join(package_dir, "business_data", "dev_data", ext))
        else:
            if "business_data_load_order" in configs and len(configs["business_data_load_order"]) > 0:
                for f in configs["business_data_load_order"]:
                    business_data.append(os.path.join(package_dir, "business_data", f))
            else:
                for ext in ["*.json", "*.jsonl", "*.csv"]:
                    business_data += glob.glob(os.path.join(package_dir, "business_data", ext))

        erring_csvs = [
            path
            for path in business_data
            if os.path.splitext(path)[1] == ".csv" and os.path.isfile(os.path.splitext(path)[0] + ".mapping") is False
        ]
        message = (
            f"The following .csv files will not load because they are missing accompanying .mapping files: \n\t {','.join(erring_csvs)}"
        )
        if len(erring_csvs) > 0:
            print(message)
        if yes is False and len(erring_csvs) > 0:
            response = input("Proceed with package load without loading indicated csv files? (Y/N): ")
            if response.lower() in ("t", "true", "y", "yes"):
                print("Proceeding with package load")
            else:
                print("Aborting operation: Package Load")
                sys.exit()

        if celery_worker_running:
            from celery import chord
            from arches.app.tasks import import_business_data, package_load_complete, on_chord_error

            valid_resource_paths = [
                path
                for path in business_data
                if (".csv" in path and os.path.exists(path.replace(".csv", ".mapping"))) or (".json" in path)
            ]

            # assumes resources in csv do not depend on data being loaded prior from json in same dir
            chord(
                [
                    import_business_data.s(data_source=path, overwrite=True, bulk_load=bulk_load, prevent_indexing=False)
                    for path in valid_resource_paths
                ]
            )(package_load_complete.signature(kwargs={"valid_resource_paths": valid_resource_paths}).on_error(on_chord_error.s()))
        else:
            for path in business_data:
                if path not in erring_csvs:
                    self.import_business_data(path, overwrite=True, bulk_load=bulk_load, prevent_indexing=prevent_indexing)

        relations = glob.glob(os.path.join(package_dir, "business_data", "relations", "*.relations"))
        for relation in relations:
            self.import_business_data_relations(relation)

        uploaded_files = glob.glob(os.path.join(package_dir, "business_data", "files", "*"))
        dest_files_dir = os.path.join(settings.MEDIA_ROOT, "uploadedfiles")
        if os.path.exists(dest_files_dir) is False:
            os.makedirs(dest_files_dir)
        for f in uploaded_files:
            shutil.copy(f, dest_files_dir)