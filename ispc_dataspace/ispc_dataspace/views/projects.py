from django.views.generic import View
from django.shortcuts import render
from arches.app.views.base import BaseManagerView
from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.models.card import Card
from arches.app.models.graph import Graph
from arches.app.models.tile import Tile
from arches.app.utils.betterJSONSerializer import JSONSerializer

from ispc_dataspace.models.viewmodels.portfolio_item import PortfolioItemViewModel
from ispc_dataspace.models.viewmodels.portfolio_items import PortfolioItemsViewModel


class ProjectsView(BaseManagerView):

    def get(self, request):
        projects = Resource.objects.filter(graph_id='243f8689-b8f6-11e6-84a5-026d961c88e6')
        project_viewmodels = PortfolioItemsViewModel()

        for project in projects:

            project_viewmodel = PortfolioItemViewModel()
            tiles = Tile.objects.filter(resourceinstance=project)

            for tile in tiles:
                if str(tile.nodegroup_id) == 'fb0c163e-d138-11e8-814d-0242ac1a0004':
                    if len(tile.data['fb0c1e72-d138-11e8-814d-0242ac1a0004']) > 0:
                        project_viewmodel.thumbnail_url = tile.data['fb0c1e72-d138-11e8-814d-0242ac1a0004'][0]['url']

                elif str(tile.nodegroup_id) == '358f3142-b113-11e8-8513-0242ac140005':
                    project_viewmodel.category_display_name = models.Value.objects \
                        .get(pk=tile.data['358f49de-b113-11e8-8513-0242ac140005']).value

            if project_viewmodel.category_display_name:
                project_viewmodel.category = project_viewmodel.category_display_name.replace(' ','-')
            else: 
                project_viewmodel.category = 'other'
                project_viewmodel.category_display_name = 'Other'

            project_viewmodel.display_name = project.displayname
            project_viewmodel.resource_instance_id = project.resourceinstanceid

            project_viewmodels.items.append(project_viewmodel)
 
        project_viewmodels.items.sort(key=lambda item: item.category)

        return render(request, 'views/projects.htm', {'projects': project_viewmodels})
