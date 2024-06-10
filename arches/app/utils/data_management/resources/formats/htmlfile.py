import os
import logging
from functools import lru_cache
from uuid import UUID
from io import StringIO
from .format import Writer
from django.template import Context, Template, TemplateDoesNotExist
from django.template.loader import get_template
from arches.app.models.models import GraphModel
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from pathlib import Path


logger = logging.getLogger(__name__)


class HtmlWriter(Writer):
    def __init__(self, **kwargs):
        super(HtmlWriter, self).__init__(**kwargs)

    @staticmethod
    def get_graphids_with_export_template():
        """
        get a list of graphids that have html export templates available.
        """
        valid_graphs = []
        existing_graphids = GraphModel.objects.filter(isresource=True).values_list(
            "graphid", flat=True
        )
        for existing_graphid in existing_graphids:
            if HtmlWriter.has_html_template(existing_graphid):
                valid_graphs.append(str(existing_graphid))

        return valid_graphs

    @staticmethod
    @lru_cache(maxsize=None)
    def has_html_template(graphid=None):
        """
        Check an html template for the graph is available
        """
        result = False
        for extension in ("htm", "html"):
            try:
                path = os.path.join("html_export", str(graphid))
                get_template(f"{path}.{extension}")
                result = True
            except TemplateDoesNotExist as e:
                pass
        return result

    def load_html_template(self, graphid=None):
        template = None
        for extension in ("htm", "html"):
            try:
                path = os.path.join("html_export", str(graphid))
                template = get_template(f"{path}.{extension}")
                return template
            except TemplateDoesNotExist as e:
                pass
        return template

    def fetch_resource_objects_list(
        self, resourceinstanceids=None, user=None, allowed_graph_ids=None
    ):
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

        """

        perm = "read_nodegroup"
        resources = Resource.objects.filter(pk__in=resourceinstanceids)
        compact = True
        hide_empty_nodes = False
        resource_lists = {}
        for resource in resources:
            gid = str(resource.graph_id)
            if gid in allowed_graph_ids:
                out = resource.to_json(
                    compact=compact,
                    hide_empty_nodes=hide_empty_nodes,
                    user=user,
                    perm=perm,
                    version="beta",
                )

                # check to handle if v2 labelgraph is not being used.
                # TODO: remove once v2 is standardised
                try:
                    x = out["displayname"]
                except KeyError:
                    out = {
                        "resource": out,
                        "displaydescription": resource.displaydescription(),
                        "displayname": resource.displayname(),
                        "graph_id": resource.graph_id,
                        "legacyid": resource.legacyid,
                        "map_popup": resource.map_popup(),
                        "resourceinstanceid": resource.resourceinstanceid,
                    }

                if gid not in resource_lists.keys():
                    resource_lists[gid] = []
                resource_lists[gid].append(out)

        return resource_lists

    def write_resources(self, graph_id=None, resourceinstanceids=None, **kwargs):
        """
        Returns a list of dictionaries representing the generated html files with the following format:
        [
            {'name':file name, 'outputfile': a StringIO() buffer of resource instance data in the specified format},
            {'name':file name, 'outputfile': a StringIO()},
            ...
            ...
        ]
        """

        valid_graphs = HtmlWriter.get_graphids_with_export_template()
        if len(valid_graphs) == 0:
            logger.warning(
                "There are no valid graph html templates in the project - cannot generate html exports."
            )
            return []

        user = kwargs.get("user", None)
        resources_list = self.fetch_resource_objects_list(
            resourceinstanceids=resourceinstanceids,
            user=user,
            allowed_graph_ids=valid_graphs,
        )
        files = self.generate_html_files(resources_list)

        return files

    def generate_html_files(self, resource_object_list=None):
        """
        uses the provided resource object list to generate a set of html file objects required by the Arches ResourceExporter.

        """
        files = []
        for gid in resource_object_list.keys():
            template = self.load_html_template(gid)
            dest = StringIO()
            dest.write(template.render({"resources": resource_object_list[gid]}))
            files.append(
                {
                    "name": f"{str(GraphModel.objects.get(pk=gid))}.html",
                    "outputfile": dest,
                }
            )

        return files
