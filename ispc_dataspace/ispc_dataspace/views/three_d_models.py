from collections import defaultdict
from django.views.generic import View
from django.shortcuts import render
from arches.app.models import models
from arches.app.models.resource import Resource
from arches.app.models.card import Card
from arches.app.models.graph import Graph
from arches.app.utils.betterJSONSerializer import JSONSerializer

import logging
logger = logging.getLogger(__name__)

from .base_view import BaseView
from ispc_dataspace.models.viewmodels.portfolio_item import PortfolioItemViewModel
from ispc_dataspace.models.viewmodels.portfolio_items import PortfolioItemsViewModel


class ThreeDModelsView(BaseView):

    def __init__(self):

        self.three_d_hop_graph_id = '36bcaff4-b82f-11e8-8598-0242ac120004'
        self.sketchfab_graph_id = '6ba5a68c-f58b-11e8-a354-0242ac120004'
        
        self.graph_types = {
            self.three_d_hop_graph_id: {
                'name': 'three-d-hop',
                'display-name': '3D HOP',
                'images-nodegroup-id': '4b9b3314-d12f-11e8-85df-0242ac1a0004',
                'thumbnail-node-id': '4b9b3c7e-d12f-11e8-85df-0242ac1a0004'
            },
            self.sketchfab_graph_id: {
                'name': 'sketchfab',
                'display-name': 'Sketchfab',
                'images-nodegroup-id': '6ba5aa06-f58b-11e8-a354-0242ac120004',
                'thumbnail-node-id': '6ba5cea0-f58b-11e8-a354-0242ac120004'
            }
        }

    def get(self, request):
        
        three_d_models = \
                Resource.objects.filter(graph_id=self.three_d_hop_graph_id) | \
                Resource.objects.filter(graph_id=self.sketchfab_graph_id)
        
        three_d_viewmodels = PortfolioItemsViewModel()

        for three_d_model in three_d_models:

            try:
                graph_type = self.graph_types[str(three_d_model.graph_id)]
            except IndexError:
                logger.exception("View '{view_name}' not configured properly. Could not find graph type with id '{graph_id}'"
                                 .format(view_name=self.__class__.__name__,
                                         graph_id=str(three_d_model.graph_id)))
                continue

            three_d_viewmodel = PortfolioItemViewModel()

            thumbnail_url = self.get_thumbnail_or_continue(graph_type, three_d_model)
            if not thumbnail_url:
                continue

            three_d_viewmodel.thumbnail_url = thumbnail_url
            three_d_viewmodel.category = graph_type['name']
            three_d_viewmodel.category_display_name = graph_type['display-name']
            three_d_viewmodel.display_name = three_d_model.displayname
            three_d_viewmodel.resource_instance_id = three_d_model.resourceinstanceid

            three_d_viewmodels.items.append(three_d_viewmodel)

        three_d_viewmodels.items.sort(key=lambda item: item.category)

        return render(request, 'views/three-d-models.htm', {'three_d_models': three_d_viewmodels})

    def get_thumbnail_or_continue(self, graph_type, three_d_model):
        images_nodegroup_id = graph_type['images-nodegroup-id']
        thumbnail_node_id = graph_type['thumbnail-node-id']
        return self.get_thumbnail_url_from_images(three_d_model, images_nodegroup_id, thumbnail_node_id)