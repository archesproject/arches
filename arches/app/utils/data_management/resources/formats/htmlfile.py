#import csv
#import pickle
#import datetime
#import json
import os
#import sys
#import uuid
#import traceback
import logging
#from time import time
#from copy import deepcopy
from io import StringIO
from .format import Writer
from .format import Reader
#from elasticsearch import TransportError
from arches.app.models.tile import Tile
from arches.app.models.concept import Concept
from arches.app.models.models import (
    GraphModel,
    Node,
    NodeGroup,
    ResourceXResource,
    ResourceInstance,
    FunctionXGraph,
    GraphXMapping,
    TileModel,
)
from arches.app.models.card import Card
from arches.app.models.graph import Graph

#from arches.app.utils.data_management.resource_graphs import exporter as GraphExporter
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from arches.app.datatypes.datatypes import DataTypeFactory
import arches.app.utils.task_management as task_management
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from django.utils.translation import ugettext as _

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


class HtmlWriter(Writer):
    def __init__(self, **kwargs):
        super(HtmlWriter, self).__init__(**kwargs)
        self.templates_dir = "C:/Development/repos/keystone/arches-her/arches_her/export_report_templates" #hardcoded for development

    def fetch_resource_objects_list(self,resourceinstanceids=None, user=None, allowed_graph_ids=None):
        """
            returns a dict containing graph_id keyed lists containing json ready resource objects
            
            {
                "<graph_id>": [
                    {<disambiguated resource object>}
                ],
                "<graph_id>": [
                    {<disambiguated resource object>}
                ],
                ...
                ...
            }

            NOTE: much was taken from api.Resources.get ln 557
        """
        
        perm = "read_nodegroup"
        resources = Resource.objects.filter(pk__in=resourceinstanceids)
        compact = True #bool(request.GET.get("compact", "true").lower() == "true")  # default True
        hide_empty_nodes = False #bool(request.GET.get("hide_empty_nodes", "false").lower() == "true")  # default False
        resource_lists = {}
        for resource in resources:
            gid = str(resource.graph_id)
            if gid in allowed_graph_ids:
                out = {
                    "resource": resource.to_json(
                        compact=compact,
                        hide_empty_nodes=hide_empty_nodes,
                        user=user,
                        perm=perm,
                    ),
                    "displaydescription": resource.displaydescription,
                    "displayname": resource.displayname,
                    "graph_id": resource.graph_id,
                    "legacyid": resource.legacyid,
                    "map_popup": resource.map_popup,
                    "resourceinstanceid": resource.resourceinstanceid,
                }
                
                if gid not in resource_lists.keys():
                    resource_lists[gid] = []
                resource_lists[gid].append(out)

        return resource_lists


    def write_resources(self, graph_id=None, resourceinstanceids=None, **kwargs):
        """
            Returns a list of dictionaries with the following format:
            [
                {'name':file name, 'outputfile': a StringIO() buffer of resource instance data in the specified format},
                {'name':file name, 'outputfile': a StringIO()},
                ...
                ...
            ]
        """
        user = kwargs.get("user", None)
        logger.debug("Starting HTML export")
        logger.debug("... Fetching JSON")

        # get list of templates ()
        from pathlib import Path
        valid_graphs = []
        for filename in os.listdir(self.templates_dir):
            valid_graphs.append(Path(filename).stem)

        resources_list = self.fetch_resource_objects_list(resourceinstanceids=resourceinstanceids, user=user, allowed_graph_ids=valid_graphs)
        
        logger.debug("...Fetched")
        logger.debug("... building html")

        files = self.generate_html_files(resources_list)
        
        logger.debug("... built")
        logger.debug("Finished HTML export")
        return files
    
    def generate_html_files(self, resource_object_list=None):
        """
            "b9e0701e-5463-11e9-b5f5-000d3ab1e588"	"Activity"
            "42ce82f6-83bf-11ea-b1e8-f875a44e0e11"	"Application Area"
            "b07cfa6f-894d-11ea-82aa-f875a44e0e11"	"Archive Source"
            "343cc20c-2c5a-11e8-90fa-0242ac120005"	"Artefact"
            "24d7b54f-5464-11e9-a86b-000d3ab1e588"	"Bibliographic Source"
            "8d41e49e-a250-11e9-9eab-00224800b26d"	"Consultation"
            "a535a235-8481-11ea-a6b9-f875a44e0e11"	"Digital Object"
            "979aaf0b-7042-11ea-9674-287fcf6a5e72"	"Heritage Area"
            "076f9381-7b00-11e9-8d6b-80000b44d1d9"	"Heritage Asset"
            "0add0e11-99aa-11ea-9ab8-f875a44e0e11"	"Heritage Story"
            "b8032b00-594d-11e9-9cf0-18cf5eb368c4"	"Historic Aircraft"
            "934cd7f0-480a-11ea-9240-c4d9877d154e"	"Historic Landscape Characterization"
            "49bac32e-5464-11e9-a6e2-000d3ab1e588"	"Maritime Vessel"
            "d4a88461-5463-11e9-90d9-000d3ab1e588"	"Organization"
            "f9045867-8861-11ea-b06f-f875a44e0e11"	"Period"
            "22477f01-1a44-11e9-b0a9-000d3ab1e588"	"Person"
            "78b32d8c-b6f2-11ea-af42-f875a44e0e11"	"Place"
            "cf3a2979-f1aa-11e8-9f5d-022b22146258"	"Radiocarbon Date"
        """
        
        
        
        files = []
        for gid in resource_object_list.keys():
            template = self.load_template(gid)
            dest = StringIO()
            dest.write(template.render(
                    resources = resource_object_list[gid]
                ))
            
            files.append({"name": f"{str(GraphModel.objects.get(pk=gid))}.html", "outputfile": dest})
        
        return files

    def load_template(self, graph_id=None):
            env = Environment( loader = FileSystemLoader(self.templates_dir) )
            template = env.get_template(f"{graph_id}.html")
            return template

 