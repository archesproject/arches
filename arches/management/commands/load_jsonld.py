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

from arches.app.models import models as archesmodels
from django.core.management.base import BaseCommand
from django.db import transaction
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
            "-s", "--source", default="data/", action="store", dest="source", help="the directory in which the data files are to be found"
        )

        parser.add_argument(
            "-ow",
            "--overwrite",
            default="ignore",
            action="store",
            dest="force",
            help="if overwrite, overwrite records that exist; if ignore, then skip; if error, then halt",
        )

        parser.add_argument("--toobig", default=0, type=int, action="store", dest="toobig", help="Do not attempt to load records > n kb")

        parser.add_argument(
            "-m", "--model", default="", action="store", dest="model", help="the name of the model path to load (eg auction_of_lot)",
        )

        parser.add_argument(
            "-b",
            "--block",
            default="",
            action="store",
            dest="block",
            help="the name of the block in the model path to load (eg 00), or slice in the form this,total (eg 1,5)",
        )

        parser.add_argument("--max", default=-1, type=int, action="store", dest="max", help="Maximum number of records to load per model")

        parser.add_argument("--fast", default=0, action="store", type=int, dest="fast", help="Use bulk_save to store n records at a time")

        parser.add_argument("-q", "--quiet", default=False, action="store_true", dest="quiet", help="Don't announce every record")

        parser.add_argument(
            "--skip", default=-1, type=int, action="store", dest="skip", help="Number of records to skip before starting to load"
        )

        parser.add_argument("--suffix", default="json", action="store", dest="suffix", help="file suffix to load if not .json")

        parser.add_argument(
            "--ignore-errors", default=False, action="store_true", dest="ignore_errors", help="Log but do not terminate on errors"
        )

        parser.add_argument(
            "--strip-issearchable",
            default=False,
            action="store_true",
            dest="strip_search",
            help="If a node is set to not be exposed to advanced search, then don't even index it",
        )

    def handle(self, *args, **options):

        print("Starting JSON-LD load")
        if options["model"]:
            print(f"Only loading {options['model']}")
        if options["block"]:
            print(f"Only loading {options['block']}")
        if options["force"] == "overwrite":
            print("Overwriting existing records")
        if options["toobig"]:
            print(f"Not loading records > {options['toobig']}kb")
        if options["quiet"]:
            print("Only announcing timing data")

        if options["strip_search"] and not options["fast"]:
            print("ERROR: stripping fields not exposed to advanced search only works in fast mode")
            return

        self.resources = []
        self.load_resources(options)

    def load_resources(self, options):

        self.reader = JsonLdReader()
        self.jss = JSONSerializer()
        source = options["source"]
        if options["model"]:
            models = [options["model"]]
        else:
            models = os.listdir(source)
            models.sort()
            models = [m for m in models if m[0] not in ["_", "."]]
        print(f"Found possible models: {models}")

        # This is boilerplate for any use of get_documents_to_index()
        # Need to add issearchable for strip_search option
        # Only calculate it once per load
        self.datatype_factory = DataTypeFactory()
        dt_instance_hash = {}
        self.node_info = {
            str(nodeid): {
                "datatype": dt_instance_hash.setdefault(datatype, self.datatype_factory.get_instance(datatype)),
                "issearchable": srch,
            }
            for nodeid, datatype, srch in archesmodels.Node.objects.values_list("nodeid", "datatype", "issearchable")
        }
        self.node_datatypes = {str(nodeid): datatype for nodeid, datatype in archesmodels.Node.objects.values_list("nodeid", "datatype")}

        start = time.time()
        seen = 0
        loaded = 0

        for m in models:
            print(f"Loading {m}")
            graphid = graph_uuid_map.get(m, None)
            if not graphid:
                # Check slug
                try:
                    graphid = archesmodels.GraphModel.objects.get(slug=m).pk
                except:
                    print(f"Couldn't find a model definition for {m}; skipping")
                    continue
            # We have a good model, so build the pre-processed tree once
            self.reader.graphtree = self.reader.process_graph(graphid)
            block = options["block"]
            if block and "," not in block:
                blocks = [block]
            else:
                blocks = os.listdir(f"{source}/{m}")
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
                    files = os.listdir(f"{source}/{m}/{b}")
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
                        fn = f"{source}/{m}/{b}/{f}"
                        # Check file size of record
                        if not options["quiet"]:
                            print(f"About to import {fn}")
                        if options["toobig"]:
                            sz = os.os.path.getsize(fn)
                            if sz > options["toobig"]:
                                if not quiet:
                                    print(f" ... Skipping due to size:  {sz} > {options['toobig']}")
                                continue
                        uu = f.replace(f".{options['suffix']}", "")
                        fh = open(fn)
                        data = fh.read()
                        fh.close()
                        # FIXME Timezone / DateTime Workaround
                        # FIXME The following line should be removed when #5669 / #6346 are closed
                        data = data.replace("T00:00:00Z", "")
                        jsdata = json.loads(data)
                        jsdata = fix_js_data(data, jsdata, m)
                        if len(uu) != 36 or uu[8] != "-":
                            # extract uuid from data if filename is not a UUID
                            uu = jsdata["id"][-36:]
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
                                    )
                                else:
                                    l = self.import_resource(uu, graphid, jsdata, reload=options["force"], quiet=options["quiet"])
                                loaded += l
                                loaded_model += l
                            except Exception as e:
                                print(f"*** Failed to load {fn}:\n     {e}\n")
                                if not options["ignore_errors"]:
                                    raise
                        else:
                            print(" ... skipped due to bad data :(")
                        if not seen % 100:
                            print(f" ... seen {seen} / loaded {loaded} in {time.time()-start}")
            except StopIteration as e:
                break
            except:
                raise
        if options["fast"] and self.resources:
            self.save_resources()
            self.index_resources(options["strip_search"])
            self.resources = []
        print(f"Total Time: seen {seen} / loaded {loaded} in {time.time()-start} seconds")

    def fast_import_resource(self, resourceid, graphid, data, n=1000, reload="ignore", quiet=True, strip_search=False):
        try:
            resource_instance = Resource.objects.get(pk=resourceid)
            if reload == "ignore":
                if not quiet:
                    print(f" ... already loaded")
                return 0
            elif reload == "error":
                print(f"*** Record exists for {resourceid}, and -ow is error")
                raise FileExistsError(resourceid)
            else:
                resource_instance.delete()
        except archesmodels.ResourceInstance.DoesNotExist:
            # thrown when resource doesn't exist
            pass
        try:
            self.reader.read_resource(data, resourceid=resourceid, graphid=graphid)
            self.resources.extend(self.reader.resources)
        except:
            print(f"Exception raised while reading {resourceid}...")
            raise
        if len(self.resources) >= n:
            self.save_resources()
            self.index_resources(strip_search)
            self.resources = []
        return 1

    def import_resource(self, resourceid, graphid, data, reload="ignore", quiet=False):
        with transaction.atomic():
            try:
                resource_instance = Resource.objects.get(pk=resourceid)
                if reload == "ignore":
                    if not quiet:
                        print(f" ... already loaded")
                    return 0
                elif reload == "error":
                    print(f"*** Record exists for {resourceid}, and -ow is error")
                    raise FileExistsError(resourceid)
                else:
                    resource_instance.delete()
            except archesmodels.ResourceInstance.DoesNotExist:
                # thrown when resource doesn't exist
                pass

            try:
                self.reader.read_resource(data, resourceid=resourceid, graphid=graphid)
                for resource in self.reader.resources:
                    resource.save(request=None)
            except archesmodels.ResourceInstance.DoesNotExist:
                print(f"*** Could not find model: {graphid}")
                return 0
            except Exception as e:
                raise
        return 1

    def save_resources(self):
        tiles = []
        for resource in self.resources:
            resource.tiles = resource.get_flattened_tiles()
            tiles.extend(resource.tiles)
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
                document, terms = monkey_get_documents_to_index(resource, node_info=self.node_info)
            else:
                document, terms = resource.get_documents_to_index(
                    fetchTiles=False, datatype_factory=self.datatype_factory, node_datatypes=self.node_datatypes
                )
            documents.append(se.create_bulk_item(index="resources", id=document["resourceinstanceid"], data=document))
            for term in terms:
                term_list.append(se.create_bulk_item(index="terms", id=term["_id"], data=term["_source"]))
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
    document["displayname"] = self.displayname
    document["displaydescription"] = self.displaydescription
    document["map_popup"] = self.map_popup
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
            if nodevalue not in ["", [], {}, None] and node_info[nodeid]["issearchable"]:
                datatype_instance = node_info[nodeid]["datatype"]
                datatype_instance.append_to_document(document, nodevalue, nodeid, tile)
                node_terms = datatype_instance.get_search_terms(nodevalue, nodeid)
                for index, term in enumerate(node_terms):
                    terms.append(
                        {
                            "_id": f"{nodeid}{tile.tileid}{index}",
                            "_source": {
                                "value": term,
                                "nodeid": nodeid,
                                "nodegroupid": tile.nodegroup_id,
                                "tileid": tile.tileid,
                                "resourceinstanceid": tile.resourceinstance_id,
                                "provisional": False,
                            },
                        }
                    )
    return document, terms
