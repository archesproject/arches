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
from arches.app.utils import v3utils
from arches.app.utils.v3migration import v3Importer, v3SkosConverter
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.models.system_settings import settings
settings.update_from_db()

class Command(BaseCommand):
    """
    This is a suite of operations that provide the ability to migrate v3 data
    to v4 through the command line.
    """

    def add_arguments(self, parser):

        parser.add_argument('operation', choices=[
            'start-migration',
            'generate-lookups',
            'write-v4-json',
            'write-v4-relations',
            'convert-v3-skos',
            ]
        )

        parser.add_argument('-m', '--resource-models', nargs="+", action='store', default=['all'],
            dest="resource-models",
            help='List the names of resource models to process. By default, all are used')

        parser.add_argument('-t', '--target', action='store', default=None,
            help='Location of v3 data directory.')

        parser.add_argument('-n', '--number', type=int, action='store', default=None,
            help='Limits the number of resources to load.')

        parser.add_argument('-o', '--overwrite', action='store_true', default=False,
            help='Overwrite existing data with the output of this operation')

        parser.add_argument('-i', '--import', action='store_true', default=False,
            help='Force the import of the v4 json created with the write-v4-json operation')

        parser.add_argument('--verbose', action='store_true', default=False,
            help='Enable verbose printing during operation.')

        parser.add_argument('--exclude', nargs="+", action='store', default=[],
            help='List of resource ids (uuids) to exclude from the write process.')

    def handle(self, *args, **options):

        if not options['target']:
            try:
                dir_path = settings.PACKAGE_DIR
                if not os.path.isdir(dir_path):
                    print "\nCurrent PACKAGE_DIR value: "+settings.PACKAGE_DIR
                    raise AttributeError
            except AttributeError:
                print "\nYou must correctly set PACKAGE_DIR in your project's "\
                "settings.py file, or use the -t/--target argument to indicate"\
                " the location of your package."
                exit()
        else:
            dir_path = os.path.abspath(options['target'])
            if not os.path.isdir(dir_path):
                print "\nInvalid -t/--target value: "+options['target']+"\n"\
                "This must be a directory."
                exit()

        op = options['operation']
        ow = options['overwrite']
        vb = options['verbose']

        if op == 'start-migration':
            self.create_v3_directory(dir_path,overwrite=ow)

        if op == 'generate-lookups':
            self.generate_lookups(dir_path,overwrite=ow)

        if op == 'write-v4-json':
            resource_models = options['resource-models']
            if "all" in resource_models:
                resource_graphs = Graph.objects.filter(isresource=True)
                models = [g.name for g in resource_graphs.exclude(
                    name="Arches System Settings")
                ]
            else:
                for rm in resource_models:
                    try:
                        graph = Graph.objects.get(name=rm)
                    except Graph.DoesNotExist:
                        print "invalid resource model name:",rm
                        exit()
                models = resource_models

            self.write_v4_json(dir_path,models,
                direct_import=options['import'],
                truncate=options['number'],
                verbose=vb,
                exclude=options['exclude']
            )
        if op == 'write-v4-relations':
            self.write_v4_relations(dir_path,direct_import=options['import'])

        if op == 'convert-v3-skos':
            self.convert_v3_skos(dir_path)
            
        if op == 'register-files':
            self.register_uploaded_files()

    def create_v3_directory(self, full_path, overwrite=False):
        """
        Creates a directory structure that will be used throughout the v3 data
        import process. Populates with some content based on existing installation.
        """

        v3_dir = os.path.join(full_path,"v3data")

        if os.path.isdir(v3_dir) and overwrite:
            try:
                shutil.rmtree(v3_dir)
            except Exception as e:
                print e
                exit()
        elif os.path.isfile(v3_dir) and overwrite:
            try:
                os.remove(v3_dir)
            except Exception as e:
                print e
                exit()
        elif os.path.isdir(v3_dir) or os.path.isfile(v3_dir):
            print "The v3data directory exists at this location:\n    "\
            +v3_dir+"\nEither change your path, or re-run command with "\
            "--overwrite to replace the existing file or directory."
            exit()

        print "making directory"

        os.mkdir(v3_dir)
        os.mkdir(os.path.join(v3_dir,'business_data'))
        os.mkdir(os.path.join(v3_dir,'reference_data'))
        os.mkdir(os.path.join(v3_dir,'graph_data'))

        rm_dir = os.path.join(full_path,"graphs","resource_models")
        graph_files = glob(os.path.join(rm_dir,"*.json"))
        graph_names = [os.path.splitext(os.path.basename(i))[0] for i in graph_files]
        configs = {}
        for name in graph_names:
            configs[name] = {
                "v3_entitytypeid":"<fill out manually>",
                "v3_nodes_csv":"<run 'python manage.py v3data configs --generate_lookups'>",
                "v3_v4_node_lookup":"<run 'python manage.py v3data configs --generate_lookups'>",
            }

        with open(os.path.join(v3_dir,"rm_configs.json"),"wb") as openfile:
            json.dump(configs,openfile,indent=4,sort_keys=True)

    def generate_lookups(self,path,overwrite=False):

        ## load configs in order to alter them
        config_file = os.path.join(path,"v3data","rm_configs.json")
        with open(config_file,"rb") as openfile:
            configs = json.load(openfile)

        for rm, config in configs.iteritems():
            v3_type = config['v3_entitytypeid']
            if v3_type.startswith("<") or v3_type.endswith(">"):
                print "you must fill out the 'v3_entitytypeid' attribute "\
                "for every resource model listed in your v3 configs."
                exit()
        csv_dir = os.path.join(path,'v3data','graph_data')

        for rm, config in configs.iteritems():
            v3_type = config['v3_entitytypeid']
            csv_file = os.path.join(csv_dir,"{}_nodes.csv".format(v3_type))
            if not os.path.isfile(csv_file):
                print "\nCan't find nodes CSV file for {}. Expected name is:"\
                "\n\n  {}".format(v3_type,csv_file)
                print "\n  -- Have you transferred your v3 nodes files yet?"
                exit()

            v3_business_nodes = []
            with open(csv_file,'rb') as opencsv:
                reader = csv.DictReader(opencsv)
                for row in reader:
                    if row['businesstable'].rstrip() == "":
                        continue
                    if row['Label'].endswith(".E32"):
                        continue

                    v3_business_nodes.append(row['Label'])
            v3_business_nodes.sort()

            lookup_file = csv_file.replace("_nodes.csv","_v4_lookup.csv")
            with open(lookup_file,"wb") as openfile:
                writer = csv.writer(openfile)
                writer.writerow(['v3_node','v4_node'])
                for node in v3_business_nodes:
                    writer.writerow([node,''])

            config['v3_nodes_csv'] = os.path.basename(csv_file)
            config['v3_v4_node_lookup'] = os.path.basename(lookup_file)

        with open(config_file,"wb") as openfile:
            json.dump(configs,openfile,indent=4,sort_keys=True)

    def write_v4_json(self, package_dir, resource_models,
        direct_import=False, truncate=None, verbose=False, exclude=[]):

        v3_data_dir = os.path.join(package_dir,"v3data")
        endmsg = "\n  -- You can load these resources later with:\n"

        v3_files = glob(os.path.join(package_dir,'v3data','business_data','*.json'))
        if len(v3_files) == 0:
            print "\nThere is no v3 data to import. Put v3 json in {}".format(v3_data_dir)
            exit()

        business_data = v3_files[0]

        if len(v3_files) > 1:
            print "\nOnly one v3 file can be imported. This file will be used"\
                ":\n\n  {}".format(business_data)

        sources = []
        for rm in resource_models:

            print rm
            output_file = os.path.join(package_dir,'business_data',rm+".json")
            importer = v3Importer(v3_data_dir,rm,business_data,
                truncate=truncate,exclude=exclude)
            output = importer.write_v4_json(output_file,verbose=verbose)
            sources.append(output_file)
            endmsg += '\n  python manage.py packages -o import_business_data -s '\
                '"{}" -ow overwrite'.format(output)

        if direct_import:
            for source in sources:
                management.call_command("packages",
                    operation="import_business_data",
                    source=source,
                    overwrite="overwrite"
                )

        else:
            print endmsg+"\n"

    def write_v4_relations(self, package_dir, direct_import=False):

        v3_business_dir = os.path.join(package_dir,'v3data','business_data')
        v3_relations_files = glob(os.path.join(v3_business_dir,'*.relations'))

        if len(v3_relations_files) == 0:
            print "\nThere are no v3 relations to import. Put v3 .relations "\
                "file in {}".format(v3_business_dir)
            exit()

        v3_relations = v3_relations_files[0]

        if len(v3_relations_files) > 1:
            print "\nOnly one v3 relations file can be imported. This file will be used"\
                ":\n\n  {}".format(v3_relations)

        v4_relations = os.path.join(package_dir,"business_data","relations","all.relations")

        with open(v3_relations, "rb") as openv3:
            reader = csv.reader(openv3, delimiter="|")
            reader.next()
            with open(v4_relations, "wb") as openv4:
                writer = csv.writer(openv4)
                writer.writerow(['resourceinstanceidfrom','resourceinstanceidto',
                    'relationshiptype','datestarted','dateended','notes'])
                for row in reader:
                    resfrom, resto, resstart, resend, restype, notes = row
                    writer.writerow([resfrom,resto,restype,resstart,resend,notes])

        if direct_import:
            management.call_command("packages",
                operation="import_business_data_relations",
                source=v4_relations
            )
        else:
            print '\n  -- You can load these resources later with:\n'\
                '\n  python manage.py packages -o import_business_data_relations -s '\
                '"{}"'.format(v4_relations)

    def convert_v3_skos(self, package_dir):

        v3_ref_dir = os.path.join(package_dir,'v3data','reference_data')
        v4_ref_dir = os.path.join(package_dir,'reference_data')

        v3_skos_files = glob(os.path.join(v3_ref_dir,'*.xml'))
        if len(v3_skos_files) == 0:
            print "\nThere is no v3 data to import. Export your concept scheme"\
                " from v3 and place it in {}".format(v3_ref_dir)
            exit()

        if len(v3_skos_files) > 0:
            skos_file = v3_skos_files[0]

        if len(v3_skos_files) > 1:
            print "\nOnly one v3 file can be imported. This file will be used"\
                ":\n\n  {}".format(skos_file)

        uuid_collection_file = os.path.join(v3_ref_dir,"collection_uuids.json")
        if not os.path.isfile(uuid_collection_file):
            uuid_collection_file = None

        skos_importer = v3SkosConverter(skos_file,
            name_space=settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)
        skos_importer.write_skos(v4_ref_dir,uuid_collection_file=uuid_collection_file)
