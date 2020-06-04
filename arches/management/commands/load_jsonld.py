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
import arches.app.utils.index_database as index_database
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.search.search_engine_factory import SearchEngineFactory

from arches.app.models.system_settings import settings


try:
    graph_uuid_map = settings.MODEL_NAME_UUID_MAP
except:
    graph_uuid_map = {}

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
            "-s", "--source",
            default="data/",
            action="store",
            dest="source",
            help="the directory in which the data files are to be found"
        )

        parser.add_argument(
            "-f", "--force", 
            default=False,
            action="store_true", 
            dest="force", 
            help='reload records that already exist'
        )

        parser.add_argument(
            "--toobig",
            default=0,
            type=int,
            action="store",
            dest="toobig",
            help="Do not attempt to load records > n kb"
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
            "--max",
            default=-1,
            type=int,
            action="store",
            dest="max",
            help="Maximum number of records to load per model"
            )

        parser.add_argument(
            "--fast",
            default=0,
            action="store",
            type=int,
            dest="fast",
            help="Use bulk_save to store n records at a time"
        )

        parser.add_argument(
            "-q", "--quiet",
            default=False,
            action="store_true",
            dest="quiet",
            help="Don't announce every record"
        )

        parser.add_argument(
            "--skip",
            default=-1,
            type=int,
            action="store",
            dest="skip",
            help="Number of records to skip before starting to load"
        )

        parser.add_argument(
            "--suffix",
            default="json",
            action="store",
            dest="suffix",
            help="file suffix to load"
            )

    def handle(self, *args, **options):

        print("Starting JSON-LD load")
        if options['model']:
            print(f"Only loading {options['model']}")
        if options['block']:
            print(f"Only loading {options['block']}")
        if options['force']:
            print("Forcing reload of existing records")
        if options['toobig']:
            print(f"Not loading records > {options['toobig']}kb")
        if options['quiet']:
            print("Only announcing timing data")
        self.resources = []
        self.load_resources(source=options['source'], force=options['force'], model=options['model'], block=options['block'], 
            maxx=options['max'], toobig=options['toobig'], fast=options['fast'], 
            quiet=options['quiet'], skip=options['skip'], suffix=options['suffix'])

    def load_resources(self, source, force, model, block, maxx, toobig, fast, quiet, skip, suffix):

        self.reader = JsonLdReader()

        if model:
            models = [model]
        else:
            models = os.listdir(source)
            models.sort()

        print(f"Found models: {models}")

        self.searchengine_factory = SearchEngineFactory().create()
        self.datatype_factory = DataTypeFactory()
        self.node_datatypes = {str(nodeid): datatype for nodeid, datatype in archesmodels.Node.objects.values_list("nodeid", "datatype")}

        errh = open("error_log.txt", 'w')
        start = time.time()
        x = 0
        for m in models:
            if not m.startswith('_') and not m.startswith('.'):
                print(f"Loading {m}")
                graphid = graph_uuid_map.get(m, None)
                if not graphid:
                    try:
                        graphid = archesmodels.GraphModel.objects.get(slug=m).pk
                    except:
                        print(f"Couldn't find a model definition for {m}; skipping")
                        continue

                # We have a good model, so build the pre-processed tree once
                self.reader.graphtree = self.reader.process_graph(graphid)
                if block and not ',' in block:
                    blocks = [block]
                else:
                    blocks = os.listdir(f"{source}/{m}")
                    blocks.sort()
                    if ',' in block:
                        # {slice},{max-slices}
                        (cslice, mslice) = block.split(',')
                        cslice = int(cslice)-1
                        mslice = int(mslice)
                        blocks = blocks[cslice::mslice]

                x = 0
                try:
                    for b in blocks:
                        files = os.listdir(f"{source}/{m}/{b}")
                        files.sort()
                        for f in files:
                            if not f.endswith(suffix):
                                continue

                            if maxx > 0 and x >= maxx:
                                raise StopIteration()
                            x += 1
                            if x < skip:
                                # Do it this way to keep the counts correct
                                continue
                            fn = f"{source}/{m}/{b}/{f}"
                            # Check file size of record
                            if not quiet:
                                print(f"About to import {fn}")
                            if toobig:
                                sz = os.os.path.getsize(fn)
                                if sz > toobig:
                                    if not quiet:
                                        print(f" ... Skipping due to size:  {sz} > {toobig}")
                                    continue
                            uu = f.replace(f".{suffix}", '')
                            fh = open(fn)
                            data = fh.read()
                            fh.close()
                            data = data.replace("T00:00:00Z", "")
                            jsdata = json.loads(data)
                            jsdata = fix_js_data(data, jsdata, m)
                            if len(uu) != 36 or uu[8] != "-":
                                # extract uuid from data
                                uu = jsdata['id'][-36:]
                            if jsdata:
                                try:
                                    if fast:
                                        self.fast_import_resource(uu, graphid, jsdata, n=fast, reload=force, quiet=quiet)
                                    else:
                                        self.import_resource(uu, graphid, jsdata, reload=force, quiet=quiet)
                                except Exception as e:
                                    errh.write(f"*** Failed to load {fn}:\n     {e}\n")
                                    errh.flush()
                                    raise
                            else:
                                print(" ... skipped due to bad data :(")
                            if not x % 100:
                                print(f" ... {x} in {time.time()-start}")
                except StopIteration as e:
                    break
                except:
                    raise
        if fast and self.resources:
            self.save_resources()
            self.index_resources()
            self.resources = []
        #if 0:
        #    # This should index in ES
        #    index_database.index_resources(clear_index=True, batch_size=settings.BULK_IMPORT_BATCH_SIZE)

        errh.close()
        print(f"duration: {x} in {time.time()-start} seconds")


    def save_resources(self):
        tiles = []
        for resource in self.resources:
            resource.tiles = resource.get_flattened_tiles()
            tiles.extend(resource.tiles)        

        Resource.objects.bulk_create(self.resources)
        TileModel.objects.bulk_create(tiles)

        for resource in self.resources:
            resource.save_edit(edit_type="create")

    def index_resources(self):

        se = self.searchengine_factory
        documents = []
        term_list = []

        for resource in self.resources:
            document, terms = resource.get_documents_to_index(
                fetchTiles=False, datatype_factory=self.datatype_factory, node_datatypes=self.node_datatypes)
            documents.append(se.create_bulk_item(index="resources", id=document["resourceinstanceid"], data=document))
            for term in terms:
                term_list.append(se.create_bulk_item(index="terms", id=term["_id"], data=term["_source"]))
        se.bulk_index(documents)
        se.bulk_index(term_list)        

    def fast_import_resource(self, resourceid, graphid, data, n=1000, reload=False, quiet=True):

        if not reload:
            try:
                resource_instance = Resource.objects.get(pk=resourceid)            
                if not reload:
                    if not quiet:
                        print(f" ... already loaded")
                    return
                else:
                    resource_instance.delete()
            except archesmodels.ResourceInstance.DoesNotExist:
                # thrown by get when resource doesn't exist
                pass

        try:
            self.reader.read_resource(data, resourceid=resourceid, graphid=graphid)
            self.resources.extend(self.reader.resources)
        except Exception as e:
            raise

        if len(self.resources) >= n:
            self.save_resources()
            self.index_resources()
            self.resources = []

    def import_resource(self, resourceid, graphid, data, reload=False, quiet=False):

        with transaction.atomic():
            try:
                resource_instance = Resource.objects.get(pk=resourceid)            
                if not reload:
                    print(f" ... already loaded")
                    return
                else:
                    resource_instance.delete()
            except archesmodels.ResourceInstance.DoesNotExist:
                # thrown by get when resource doesn't exist
                pass
            try:
                self.reader.read_resource(data, resourceid=resourceid, graphid=graphid)
                for resource in self.reader.resources:
                    resource.save(request=None)
            except archesmodels.ResourceInstance.DoesNotExist:
                print(f"*** Could not find model: {graphid}")
            except Exception as e:
                raise

