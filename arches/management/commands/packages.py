import json
import pyprind
import csv
import shutil
import subprocess
import glob
import uuid
import sys
import urllib.request, urllib.parse, urllib.error
import os
import imp
import logging
import requests
from arches.setup import unzip_file
from arches.management.commands import utils
from arches.app.utils import import_class_from_string
from arches.app.utils.skos import SKOSReader
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.system_metadata import system_metadata
from arches.app.utils.data_management.resources.importer import BusinessDataImporter
from arches.app.utils.data_management.resource_graphs import exporter as ResourceGraphExporter
from arches.app.utils.data_management.resource_graphs.importer import import_graph as ResourceGraphImporter
from arches.app.utils.data_management.resources.formats.csvfile import (
    MissingConfigException,
    TileCsvReader,
)
from arches.app.utils.data_management.resources.formats.format import MissingGraphException
from arches.app.utils.data_management.resources.formats.format import Reader as RelationImporter
from arches.app.utils.data_management.resources.exporter import ResourceExporter
from arches.app.models.system_settings import settings
from arches.app.models import models
import arches.app.utils.data_management.resource_graphs.importer as graph_importer
import arches.app.utils.data_management.resource_graphs.exporter as graph_exporter
import arches.app.utils.data_management.resources.remover as resource_remover
import arches.app.utils.task_management as task_management
from django.forms.models import model_to_dict
from django.db.utils import IntegrityError
from django.db import transaction, connection
from django.utils.module_loading import import_string
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.core import management
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

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

"""This module contains commands for building Arches."""


