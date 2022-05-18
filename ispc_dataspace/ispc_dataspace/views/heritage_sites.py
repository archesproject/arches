from collections import defaultdict
from django.views.generic import View
from django.shortcuts import render
from django.core.exceptions import ValidationError
from arches.app.views.base import BaseManagerView
from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.models.card import Card
from arches.app.models.graph import Graph
from arches.app.models.tile import Tile
from arches.app.utils.betterJSONSerializer import JSONSerializer

from .base_view import BaseView
from ispc_dataspace.models.viewmodels.portfolio_item import PortfolioItemViewModel
from ispc_dataspace.models.viewmodels.portfolio_items import PortfolioItemsViewModel

class HeritageSitesView(BaseView):

    def __init__(self):
        self.images_nodegroup_id = 'a13a9486-d134-11e8-a039-0242ac1a0004'
        self.thumbnail_node_id = 'a13a9cc4-d134-11e8-a039-0242ac1a0004'
        self.country_nodegroup_id = '709e4cf8-b12e-11e8-81d7-0242ac140004'
        self.country_display_name_node_id = '709e5d74-b12e-11e8-81d7-0242ac140004'

    def get(self, request):
        sites = Resource.objects.filter(graph_id='fad0563b-b8f8-11e6-84a5-026d961c88e6')
        site_viewmodels = PortfolioItemsViewModel()

        for site in sites:
            site_viewmodel = self.get_site_info(site)
            if site_viewmodel:
                site_viewmodels.items.append(site_viewmodel)
 
        site_viewmodels.items.sort(key=lambda item: item.category)

        return render(request, 'views/heritage-sites.htm', { 'sites': site_viewmodels })

    def get_site_info(self, site_resource):
        site_viewmodel = PortfolioItemViewModel()
        tiles = Tile.objects.filter(resourceinstance=site_resource)

        site_viewmodel.thumbnail_url = self.get_thumbnail_url_from_tiles(tiles, self.images_nodegroup_id, self.thumbnail_node_id)
        if not site_viewmodel.thumbnail_url:
            return None

        self.get_country_info(tiles, site_viewmodel)

        site_viewmodel.display_name = site_resource.displayname
        site_viewmodel.resource_instance_id = site_resource.resourceinstanceid        

        return site_viewmodel

    def get_country_info(self, tiles, site_viewmodel):
        site_viewmodel.category_display_name = self.get_country_display_name(tiles)
        
        if site_viewmodel.category_display_name:
            site_viewmodel.category = site_viewmodel.category_display_name.replace(' ','-')
        else: 
            site_viewmodel.category = 'other'
            site_viewmodel.category_display_name = 'Other'

    def get_country_display_name(self, tiles):
        try:
            country_nodegroup_tile = tiles.get(nodegroup_id=self.country_nodegroup_id)
        except Tile.DoesNotExist:
            pass

        country_value_id = country_nodegroup_tile.data[self.country_display_name_node_id]
        if not country_value_id:
            return None
        try:
            return models.Value.objects.get(pk=country_value_id).value
        except ValidationError:
            return None
