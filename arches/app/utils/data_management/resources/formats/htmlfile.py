import os
import logging
from uuid import UUID
from io import StringIO
from .format import Writer
from arches.app.models.models import GraphModel
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from jinja2 import Environment, FileSystemLoader
from pathlib import Path


logger = logging.getLogger(__name__)


class HtmlWriter(Writer):
    def __init__(self, **kwargs):
        super(HtmlWriter, self).__init__(**kwargs)
        self.templates_dir = HtmlWriter.get_templates_dir_path()

    @staticmethod
    def get_templates_dir_path():
        return os.path.join(settings.APP_ROOT, "export_html_templates")

    @staticmethod
    def get_graphids_with_export_template():
        valid_graphs = []
        filename_list = []
        for filename in os.listdir(HtmlWriter.get_templates_dir_path()):
            try:
                pth = Path(filename)
                if pth.suffix == ".html":
                    template_file_name = pth.stem
                    #ensure the template name is the graph UUID
                    x = UUID(template_file_name)
                    filename_list.append(template_file_name)
            except:
                pass

        #return [str(graph) for graph in GraphModel.objects.filter(pk__in=filename_list)]
        return filename_list



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

        """
        
        perm = "read_nodegroup"
        resources = Resource.objects.filter(pk__in=resourceinstanceids)
        compact = True
        hide_empty_nodes = False
        resource_lists = {}
        for resource in resources:
            gid = str(resource.graph_id)
            if gid in allowed_graph_ids:
                #should this use the API over http call as might parallel run if webserver configured for multiple processes?
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
            logger.warning("There are no valid graph html templates in the project - cannot generate html exports.")
            return []

        user = kwargs.get("user", None)
        resources_list = self.fetch_resource_objects_list(resourceinstanceids=resourceinstanceids, user=user, allowed_graph_ids=valid_graphs)
        files = self.generate_html_files(resources_list)

        return files
    
    def generate_html_files(self, resource_object_list=None):
        """
            uses the provided resource object list to generate a set of html file objects required by the Arches ResourceExporter.

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

 