class Command(BaseCommand):
    """
    Commands for managing the loading and running of packages in Arches

    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-o",
            "--operation",
            action="store",
            dest="operation",
            default="setup",
            choices=[
                "setup",
                "install",
                "setup_indexes",
                "load_concept_scheme",
                "export_business_data",
                "export_graphs",
                "delete_mapbox_layer",
                "create_mapping_file",
                "import_reference_data",
                "import_graphs",
                "import_business_data",
                "import_business_data_relations",
                "import_mapping_file",
                "save_system_settings",
                "add_mapbox_layer",
                "load_package",
                "create_package",
                "update_package",
                "export_package_configs",
                "import_node_value_data",
            ],
            help="Operation Type; "
            + "'setup'=Sets up the database schema and code"
            + "'setup_indexes'=Creates the indexes in Elastic Search needed by the system"
            + "'install'=Runs the setup file defined in your package root",
        )

        parser.add_argument(
            "-s", "--source", action="store", dest="source", default="", help="Directory or file for processing",
        )

        parser.add_argument(
            "-f", "--format", action="store", dest="format", default="arches", help="Format: shp or arches",
        )

        parser.add_argument(
            "-l",
            "--load_id",
            action="store",
            dest="load_id",
            help="Text string identifying the resources in the data load you want to delete.",
        )

        parser.add_argument(
            "-d", "--dest_dir", action="store", dest="dest_dir", default=".", help="Directory where you want to save exported files."
        )

        parser.add_argument(
            "-r",
            "--resources",
            action="store",
            dest="resources",
            default=False,
            help="A comma separated list of the resourceids of the resources you would like to import/export.",
        )

        parser.add_argument(
            "-g",
            "--graphs",
            action="store",
            dest="graphs",
            default=False,
            help="A comma separated list of the graphids of the resources you would like to import/export.",
        )

        parser.add_argument(
            "-c", "--config_file", action="store", dest="config_file", default=None, help="Usually an export mapping file.",
        )

        parser.add_argument(
            "-j",
            "--mapbox_json_path",
            action="store",
            dest="mapbox_json_path",
            default=False,
            help="A path to a mapbox json file to generate a layer from.",
        )

        parser.add_argument(
            "-n", "--layer_name", action="store", dest="layer_name", default=False, help="The name of the layer to add or delete."
        )

        parser.add_argument(
            "-ow",
            "--overwrite",
            action="store",
            dest="overwrite",
            default="",
            help="Whether to overwrite existing concepts with ones being imported or not.",
        )

        parser.add_argument(
            "-st",
            "--stage",
            action="store",
            dest="stage",
            default="keep",
            help="Whether to stage new concepts or add them to the existing concept scheme.",
        )

        parser.add_argument(
            "-i", "--layer_icon", action="store", dest="layer_icon", default="fa fa-globe", help="An icon class to use for a map layer."
        )

        parser.add_argument("-b", "--is_basemap", action="store_true", dest="is_basemap", help="Add to make the layer a basemap.")

        parser.add_argument("-db", "--setup_db", action="store_true", dest="setup_db", default=False, help="Rebuild database")
        parser.add_argument("-dev", "--dev", action="store_true", dest="dev", help="Loading package for development")

        parser.add_argument(
            "-bulk",
            "--bulk_load",
            action="store_true",
            dest="bulk_load",
            help="Bulk load values into the database.  By setting this flag the system will bypass any PreSave \
            functions attached to the resource, as well as prevent some logging statements from printing to console.",
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
            "-pi",
            "--prevent_indexing",
            action="store_true",
            dest="prevent_indexing",
            help="Prevents indexing the resources or concepts into Elasticsearch",
        )

        parser.add_argument(
            "-create_concepts",
            "--create_concepts",
            action="store",
            dest="create_concepts",
            help="Create concepts from your business data on import. When setting this flag the system will pull the \
            unique values from columns indicated as concepts and load them into candidates and collections.",
        )

        parser.add_argument(
            "-single_file",
            "--single_file",
            action="store_true",
            dest="single_file",
            help="Export grouped business data attrbiutes one or multiple csv files. By setting this flag the system \
            will export all grouped business data to one csv file.",
        )

        parser.add_argument("-type", "--graphtype", action="store", dest="type", help="indicates the type of graph intended for export")

        parser.add_argument(
            "-y", "--yes", action="store_true", dest="yes", help='used to force a yes answer to any user input "continue? y/n" prompt'
        )

        parser.add_argument("--use_multiprocessing", action="store_true", help="enables multiprocessing during data import")

    def handle(self, *args, **options):
        print("operation: " + options["operation"])
        package_name = settings.PACKAGE_NAME

        if options["operation"] == "setup":
            self.setup(package_name, es_install_location=options["dest_dir"])

        if options["operation"] == "install":
            self.install(package_name)

        if options["operation"] == "setup_indexes":
            self.setup_indexes()

        if options["operation"] == "delete_indexes":
            self.delete_indexes()

        if options["operation"] == "load_concept_scheme":
            self.load_concept_scheme(package_name, options["source"])

        if options["operation"] == "export_business_data":
            self.export_business_data(
                options["dest_dir"], options["format"], options["config_file"], options["graphs"], options["single_file"]
            )

        if options["operation"] == "import_reference_data":
            self.import_reference_data(options["source"], options["overwrite"], options["stage"], options["prevent_indexing"])

        if options["operation"] == "import_graphs":
            self.import_graphs(options["source"])

        if options["operation"] == "export_graphs":
            self.export_graphs(options["dest_dir"], options["graphs"], options["type"])

        if options["operation"] == "import_business_data":

            self.import_business_data(
                options["source"],
                options["config_file"],
                options["overwrite"],
                options["bulk_load"],
                options["create_concepts"],
                use_multiprocessing=options["use_multiprocessing"],
                force=options["yes"],
                prevent_indexing=options["prevent_indexing"],
            )

        if options["operation"] == "import_node_value_data":
            self.import_node_value_data(options["source"], options["overwrite"])

        if options["operation"] == "import_business_data_relations":
            self.import_business_data_relations(options["source"])

        if options["operation"] == "import_mapping_file":
            self.import_mapping_file(options["source"])

        if options["operation"] == "save_system_settings":
            self.save_system_settings(options["dest_dir"])

        if options["operation"] == "add_mapbox_layer":
            self.add_mapbox_layer(
                options["layer_name"], options["mapbox_json_path"], options["layer_icon"], options["is_basemap"],
            )

        if options["operation"] == "delete_mapbox_layer":
            self.delete_mapbox_layer(options["layer_name"])

        if options["operation"] == "create_mapping_file":
            self.create_mapping_file(options["dest_dir"], options["graphs"])

        if options["operation"] in ["load", "load_package"]:
            defer_indexing = False if str(options["defer_indexing"])[0].lower() == "f" else True
            self.load_package(
                options["source"],
                options["setup_db"],
                options["overwrite"],
                options["bulk_load"],
                options["stage"],
                options["yes"],
                options["dev"],
                defer_indexing,
            )

        if options["operation"] in ["create", "create_package"]:
            self.create_package(options["dest_dir"])

        if options["operation"] in ["update", "update_package"]:
            self.update_package(options["dest_dir"], options["yes"])

        if options["operation"] == "export_package_configs":
            self.export_package_configs(options["dest_dir"])

    def export_package_configs(self, dest_dir):
        with open(os.path.join(dest_dir, "package_config.json"), "w") as config_file:
            try:
                constraints = models.Resource2ResourceConstraint.objects.all()
                configs = {"permitted_resource_relationships": constraints, "business_data_load_order": []}
                config_file.write(JSONSerializer().serialize(configs))
            except Exception as e:
                print(e)
                print("Could not read resource to resource constraints")

    def export_resource_graphs(self, dest_dir, force=False):
        """
        Saves a json file for each resource model in a project.
        Uses the graph name as the file name unless a graph
        (confirmed by matching graphid) already exists in the destination
        directory. In that case, the existing filename is used.
        """
        existing_resource_graphs = {}
        existing_resource_graph_paths = glob.glob(os.path.join(dest_dir, "*.json"))
        for existing_graph_file in existing_resource_graph_paths:
            print("reading", existing_graph_file)
            with open(existing_graph_file, "r") as f:
                existing_graph = json.loads(f.read())
                if "graph" in existing_graph:
                    existing_graph = existing_graph["graph"][0]
                existing_resource_graphs[existing_graph["graphid"]] = {
                    "name": existing_graph["name"],
                    "path": existing_graph_file,
                }

        resource_graphs = ResourceGraphExporter.get_graphs_for_export(["resource_models"])
        if "graph" in resource_graphs:
            for graph in resource_graphs["graph"]:
                output_graph = {"graph": [graph], "metadata": system_metadata()}
                graph_json = JSONSerializer().serialize(output_graph, indent=4)
                if graph["graphid"] not in existing_resource_graphs:
                    output_file = os.path.join(dest_dir, graph["name"] + ".json")
                    with open(output_file, "w") as f:
                        print("writing", output_file)
                        f.write(graph_json)
                else:
                    output_file = existing_resource_graphs[graph["graphid"]]["path"]
                    if force is False:
                        overwrite = input(
                            '"{0}" already exists in this directory. \
                        Overwrite? (Y/N): '.format(
                                existing_resource_graphs[graph["graphid"]]["name"]
                            )
                        )
                    else:
                        overwrite = "true"
                    if overwrite.lower() in ("t", "true", "y", "yes"):
                        with open(output_file, "w") as f:
                            print("writing", output_file)
                            f.write(graph_json)

    def export_package_settings(self, dest_dir, force=False):
        overwrite = True
        projects_package_settings_file = os.path.join(settings.APP_ROOT, "package_settings.py")
        packages_package_settings_file = os.path.join(dest_dir, "package_settings.py")
        if os.path.exists(projects_package_settings_file):
            if os.path.exists(packages_package_settings_file) and force is False:
                resp = input(
                    '"{0}" already exists in this directory.\
                    Overwrite? (Y/N): '.format(
                        "package_settings.py"
                    )
                )
                if resp.lower() in ("t", "true", "y", "yes"):
                    overwrite = True
                else:
                    overwrite = False
            if overwrite is True:
                shutil.copy(projects_package_settings_file, dest_dir)

    def export_widgets(self, dest_dir, force=False):
        overwrite = True
        widget_path = os.path.join(settings.APP_ROOT, "media", "js", "views", "components", "widgets")
        widget_template_path = os.path.join(settings.APP_ROOT, "templates", "views", "components", "widgets")
        widget_config_path = os.path.join(settings.APP_ROOT, "widgets")
        if os.path.exists(widget_path):
            widgets = glob.glob(os.path.join(widget_path, "*.js"))
            for widget in widgets:
                widget_basename = os.path.splitext(os.path.basename(widget))[0]
                widget_dir = os.path.join(dest_dir, widget_basename)
                widget_config_file = os.path.join(widget_config_path, widget_basename + ".json")
                widget_template_file = os.path.join(widget_template_path, widget_basename + ".htm")
                if os.path.exists(widget_dir) is False:
                    os.makedirs(widget_dir)
                shutil.copy(widget, widget_dir)
                if os.path.exists(widget_template_file):
                    shutil.copy(widget_template_file, widget_dir)
                if os.path.exists(widget_config_file):
                    with open(widget_config_file) as f:
                        details = json.load(f)
                        if "widgetid" not in details:
                            widget_instance = models.Widget.objects.get(name=details["name"])
                            details["widgetid"] = str(widget_instance.widgetid)
                            f.close()
                            with open(widget_config_file, "w") as of:
                                json.dump(details, of, sort_keys=True, indent=4)
                    shutil.copy(widget_config_file, widget_dir)

    def update_package(self, dest_dir, yes):
        if os.path.exists(os.path.join(dest_dir, "package_config.json")):
            print("Updating Widgets")
            self.export_widgets(os.path.join(dest_dir, "extensions", "widgets"))
            print("Updating Resource Models")
            self.export_resource_graphs(os.path.join(dest_dir, "graphs", "resource_models"), yes)
        else:
            print(
                "Could not update package. This directory does not have a package_config.json file. \
                It cannot be verified as a package."
            )
        self.export_package_settings(dest_dir, yes)

    def create_package(self, dest_dir):
        if os.path.exists(dest_dir):
            print("Cannot create package", dest_dir, "already exists")
        else:
            print("Creating template package in", dest_dir)
            dirs = [
                "business_data",
                "business_data/files",
                "business_data/relations",
                "business_data/resource_views",
                "extensions/datatypes",
                "extensions/functions",
                "extensions/widgets",
                "extensions/css",
                "extensions/bindings",
                "extensions/card_components",
                "extensions/plugins",
                "graphs/branches",
                "graphs/resource_models",
                "ontologies",
                "map_layers/mapbox_spec_json/overlays",
                "map_layers/mapbox_spec_json/basemaps",
                "preliminary_sql",
                "reference_data/concepts",
                "reference_data/collections",
                "system_settings",
            ]
            for directory in dirs:
                os.makedirs(os.path.join(dest_dir, directory))

            for directory in dirs:
                if len(glob.glob(os.path.join(dest_dir, directory, "*"))) == 0:
                    with open(os.path.join(dest_dir, directory, ".gitkeep"), "w"):
                        print("added", os.path.join(dest_dir, directory, ".gitkeep"))

            self.export_package_configs(dest_dir)
            self.export_resource_graphs(os.path.join(dest_dir, "graphs", "resource_models"), "true")
            self.export_widgets(os.path.join(dest_dir, "extensions", "widgets"))

            try:
                self.save_system_settings(data_dest=os.path.join(dest_dir, "system_settings"))
            except Exception as e:
                print(e)
                print("Could not save system settings")
            self.export_package_settings(dest_dir, "true")

    def load_package(
        self,
        source,
        setup_db=False,
        overwrite_concepts="ignore",
        bulk_load=False,
        stage_concepts="keep",
        yes=False,
        dev=False,
        defer_indexing=True,
    ):

        celery_worker_running = task_management.check_if_celery_available()

        def load_ontologies(package_dir):
            ontologies = glob.glob(os.path.join(package_dir, "ontologies/*"))
            if len(ontologies) > 0:
                print("loading ontologies")
            else:
                print("No Ontologies to load")
            for ontology in ontologies:
                management.call_command("load_ontology", source=ontology)

        def load_system_settings(package_dir):
            update_system_settings = True
            if os.path.exists(settings.SYSTEM_SETTINGS_LOCAL_PATH):
                if yes is False:
                    response = input("Overwrite current system settings with package settings? (Y/N): ")
                    if response.lower() in ("t", "true", "y", "yes"):
                        update_system_settings = True
                        print("Using package system settings")
                    else:
                        update_system_settings = False

            if update_system_settings is True:
                if len(glob.glob(os.path.join(package_dir, "system_settings", "System_Settings.json"))) > 0:
                    system_settings = os.path.join(package_dir, "system_settings", "System_Settings.json")
                    shutil.copy(system_settings, settings.SYSTEM_SETTINGS_LOCAL_PATH)
                    self.import_business_data(settings.SYSTEM_SETTINGS_LOCAL_PATH, overwrite=True)

        def load_package_settings(package_dir):
            if os.path.exists(os.path.join(package_dir, "package_settings.py")) is True:
                update_package_settings = True
                if os.path.exists(os.path.join(settings.APP_ROOT, "package_settings.py")):
                    if yes is False:
                        response = input("Overwrite current packages_settings.py? (Y/N): ")
                        if response.lower() not in ("t", "true", "y", "yes"):
                            update_package_settings = False
                    if update_package_settings is True and os.path.exists(os.path.join(package_dir, "package_settings.py")):
                        package_settings = os.path.join(package_dir, "package_settings.py")
                        shutil.copy(package_settings, settings.APP_ROOT)
                elif os.path.exists(os.path.join(package_dir, "package_settings.py")):
                    package_settings = os.path.join(package_dir, "package_settings.py")
                    shutil.copy(package_settings, settings.APP_ROOT)

        def load_resource_to_resource_constraints(package_dir):
            config_paths = glob.glob(os.path.join(package_dir, "package_config.json"))
            if len(config_paths) > 0:
                try:
                    configs = json.load(open(config_paths[0]))
                    for relationship in configs["permitted_resource_relationships"]:
                        (obj, created) = models.Resource2ResourceConstraint.objects.update_or_create(
                            resourceclassfrom_id=uuid.UUID(relationship["resourceclassfrom_id"]),
                            resourceclassto_id=uuid.UUID(relationship["resourceclassto_id"]),
                            resource2resourceid=uuid.UUID(relationship["resource2resourceid"]),
                        )
                except json.decoder.JSONDecodeError as e:
                    logger.warn("Invalid syntax in package_config.json. Please inspect and then re-run command.")
                    logger.warn(e)
                    sys.exit()

        @transaction.atomic
        def load_sql(package_dir, sql_dir):
            sql_files = glob.glob(os.path.join(package_dir, sql_dir, "*.sql"))
            try:
                with connection.cursor() as cursor:
                    for sql_file in sql_files:
                        with open(sql_file, "r") as f:
                            sql = f.read()
                            cursor.execute(sql)
            except Exception as e:
                print(e)
                print("Failed to load sql files")

        def load_resource_views(package_dir):
            resource_views = glob.glob(os.path.join(package_dir, "business_data", "resource_views", "*.sql"))
            try:
                with connection.cursor() as cursor:
                    for view in resource_views:
                        with open(view, "r") as f:
                            sql = f.read()
                            cursor.execute(sql)
            except Exception as e:
                print(e)
                print("Failed to load resource views")

        def load_graphs(package_dir):
            try:
                branches = glob.glob(os.path.join(package_dir, "graphs", "branches"))[0]
            except IndexError as e:
                logger.warning("No branches in package")
                branches = ""
            resource_models = glob.glob(os.path.join(package_dir, "graphs", "resource_models"))[0]
            # self.import_graphs(os.path.join(settings.ROOT_DIR, 'db', 'graphs','branches'), overwrite_graphs=False)
            overwrite_graphs = True if yes is True else False
            self.import_graphs(branches, overwrite_graphs=overwrite_graphs)
            self.import_graphs(resource_models, overwrite_graphs=overwrite_graphs)

        def load_concepts(package_dir, overwrite, stage, defer_indexing):
            file_types = ["*.xml", "*.rdf"]

            from time import time

            start = time()

            concept_data = []
            for file_type in file_types:
                concept_data.extend(glob.glob(os.path.join(package_dir, "reference_data", "concepts", file_type)))

            bar1 = pyprind.ProgBar(len(concept_data), bar_char="█") if len(concept_data) > 1 else None
            for path in concept_data:
                if bar1 is None:
                    print(path)
                self.import_reference_data(path, overwrite, stage, defer_indexing)
                if bar1 is not None:
                    head, tail = os.path.split(path)
                    bar1.update(item_id=tail + (" " * 10))

            collection_data = []
            for file_type in file_types:
                collection_data.extend(glob.glob(os.path.join(package_dir, "reference_data", "collections", file_type)))

            bar2 = pyprind.ProgBar(len(collection_data), bar_char="█") if len(collection_data) > 1 else None
            for path in collection_data:
                if bar2 is None:
                    print(path)
                self.import_reference_data(path, overwrite, stage, defer_indexing)
                if bar2 is not None:
                    head, tail = os.path.split(path)
                    bar2.update(item_id=tail)

            print("Total time to load concepts: %s s" % (timedelta(seconds=time() - start)))

        def load_mapbox_styles(style_paths, basemap):
            for path in style_paths:
                style = json.load(open(path))
                try:
                    meta = {"icon": "fa fa-globe", "name": style["name"]}
                    if os.path.exists(os.path.join(os.path.dirname(path), "meta.json")):
                        meta = json.load(open(os.path.join(os.path.dirname(path), "meta.json")))
                    self.add_mapbox_layer(meta["name"], path, meta["icon"], basemap)
                except KeyError as e:
                    logger.warning("The map layer '{}' was not imported: {} is missing.".format(path, e))

        def load_map_layers(package_dir):
            basemap_styles = glob.glob(os.path.join(package_dir, "map_layers", "mapbox_spec_json", "basemaps", "*", "*.json"))
            overlay_styles = glob.glob(os.path.join(package_dir, "map_layers", "mapbox_spec_json", "overlays", "*", "*.json"))
            load_mapbox_styles(basemap_styles, True)
            load_mapbox_styles(overlay_styles, False)

        def load_business_data(package_dir, prevent_indexing):
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
                        import_business_data.s(data_source=path, overwrite=True, bulk_load=bulk_load, prevent_indexing=prevent_indexing)
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

        def load_extensions(package_dir, ext_type, cmd):
            extensions = glob.glob(os.path.join(package_dir, "extensions", ext_type, "*"))
            root = settings.APP_ROOT if settings.APP_ROOT is not None else os.path.join(settings.ROOT_DIR, "app")
            component_dir = os.path.join(root, "media", "js", "views", "components", ext_type)
            module_dir = os.path.join(root, ext_type)
            template_dir = os.path.join(root, "templates", "views", "components", ext_type)

            for extension in extensions:
                templates = glob.glob(os.path.join(extension, "*.htm"))
                components = glob.glob(os.path.join(extension, "*.js"))

                if len(templates) == 1:
                    dest_path = os.path.join(template_dir, os.path.basename(templates[0]))
                    if os.path.exists(dest_path) is False:
                        if os.path.exists(template_dir) is False:
                            os.mkdir(template_dir)
                        shutil.copy(templates[0], template_dir)
                    else:
                        logger.info("Not loading {0} from package. Extension already exists".format(templates[0]))

                if len(components) == 1:
                    dest_path = os.path.join(component_dir, os.path.basename(components[0]))
                    if os.path.exists(dest_path) is False:
                        if os.path.exists(component_dir) is False:
                            os.mkdir(component_dir)
                        shutil.copy(components[0], component_dir)
                    else:
                        logger.info("Not loading {0} from package. Extension already exists".format(components[0]))

                modules = glob.glob(os.path.join(extension, "*.json"))
                modules.extend(glob.glob(os.path.join(extension, "*.py")))

                if len(modules) > 0:
                    dest_path = os.path.join(module_dir, os.path.basename(modules[0]))
                    if os.path.exists(dest_path) is False:
                        module = modules[0]
                        shutil.copy(module, module_dir)
                        management.call_command(cmd, "register", source=module)
                    else:
                        logger.info("Not loading {0} from package. Extension already exists".format(modules[0]))

        def load_indexes(package_dir):
            index_files = glob.glob(os.path.join(package_dir, "search_indexes", "*.py"))
            root = settings.APP_ROOT if settings.APP_ROOT is not None else os.path.join(settings.ROOT_DIR, "app")
            dest_dir = os.path.join(root, "search_indexes")

            for index_file in index_files:
                shutil.copy(index_file, dest_dir)
                package_settings = imp.load_source("", os.path.join(settings.APP_ROOT, "package_settings.py"))
                for index in package_settings.ELASTICSEARCH_CUSTOM_INDEXES:
                    es_index = import_class_from_string(index["module"])(index["name"])
                    es_index.prepare_index()

        def load_kibana_objects(package_dir):
            # only try and load Kibana objects if they exist
            if len(glob.glob(os.path.join(package_dir, "kibana_objects", "*.ndjson"))) > 0:
                commands = ["kibana", "--source_dir", os.path.join(package_dir, "kibana_objects"), "-ow"]
                if yes is True:
                    commands.append("-y")
                management.call_command(*commands, operation="load")

        def load_datatypes(package_dir):
            load_extensions(package_dir, "datatypes", "datatype")

        def load_widgets(package_dir):
            load_extensions(package_dir, "widgets", "widget")

        def load_card_components(package_dir):
            load_extensions(package_dir, "card_components", "card_component")

        def load_search_components(package_dir):
            load_extensions(package_dir, "search", "search")

        def load_plugins(package_dir):
            load_extensions(package_dir, "plugins", "plugin")

        def load_reports(package_dir):
            load_extensions(package_dir, "reports", "report")

        def load_functions(package_dir):
            load_extensions(package_dir, "functions", "fn")

        def cache_graphs():
            management.call_command("cache", operation="graphs")

        def update_resource_materialized_view():
            with connection.cursor() as cursor:
                cursor.execute("REFRESH MATERIALIZED VIEW mv_geojson_geoms;")

        def load_apps(package_dir):
            package_apps = glob.glob(os.path.join(package_dir, "apps", "*"))
            for app in package_apps:
                try:
                    app_name = os.path.basename(app)
                    management.call_command("startapp", "--template", app, app_name)
                    management.call_command("makemigrations", app_name, interactive=False)
                    management.call_command("migrate", new_name, interactive=False)
                except CommandError as e:
                    print(e)

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

        package_location = handle_source(source)
        if not package_location:
            raise Exception("this is an invalid package source")

        if setup_db:
            management.call_command("setup_db", force=True)
        if dev:
            management.call_command("add_test_users")
        load_ontologies(package_location)
        print("loading Kibana objects")
        load_kibana_objects(package_location)
        print("loading package_settings.py")
        load_package_settings(package_location)
        print("loading preliminary sql")
        load_sql(package_location, "preliminary_sql")
        print("loading system settings")
        load_system_settings(package_location)
        print("loading project extensions from project")
        management.call_command("project", "update")
        print("loading widgets")
        load_widgets(package_location)
        print("loading card components")
        load_card_components(package_location)
        print("loading search components")
        load_search_components(package_location)
        print("loading plugins")
        load_plugins(package_location)
        print("loading reports")
        load_reports(package_location)
        print("loading functions")
        load_functions(package_location)
        print("loading datatypes")
        load_datatypes(package_location)
        print("loading concepts")
        load_concepts(package_location, overwrite_concepts, stage_concepts, defer_indexing)
        print("loading resource models and branches")
        load_graphs(package_location)
        print("loading resource to resource constraints")
        load_resource_to_resource_constraints(package_location)
        print("loading map layers")
        load_map_layers(package_location)
        print("loading search indexes")
        load_indexes(package_location)
        print("loading business data - resource instances and relationships")
        load_business_data(package_location, defer_indexing)
        print("loading resource views")
        load_resource_views(package_location)
        print("loading apps")
        load_apps(package_location)
        root = settings.APP_ROOT if settings.APP_ROOT is not None else os.path.join(settings.ROOT_DIR, "app")
        print("loading package css")
        css_source = os.path.join(package_location, "extensions", "css")
        if os.path.exists(css_source):
            css_dest = os.path.join(root, "media", "css")
            if not os.path.exists(css_dest):
                os.mkdir(css_dest)
            css_files = glob.glob(os.path.join(css_source, "*.css"))
            for css_file in css_files:
                shutil.copy(css_file, css_dest)
        print("Refreshing the resource view")
        update_resource_materialized_view()
        print("loading post sql")
        load_sql(package_location, "post_sql")
        if defer_indexing is True:
            print("indexing database")
            management.call_command("es", "reindex_database")
        if celery_worker_running:
            print("Celery detected: Resource instances loading. Log in to arches to be notified on completion.")
        else:
            print("package load complete")

    def setup(self, package_name, es_install_location=None):
        """
        Installs the database into postgres as "arches_<package_name>"

        """

        self.setup_db(package_name)

    def install(self, package_name):
        """
        Runs the setup.py file found in the package root

        """

        install = import_string("%s.setup.install" % package_name)
        install()

    def setup_db(self, package_name):
        """
        Drops and re-installs the database found at "arches_<package_name>"
        WARNING: This will destroy data

        """

        management.call_command("setup_db", force=True)

    def setup_indexes(self):
        management.call_command("es", operation="setup_indexes")

    def delete_indexes(self):
        management.call_command("es", operation="delete_indexes")

    def export_business_data(
        self, data_dest=None, file_format=None, config_file=None, graphid=None, single_file=False,
    ):
        graphids = []
        if graphid is False and file_format == "json":
            graphids = [
                str(graph.graphid)
                for graph in models.GraphModel.objects.filter(isresource=True).exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
            ]
        if graphid is False and file_format != "json":
            utils.print_message("Exporting data for all graphs is currently only supported for the json format")
            sys.exit()
        if graphid:
            graphids.append(graphid)
        if os.path.exists(data_dest):
            safe_characters = (" ", ".", "_", "-")
            for graphid in graphids:
                try:
                    resource_exporter = ResourceExporter(
                        file_format, configs=config_file, single_file=single_file
                    )  # New exporter needed for each graphid, else previous data is appended with each subsequent graph
                    data = resource_exporter.export(graph_id=graphid, resourceinstanceids=None)
                    for file in data:
                        with open(
                            os.path.join(
                                data_dest,
                                "".join(char if (char.isalnum() or char in safe_characters) else "-" for char in file["name"]).rstrip(),
                            ),
                            "w",
                        ) as f:
                            file["outputfile"].seek(0)
                            shutil.copyfileobj(file["outputfile"], f, 16 * 1024)
                except KeyError:
                    utils.print_message("{0} is not a valid export file format.".format(file_format))
                    sys.exit()
                except MissingConfigException:
                    utils.print_message("No mapping file specified. Please rerun this command with the '-c' parameter populated.")
                    sys.exit()
        else:
            utils.print_message(
                "The destination is unspecified or invalid. Please rerun this command with the '-d' parameter populated with a valid path."
            )
            sys.exit()

    def import_reference_data(self, data_source, overwrite="ignore", stage="stage", prevent_indexing=False):
        if overwrite == "":
            overwrite = "overwrite"

        skos = SKOSReader()
        rdf = skos.read_file(data_source)
        ret = skos.save_concepts_from_skos(rdf, overwrite, stage, prevent_indexing)

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
            for source in data_source:
                path = utils.get_valid_path(source)
                if path is not None:
                    print("Importing {0}. . .".format(path))
                    BusinessDataImporter(path, config_file).import_business_data(
                        overwrite=overwrite,
                        bulk=bulk_load,
                        create_concepts=create_concepts,
                        create_collections=create_collections,
                        use_multiprocessing=use_multiprocessing,
                        prevent_indexing=prevent_indexing,
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

    def import_node_value_data(self, data_source, overwrite=None):
        """
        Imports node-value datatype business data only.
        """

        if overwrite == "":
            utils.print_message("No overwrite option indicated. Please rerun command with '-ow' parameter.")
            sys.exit()

        if isinstance(data_source, str):
            data_source = [data_source]

        if len(data_source) > 0:
            for source in data_source:
                path = utils.get_valid_path(source)
                if path is not None:
                    data = csv.DictReader(open(path, "r"), encoding="utf-8-sig")
                    business_data = list(data)
                    TileCsvReader(business_data).import_business_data(overwrite=None)
                else:
                    utils.print_message("No file found at indicated location: {0}".format(source))
                    sys.exit()
        else:
            utils.print_message(
                "No BUSINESS_DATA_FILES locations specified in your settings file.\
                Please rerun this command with BUSINESS_DATA_FILES locations specified or \
                pass the locations in manually with the '-s' parameter."
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

    def import_graphs(self, data_source="", overwrite_graphs=True):
        """
        Imports objects from arches.json.

        """

        if data_source == "":
            data_source = settings.RESOURCE_GRAPH_LOCATIONS

        if isinstance(data_source, str):
            data_source = [data_source]

        errors = []
        for path in data_source:
            if os.path.isfile(os.path.join(path)):
                print(os.path.join(path))
                with open(path, "rU") as f:
                    archesfile = JSONDeserializer().deserialize(f)
                    errs, importer = ResourceGraphImporter(archesfile["graph"], overwrite_graphs)
                    errors.extend(errs)
            else:
                file_paths = [file_path for file_path in os.listdir(path) if file_path.endswith(".json")]
                for file_path in file_paths:
                    print(os.path.join(path, file_path))
                    with open(os.path.join(path, file_path), "rU") as f:
                        archesfile = JSONDeserializer().deserialize(f)
                        errs, importer = ResourceGraphImporter(archesfile["graph"], overwrite_graphs)
                        errors.extend(errs)
        for e in errors:
            utils.print_message(e)

    def export_graphs(self, data_dest="", graphs="", graphtype=""):
        """
        Exports graphs to arches.json.

        """
        if data_dest != "":
            if not graphs:
                if not graphtype:
                    graphs = [
                        str(graph["graphid"])
                        for graph in models.GraphModel.objects.exclude(graphid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID).values("graphid")
                    ]
                elif graphtype == "branch":
                    graphs = [str(graph["graphid"]) for graph in models.GraphModel.objects.filter(isresource=False).values("graphid")]
                elif graphtype == "resource":
                    graphs = [
                        str(graph["graphid"])
                        for graph in models.GraphModel.objects.filter(isresource=True)
                        .exclude(graphid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
                        .values("graphid")
                    ]
            else:
                graphs = [graph.strip() for graph in graphs.split(",")]
            for graph in ResourceGraphExporter.get_graphs_for_export(graphids=graphs)["graph"]:
                graph_name = graph["name"].replace("/", "-")
                with open(os.path.join(data_dest, graph_name + ".json"), "wb") as f:
                    f.write(JSONSerializer().serialize({"graph": [graph]}, indent=4).encode("utf-8"))
        else:
            utils.print_message("No destination directory specified. Please rerun this command with the '-d' parameter populated.")
            sys.exit()

    def save_system_settings(
        self,
        data_dest=settings.SYSTEM_SETTINGS_LOCAL_PATH,
        file_format="json",
        config_file=None,
        graph=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID,
        single_file=False,
    ):

        resource_exporter = ResourceExporter(file_format, configs=config_file, single_file=single_file)
        if data_dest == ".":
            data_dest = os.path.dirname(settings.SYSTEM_SETTINGS_LOCAL_PATH)
        if data_dest != "":
            data = resource_exporter.export(graph_id=graph)
            for file in data:
                with open(os.path.join(data_dest, file["name"]), "w") as f:
                    f.write(file["outputfile"].getvalue())
        else:
            utils.print_message("No destination directory specified. Please rerun this command with the '-d' parameter populated.")
            sys.exit()

    def add_mapbox_layer(
        self, layer_name=False, mapbox_json_path=False, layer_icon="fa fa-globe", is_basemap=False,
    ):
        if layer_name is not False and mapbox_json_path is not False:
            with open(mapbox_json_path) as data_file:
                data = json.load(data_file)
                with transaction.atomic():
                    for layer in data["layers"]:
                        if "source" in layer:
                            layer["source"] = layer["source"] + "-" + layer_name
                    for source_name, source_dict in data["sources"].items():
                        map_source = models.MapSource.objects.get_or_create(name=source_name + "-" + layer_name, source=source_dict)
                    map_layer = models.MapLayer(
                        name=layer_name, layerdefinitions=data["layers"], isoverlay=(not is_basemap), icon=layer_icon
                    )
                    try:
                        map_layer.save()
                    except IntegrityError as e:
                        print("Cannot save layer: {0} already exists".format(layer_name))

    def delete_mapbox_layer(self, layer_name=False):
        if layer_name is not False:
            try:
                mapbox_layer = models.MapLayer.objects.get(name=layer_name)
            except ObjectDoesNotExist:
                print('error: no mapbox layer named "{}"'.format(layer_name))
                return
            all_sources = [i.get("source") for i in mapbox_layer.layerdefinitions]
            # remove duplicates and None
            sources = {i for i in all_sources if i}
            with transaction.atomic():
                for source in sources:
                    src = models.MapSource.objects.get(name=source)
                    src.delete()
                mapbox_layer.delete()

    def create_mapping_file(self, dest_dir=None, graphs=None):
        if graphs is not False:
            graph = [x.strip(" ") for x in graphs.split(",")]
        include_concepts = True

        graph_exporter.create_mapping_configuration_file(graphs, include_concepts, dest_dir)

    def import_mapping_file(self, source=None):
        """
        Imports export mapping files for resource models.
        """
        if source == "":
            utils.print_message("No data source indicated. Please rerun command with '-s' parameter.")

        if isinstance(source, str):
            source = [source]

        for path in source:
            if os.path.isfile(os.path.join(path)):
                with open(path, "rU") as f:
                    mapping_file = json.load(f)
                    graph_importer.import_mapping_file(mapping_file)
