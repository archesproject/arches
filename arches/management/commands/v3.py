import os
import csv
import json
import shutil
from glob import glob
from datetime import datetime
from django.core import management
from django.core.management.base import BaseCommand, CommandError
from arches.app.models.graph import Graph
from arches.app.models.models import TileModel, Node
from arches.app.utils.skos import SKOSReader
from arches.app.utils import v3utils
from arches.app.utils.v3migration import v3Importer, v3SkosConverter, DataValueConverter
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.models.system_settings import settings


class Command(BaseCommand):
    """
    This is a suite of operations that provide the ability to migrate v3 data
    to v4 through the command line.
    """

    def add_arguments(self, parser):

        parser.add_argument(
            "operation",
            choices=[
                "start-migration",
                "generate-rm-configs",
                "generate-lookups",
                "test-lookups",
                "write-v4-json",
                "write-v4-relations",
                "convert-v3-skos",
            ],
        )

        parser.add_argument(
            "-m",
            "--resource-models",
            nargs="+",
            action="store",
            default=["all"],
            dest="resource-models",
            help="List the names of resource models to process. By default, all are used",
        )

        parser.add_argument("-t", "--target", action="store", default=None, help="Location of v3 data directory.")

        parser.add_argument("-n", "--number", type=int, action="store", default=None, help="Limits the number of resources to load.")

        parser.add_argument(
            "-o", "--overwrite", action="store_true", default=False, help="Overwrite existing data with the output of this operation"
        )

        parser.add_argument(
            "-i",
            "--import",
            action="store_true",
            default=False,
            help="Force the import of the v4 json created with the write-v4-json operation",
        )

        parser.add_argument("--verbose", action="store_true", default=False, help="Enable verbose printing during operation.")

        parser.add_argument(
            "--exclude", nargs="+", action="store", default=[], help="List of resource ids (uuids) to exclude from the write process."
        )

        parser.add_argument("--only", nargs="+", action="store", default=[], help="List of specific resource ids (uuids) to use.")

        parser.add_argument(
            "--skip-file-check",
            action="store_true",
            default=False,
            help="Skips the check for the existence of uploaded files " "during the conversion process.",
        )

    def handle(self, *args, **options):

        if not options["target"]:
            try:
                dir_path = settings.PACKAGE_DIR
                if not os.path.isdir(dir_path):
                    print("\nCurrent PACKAGE_DIR value: " + settings.PACKAGE_DIR)
                    print("This directory does not exist.")
                    raise AttributeError
            except AttributeError:
                print(
                    "\nYou must correctly set PACKAGE_DIR in your project's "
                    "settings.py file, or use the -t/--target argument to indicate "
                    "the location of your package."
                )
                exit()
        else:
            dir_path = os.path.abspath(options["target"])
            if not os.path.isdir(dir_path):
                print("\nInvalid -t/--target value: " + options["target"] + "\n" "This must be a directory.")
                exit()

        op = options["operation"]
        ow = options["overwrite"]
        vb = options["verbose"]

        print("package directory: " + dir_path)

        if op == "start-migration":
            self.prepare_package(dir_path, overwrite=ow)

        if op == "generate-rm-configs":
            self.generate_rm_configs(dir_path)

        if op == "generate-lookups":
            self.generate_lookups(dir_path)

        if op == "test-lookups":
            self.test_lookups(dir_path)

        if op == "write-v4-json":
            resource_models = options["resource-models"]
            if "all" in resource_models:
                resource_graphs = Graph.objects.filter(isresource=True)
                models = [g.name for g in resource_graphs.exclude(name="Arches System Settings")]
            else:
                for rm in resource_models:
                    try:
                        graph = Graph.objects.get(name=rm)
                    except Graph.DoesNotExist:
                        print("invalid resource model name: {}".format(rm))
                        exit()
                models = resource_models

            self.write_v4_json(
                dir_path,
                models,
                direct_import=options["import"],
                truncate=options["number"],
                verbose=vb,
                exclude=options["exclude"],
                only=options["only"],
                skipfilecheck=options["skip_file_check"],
            )

        if op == "write-v4-relations":
            self.write_v4_relations(dir_path, direct_import=options["import"])

        if op == "convert-v3-skos":
            self.convert_v3_skos(dir_path, direct_import=options["import"], verbose=vb)

        if op == "register-files":
            self.register_uploaded_files()

    def prepare_package(self, full_path, overwrite=False):
        """
        Creates a directory structure that will be used throughout the v3 data
        import process. Also creates a blank v3topconcept_lookup file.
        """

        v3_dir = os.path.join(full_path, "v3data")

        if os.path.isdir(v3_dir) and overwrite:
            try:
                shutil.rmtree(v3_dir)
            except Exception as e:
                print(e)
                exit()
        elif os.path.isfile(v3_dir) and overwrite:
            try:
                os.remove(v3_dir)
            except Exception as e:
                print(e)
                exit()
        elif os.path.isdir(v3_dir) or os.path.isfile(v3_dir):
            print(
                "The v3data directory already exists at this location:\n    "
                "{}\nEither change your path, or re-run command with "
                "--overwrite to replace the existing file or directory.".format(v3_dir)
            )
            exit()

        print("making directory")

        os.mkdir(v3_dir)
        os.mkdir(os.path.join(v3_dir, "business_data"))
        os.mkdir(os.path.join(v3_dir, "reference_data"))
        os.mkdir(os.path.join(v3_dir, "graph_data"))

        with open(os.path.join(full_path, "reference_data", "v3topconcept_lookup.json"), "w") as openfile:
            json.dump({}, openfile)

    def generate_rm_configs(self, pkg_path):
        """generate the template for the rm_configs.json file."""

        rm_dir = os.path.join(pkg_path, "graphs", "resource_models")
        graph_files = glob(os.path.join(rm_dir, "*.json"))
        graph_names = [os.path.splitext(os.path.basename(i))[0] for i in graph_files]
        configs = {}
        for name in graph_names:
            configs[name] = {
                "v3_entitytypeid": "<fill out manually>",
                "v3_nodes_csv": "<run 'python manage.py v3 generate-lookups'>",
                "v3_v4_node_lookup": "<run 'python manage.py v3 generate-lookups'>",
            }

        v3_dir = os.path.join(pkg_path, "v3data")
        with open(os.path.join(v3_dir, "rm_configs.json"), "w") as openfile:
            json.dump(configs, openfile, indent=4, sort_keys=True)

    def generate_lookups(self, path):

        # load configs in order to alter them
        config_file = os.path.join(path, "v3data", "rm_configs.json")
        with open(config_file, "rb") as openfile:
            configs = json.load(openfile)

        for rm, config in configs.items():
            v3_type = config["v3_entitytypeid"]
            if v3_type.startswith("<") or v3_type.endswith(">"):
                print("you must fill out the 'v3_entitytypeid' attribute " "for every resource model listed in your v3 configs.")
                exit()
        csv_dir = os.path.join(path, "v3data", "graph_data")

        for rm, config in configs.items():
            v3_type = config["v3_entitytypeid"]
            csv_file = os.path.join(csv_dir, "{}_nodes.csv".format(v3_type))
            if not os.path.isfile(csv_file):
                print("\nCan't find nodes CSV file for {}. Expected name is:" "\n\n  {}".format(v3_type, csv_file))
                print("\n  -- Have you transferred your v3 nodes files yet?")
                exit()

            v3_business_nodes = []
            with open(csv_file, "r") as opencsv:
                reader = csv.DictReader(opencsv)
                for row in reader:
                    if row["businesstable"].rstrip() == "":
                        continue
                    if row["Label"].endswith(".E32"):
                        continue

                    v3_business_nodes.append(row["Label"])
            v3_business_nodes.sort()

            lookup_file = csv_file.replace("_nodes.csv", "_v4_lookup.csv")
            with open(lookup_file, "w") as openfile:
                writer = csv.writer(openfile)
                writer.writerow(["v3_node", "v4_node"])
                for node in v3_business_nodes:
                    writer.writerow([node, ""])

            config["v3_nodes_csv"] = os.path.basename(csv_file)
            config["v3_v4_node_lookup"] = os.path.basename(lookup_file)

        with open(config_file, "w") as openfile:
            json.dump(configs, openfile, indent=4, sort_keys=True)

    def test_lookups(self, package_dir):

        v3_data_dir = os.path.join(package_dir, "v3data")
        errors = v3utils.test_rm_configs(v3_data_dir)
        if len(errors) > 0:
            print("FAIL")
            for e in errors:
                print(e)
            exit()

        print("PASS")

    def write_v4_json(
        self, package_dir, resource_models, direct_import=False, truncate=None, verbose=False, exclude=[], only=[], skipfilecheck=False
    ):

        start = datetime.now()
        v3_data_dir = os.path.join(package_dir, "v3data")
        endmsg = "\n  -- You can load these resources later with:\n"

        # get all json and jsonl files in the business_data directory
        v3_files = glob(os.path.join(package_dir, "v3data", "business_data", "*.json*"))

        if len(v3_files) == 0:
            print("\nThere is no v3 data to import. Put v3 json or jsonl in {}".format(v3_data_dir))
            exit()

        try:
            if os.path.isfile(only[0]):
                print("using resource ids from file")
                onlyids = list()
                with open(only[0], "rb") as f:
                    for line in f.readlines():
                        onlyids.append(line.rstrip())
                only = onlyids
        except Exception as e:
            pass

        if len(only) > 0:
            print("  processing {} resources".format(len(only)))

        sources = []

        # in the process of adjusting this to not only take multiple business_data
        # files, but also to accept and process jsonl files.
        for v3_file in v3_files:
            infilename = os.path.basename(v3_file)
            print("\n -- Processing " + infilename + " --")
            ext = os.path.splitext(v3_file)[1]

            for rm in resource_models:

                print("looking for " + rm + " resources...")
                value_converter = DataValueConverter(skip_file_check=skipfilecheck)

                importer = v3Importer(
                    v3_data_dir,
                    rm,
                    v3_resource_file=v3_file,
                    truncate=truncate,
                    exclude=exclude,
                    only=only,
                    verbose=verbose,
                    dt_converter=value_converter,
                )

                outfilename = os.path.splitext(infilename)[0] + "-" + rm + os.path.splitext(infilename)[1]
                output_file = os.path.join(package_dir, "business_data", outfilename)

                if ext == ".json":
                    output = importer.write_v4_json(output_file)
                elif ext == ".jsonl":
                    output = importer.write_v4_jsonl(output_file)

                if output is not False:
                    sources.append(output_file)
                    endmsg += "\n  python manage.py packages -o import_business_data -s " '"{}" -ow overwrite'.format(output)

        if direct_import:
            for source in sources:
                management.call_command("packages", operation="import_business_data", source=source, overwrite="overwrite")

        else:
            print(endmsg + "\n")

        print("elapsed time: {}".format(datetime.now() - start))

    def write_v4_relations(self, package_dir, direct_import=False):

        start = datetime.now()
        v3_business_dir = os.path.join(package_dir, "v3data", "business_data")
        v3_relations_files = glob(os.path.join(v3_business_dir, "*.relations"))

        if len(v3_relations_files) == 0:
            print("\nThere are no v3 relations to import. Put v3 .relations " "file in {}".format(v3_business_dir))
            exit()

        v3_relations = v3_relations_files[0]

        if len(v3_relations_files) > 1:
            print("\nOnly one v3 relations file can be imported. This file will be used" ":\n\n  {}".format(v3_relations))

        v4_relations = os.path.join(package_dir, "business_data", "relations", "all.relations")

        with open(v3_relations, "r") as openv3:
            reader = csv.reader(openv3, delimiter="|")
            next(reader)
            with open(v4_relations, "w") as openv4:
                writer = csv.writer(openv4)
                writer.writerow(["resourceinstanceidfrom", "resourceinstanceidto", "relationshiptype", "datestarted", "dateended", "notes"])
                for row in reader:
                    resfrom, resto, resstart, resend, restype, notes = row
                    writer.writerow([resfrom, resto, restype, resstart, resend, notes])

        if direct_import:
            management.call_command("packages", operation="import_business_data_relations", source=v4_relations)
        else:
            print(
                "\n  -- You can load these resources later with:\n"
                "\n  python manage.py packages -o import_business_data_relations -s "
                '"{}"'.format(v4_relations)
            )

        print("elapsed time: {}".format(datetime.now() - start))

    def convert_v3_skos(self, package_dir, direct_import=False, verbose=False):

        uuid_collection_file = os.path.join(package_dir, "reference_data", "v3topconcept_lookup.json")
        if not os.path.isfile(uuid_collection_file):
            if verbose:
                print("creating new collection lookup file: " + uuid_collection_file)
            with open(uuid_collection_file, "wb") as openfile:
                json.dump({}, openfile)
        try:
            if verbose:
                print("using existing collection lookup file: " + uuid_collection_file)
            with open(uuid_collection_file, "rb") as openfile:
                uuid_data = json.loads(openfile.read())
        except ValueError as e:
            print("\n  -- JSON parse error in " + uuid_collection_file + ":\n\n    " + e.message)
            exit()

        v3_ref_dir = os.path.join(package_dir, "v3data", "reference_data")
        v4_ref_dir = os.path.join(package_dir, "reference_data")

        v3_skos_files = glob(os.path.join(v3_ref_dir, "*.xml"))
        if len(v3_skos_files) == 0:
            print("\nThere is no v3 data to import. Export your concept scheme" " from v3 and place it in {}".format(v3_ref_dir))
            exit()

        if len(v3_skos_files) > 0:
            skos_file = v3_skos_files[0]

        if len(v3_skos_files) > 1:
            print("\nOnly one v3 file can be converted. This file will be used" ":\n\n  {}".format(skos_file))

        skos_importer = v3SkosConverter(
            skos_file, name_space=settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT, uuid_lookup=uuid_data, verbose=verbose
        )
        skos_importer.write_skos(v4_ref_dir)
        skos_importer.write_uuid_lookup(uuid_collection_file)

        if direct_import:

            theaurus_file = os.path.join(v4_ref_dir, "concepts", "thesaurus.xml")
            collection_file = os.path.join(v4_ref_dir, "collections", "collections.xml")
            for skosfile in [theaurus_file, collection_file]:
                skos = SKOSReader()
                rdf = skos.read_file(skosfile)
                ret = skos.save_concepts_from_skos(rdf, "overwrite", "keep")
