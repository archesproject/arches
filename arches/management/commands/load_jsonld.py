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

import os
import json
import time
from pathlib import Path

from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.db import transaction

from arches.app.models import models as archesmodels
from arches.app.models.resource import Resource
from arches.app.utils.data_management.resources.formats.rdffile import JsonLdReader
from arches.app.models.models import TileModel
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.search.search_engine_factory import SearchEngineInstance
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.models.system_settings import settings


# This is a map of graph directory name to graph UUID
try:
    graph_uuid_map = settings.MODEL_NAME_UUID_MAP
except:
    graph_uuid_map = {}

# This is a function that will mutate the data before being loaded
try:
    fix_js_data = settings.JSON_LD_FIX_DATA_FUNCTION
except:

    def fix_js_data(data, jsdata, model):
        return jsdata


class Command(BaseCommand):
    """
    Command for importing JSON-LD data into Arches
    """

    def add_arguments(self, parser):

        parser.add_argument(
            "-s",
            "--source",
            default="data/",
            action="store",
            dest="source",
            help="the directory in which the data files are to be found",
        )

        parser.add_argument(
            "-ow",
            "--overwrite",
            default="ignore",
            action="store",
            dest="force",
            help="if overwrite, overwrite records that exist; if ignore, then skip; if error, then halt",
        )

        parser.add_argument(
            "--toobig",
            default=0,
            type=int,
            action="store",
            dest="toobig",
            help="Do not attempt to load records > n kb",
        )

        parser.add_argument(
            "-m",
            "--model",
            default="",
            action="store",
            dest="model",
            help="the name of the model path to load (eg auction_of_lot)",
        )

        parser.add_argument(
            "-b",
            "--block",
            default="",
            action="store",
            dest="block",
            help="the name of the block in the model path to load (eg 00), or slice in the form this,total (eg 1,5)",
        )

        parser.add_argument(
            "-tz",
            "--default-timezone",
            default="",
            action="store",
            dest="default_timezone",
            help="Sets the default timezone for data that does not contain a timezone.",
        )

        parser.add_argument(
            "--max",
            default=-1,
            type=int,
            action="store",
            dest="max",
            help="Maximum number of records to load per model",
        )

        parser.add_argument(
            "--fast",
            default=0,
            action="store",
            type=int,
            dest="fast",
            help="Use bulk_save to store n records at a time",
        )

        parser.add_argument(
            "-q",
            "--quiet",
            default=False,
            action="store_true",
            dest="quiet",
            help="Don't announce every record",
        )

        parser.add_argument(
            "--skip",
            default=-1,
            type=int,
            action="store",
            dest="skip",
            help="Number of records to skip before starting to load",
        )

        parser.add_argument(
            "--suffix",
            default="json",
            action="store",
            dest="suffix",
            help="file suffix to load if not .json",
        )

        parser.add_argument(
            "--ignore-errors",
            default=False,
            action="store_true",
            dest="ignore_errors",
            help="Log but do not terminate on errors",
        )

        parser.add_argument(
            "--strip-issearchable",
            default=False,
            action="store_true",
            dest="strip_search",
            help="If a node is set to not be exposed to advanced search, then don't even index it",
        )

        parser.add_argument(
            "--dry-run",
            default=False,
            action="store_true",
            dest="dry_run",
            help="Neither save nor index resources, but run all validation with requested logging.",
        )

        parser.add_argument(
            "--use-storage",
            default=False,
            action="store_true",
            dest="use_storage",
            help="Resolve filepaths against Django default_storage.",
        )

    def handle(self, *args, **options):

        self.stdout.write("Starting JSON-LD load")
        if options["model"]:
            self.stdout.write(f"Only loading {options['model']}")
        if options["block"]:
            self.stdout.write(f"Only loading {options['block']}")
        if options["force"] == "overwrite":
            self.stdout.write("Overwriting existing records")
        if options["toobig"]:
            self.stdout.write(f"Not loading records > {options['toobig']}kb")
        if options["quiet"]:
            self.stdout.write("Only announcing timing data")
        if options["default_timezone"]:
            self.stdout.write(
                f"Setting default timezone to: {options['default_timezone']}"
            )
        if options["verbosity"] > 1:
            self.stdout.write(
                "Logging detailed error information: set log level to DEBUG to view messages"
            )
            self.stdout.write(
                "Verbosity level 2 will log based on the application's LOGGING settings in settings.py"
            )
            self.stdout.write(
                "Verbosity level 3 will include level 2 logging as well as logging to the console"
            )
            resp = input(
                "Logging detailed information can slow down the import process.  Continue anyway? (y/n)"
            )

            if "n" in resp.lower():
                return

        if options["strip_search"] and not options["fast"]:
            self.stderr.write(
                "ERROR: stripping fields not exposed to advanced search only works in fast mode"
            )
            return

        if options["dry_run"]:
            self.stdout.write(
                "Running in --dry-run mode. Validating only (no saving, no indexing)."
            )

        self.resources = []
        self.load_resources(options)

        if options["dry_run"]:
            # Return the unused resources to the python caller.
            # Technically, you are only supposed to return a string,
            # so that it can be written to self.stdout, but if you
            # just patch out Django's write() call, you can do as you like.
            self.stdout.write = lambda unused: None
            return self.resources

    def load_resources(self, options):
        self.reader = JsonLdReader(
            verbosity=options["verbosity"],
            ignore_errors=options["ignore_errors"],
            default_timezone=options["default_timezone"],
        )
        self.jss = JSONSerializer()
        source = options["source"]
        if options["model"]:
            models = [options["model"]]
        else:
            if options["use_storage"]:
                models = [default_storage.listdir(source)][0]
            else:
                models = os.listdir(source)
            models.sort()
            models = [m for m in models if m[0] not in ["_", "."]]
        self.stdout.write(f"Found possible models: {models}")

        # This is boilerplate for any use of get_documents_to_index()
        # Need to add issearchable for strip_search option
        # Only calculate it once per load
        self.datatype_factory = DataTypeFactory()
        dt_instance_hash = {}
        self.node_info = {
            str(nodeid): {
                "datatype": dt_instance_hash.setdefault(
                    datatype, self.datatype_factory.get_instance(datatype)
                ),
                "issearchable": srch,
            }
            for nodeid, datatype, srch in archesmodels.Node.objects.values_list(
                "nodeid", "datatype", "issearchable"
            )
        }
        self.node_datatypes = {
            str(nodeid): datatype
            for nodeid, datatype in archesmodels.Node.objects.values_list(
                "nodeid", "datatype"
            )
        }

        start = time.time()
        seen = 0
        loaded = 0

        for m in models:
            self.stdout.write(f"Loading {m}")
            model_path = Path(source) / m
            graphid = graph_uuid_map.get(m, None)
            if not graphid:
                # Check slug
                try:
                    graphid = archesmodels.GraphModel.objects.get(
                        slug=m, source_identifier=None
                    ).pk
                except:
                    self.stderr.write(
                        f"Couldn't find a model definition for {m}; skipping"
                    )
                    continue
            # We have a good model, so build the pre-processed tree once
            self.reader.graphtree = self.reader.process_graph(graphid)
            block = options["block"]
            if block and "," not in block:
                blocks = [block]
            else:
                if options["use_storage"]:
                    blocks = default_storage.listdir(model_path)[0]
                else:
                    blocks = os.listdir(model_path)
                blocks.sort()
                blocks = [b for b in blocks if b[0] not in ["_", "."]]
                if "," in block:
                    # {slice},{max-slices}
                    (cslice, mslice) = block.split(",")
                    cslice = int(cslice) - 1
                    mslice = int(mslice)
                    blocks = blocks[cslice::mslice]

            loaded_model = 0

            try:
                for b in blocks:
                    block_path = model_path / b
                    if options["use_storage"]:
                        files = default_storage.listdir(block_path)[1]
                    else:
                        files = os.listdir(block_path)
                    files.sort()
                    for f in files:
                        if not f.endswith(options["suffix"]):
                            continue
                        elif f.startswith(".") or f.startswith("_"):
                            continue

                        if options["max"] > 0 and loaded_model >= options["max"]:
                            raise StopIteration()
                        seen += 1
                        if seen <= options["skip"]:
                            # Do it this way to keep the counts correct
                            continue
                        fn = block_path / f
                        # Check file size of record
                        if not options["quiet"]:
                            self.stdout.write(f"About to import {fn}")
                        if options["toobig"]:
                            sz = os.os.path.getsize(fn)
                            if sz > options["toobig"]:
                                if not options["quiet"]:
                                    self.stdout.write(
                                        f" ... Skipping due to size:  {sz} > {options['toobig']}"
                                    )
                                continue
                        uu = f.replace(f".{options['suffix']}", "")
                        if options["use_storage"]:
                            with default_storage.open(fn, mode="r") as fh:
                                data = fh.read()
                        else:
                            with open(fn, mode="r") as fh:
                                data = fh.read()
                        # FIXME Timezone / DateTime Workaround
                        # FIXME The following line should be removed when #5669 / #6346 are closed
                        data = data.replace("T00:00:00Z", "")
                        jsdata = json.loads(data)
                        jsdata = fix_js_data(data, jsdata, m)
                        if len(uu) != 36 or uu[8] != "-":
                            # extract uuid from data if filename is not a UUID
                            uu = jsdata["@id"][-36:]
                        if jsdata:
                            try:
                                if options["fast"]:
                                    l = self.fast_import_resource(
                                        uu,
                                        graphid,
                                        jsdata,
                                        n=options["fast"],
                                        reload=options["force"],
                                        quiet=options["quiet"],
                                        strip_search=options["strip_search"],
                                        dry_run=options["dry_run"],
                                    )
                                else:
                                    l = self.import_resource(
                                        uu,
                                        graphid,
                                        jsdata,
                                        reload=options["force"],
                                        quiet=options["quiet"],
                                        dry_run=options["dry_run"],
                                    )
                                loaded += l
                                loaded_model += l
                            except Exception as e:
                                self.stderr.write(
                                    f"*** Failed to load {fn}:\n     {e}\n"
                                )
                                if not options["ignore_errors"]:
                                    short_path_to_failing_file = f"{Path(m) / b / f}"
                                    e.add_note(short_path_to_failing_file)
                                    raise
                        else:
                            self.stdout.write(" ... skipped due to bad data :(")
                        if not seen % 100:
                            self.stdout.write(
                                f" ... seen {seen} / loaded {loaded} in {time.time()-start}"
                            )
            except StopIteration as e:
                break
            except:
                raise

        if options["fast"] and not options["dry_run"] and self.resources:
            self.save_resources()
            self.index_resources(options["strip_search"])
            self.resources = []
        self.stdout.write(
            f"Total Time: seen {seen} / loaded {loaded} in {time.time()-start} seconds"
        )

    def fast_import_resource(
        self,
        resourceid,
        graphid,
        data,
        n=1000,
        reload="ignore",
        quiet=True,
        strip_search=False,
        dry_run=False,
    ):
        try:
            resource_instance = Resource.objects.get(pk=resourceid)
            if reload == "ignore":
                if not quiet:
                    self.stdout.write(f" ... already loaded")
                return 0
            elif reload == "error":
                self.stderr.write(
                    f"*** Record exists for {resourceid}, and -ow is error"
                )
                raise FileExistsError(resourceid)
            elif not dry_run:
                resource_instance.delete()
        except archesmodels.ResourceInstance.DoesNotExist:
            # thrown when resource doesn't exist
            pass
        try:
            self.reader.read_resource(data, resourceid=resourceid, graphid=graphid)
            self.resources.extend(self.reader.resources)
        except:
            self.stderr.write(f"Exception raised while reading {resourceid}...")
            raise
        if not dry_run and len(self.resources) >= n:
            self.save_resources()
            self.index_resources(strip_search)
            self.resources = []
        return 1

    def import_resource(
        self, resourceid, graphid, data, reload="ignore", quiet=False, dry_run=False
    ):
        with transaction.atomic():
            try:
                resource_instance = Resource.objects.get(pk=resourceid)
                if reload == "ignore":
                    if not quiet:
                        self.stdout.write(f" ... already loaded")
                    return 0
                elif reload == "error":
                    self.stdout.write(
                        f"*** Record exists for {resourceid}, and -ow is error"
                    )
                    raise FileExistsError(resourceid)
                else:
                    resource_instance.delete()
            except archesmodels.ResourceInstance.DoesNotExist:
                # thrown when resource doesn't exist
                pass

            try:
                self.reader.read_resource(data, resourceid=resourceid, graphid=graphid)
                if dry_run:
                    return 1
                for resource in self.reader.resources:
                    resource.save(request=None)
            except archesmodels.ResourceInstance.DoesNotExist:
                self.stderr.write(f"*** Could not find model: {graphid}")
                return 0
            except Exception as e:
                raise
        return 1

    def save_resources(self):
        tiles = []
        for resource in self.resources:
            resource.tiles = resource.get_flattened_tiles()
            tiles.extend(resource.tiles)

            if not hasattr(resource, "resource_instance_lifecycle_state"):
                resource.resource_instance_lifecycle_state = (
                    resource.get_initial_resource_instance_lifecycle_state()
                )

        Resource.objects.bulk_create(self.resources)
        TileModel.objects.bulk_create(tiles)
        for t in tiles:
            for nodeid in t.data.keys():
                datatype = self.node_info[nodeid]["datatype"]
                datatype.pre_tile_save(t, nodeid)
        for resource in self.resources:
            resource.save_edit(edit_type="create")

    def index_resources(self, strip_search=False):
        se = SearchEngineInstance
        documents = []
        term_list = []
        for resource in self.resources:
            if strip_search:
                document, terms = monkey_get_documents_to_index(
                    resource, node_info=self.node_info
                )
            else:
                document, terms = resource.get_documents_to_index(
                    fetchTiles=False,
                    datatype_factory=self.datatype_factory,
                    node_datatypes=self.node_datatypes,
                )
            documents.append(
                se.create_bulk_item(
                    index="resources", id=document["resourceinstanceid"], data=document
                )
            )
            for term in terms:
                term_list.append(
                    se.create_bulk_item(
                        index="terms", id=term["_id"], data=term["_source"]
                    )
                )
        se.bulk_index(documents)
        se.bulk_index(term_list)


def monkey_get_documents_to_index(self, node_info):
    document = {}
    document["displaydescription"] = None
    document["resourceinstanceid"] = str(self.resourceinstanceid)
    document["graph_id"] = str(self.graph_id)
    document["map_popup"] = None
    document["displayname"] = None
    document["root_ontology_class"] = self.get_root_ontology()
    document["legacyid"] = self.legacyid
    document["displayname"] = self.displayname()
    document["displaydescription"] = self.displaydescription()
    document["map_popup"] = self.map_popup()
    document["tiles"] = self.tiles
    document["permissions"] = {"users_without_read_perm": []}
    document["permissions"]["users_without_edit_perm"] = []
    document["permissions"]["users_without_delete_perm"] = []
    document["permissions"]["users_with_no_access"] = []
    document["strings"] = []
    document["dates"] = []
    document["domains"] = []
    document["geometries"] = []
    document["points"] = []
    document["numbers"] = []
    document["date_ranges"] = []
    document["ids"] = []
    document["provisional_resource"] = "false"

    terms = []
    for tile in document["tiles"]:
        for nodeid, nodevalue in tile.data.items():
            # filter out not issearchable
            if (
                nodevalue not in ["", [], {}, None]
                and node_info[nodeid]["issearchable"]
            ):
                datatype_instance = node_info[nodeid]["datatype"]
                datatype_instance.append_to_document(document, nodevalue, nodeid, tile)
                node_terms = datatype_instance.get_search_terms(nodevalue, nodeid)
                for index, term in enumerate(node_terms):
                    terms.append(
                        {
                            "_id": f"{nodeid}{tile.tileid}{index}",
                            "_source": {
                                "value": term.value,
                                "nodeid": nodeid,
                                "nodegroupid": tile.nodegroup_id,
                                "tileid": tile.tileid,
                                "language": term.lang,
                                "resourceinstanceid": tile.resourceinstance_id,
                                "provisional": False,
                            },
                        }
                    )
    return document, terms
