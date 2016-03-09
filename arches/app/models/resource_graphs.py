'''
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
'''

import uuid
import types
import copy
import arches.app.models.models as archesmodels
from django.apps import apps
from django.contrib.gis.db import models
from django.contrib.gis.geos import fromstr
from django.contrib.gis.geos import GEOSGeometry
from django.db import connection
from django.db import transaction
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from arches.app.models.concept import Concept
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

class ResourceGraph(object):
    """ 
    Used for mapping complete resource graph objects to and from the database

    """
    
    def __init__(self, *args, **kwargs):
        if args[0]["nodes"] and args[0]["edges"]:
            self.nodes = args[0]["nodes"]
            self.edges = args[0]["edges"]


    def _save(self):
        """
        Saves an entity back to the db, returns a DB model instance, not an instance of self

        """

        for node in self.nodes:
            newNode = archesmodels.Node()

            try:
                uuid.UUID(str(node['nodeid']))
                newNode.nodeid = node['nodeid']
            except(ValueError):
                node['nodeid'] = str(uuid.uuid4())

            newNode.nodeid = node.get('nodeid')
            newNode.name = node.get('name', '')
            newNode.description = node.get('description','')
            newNode.istopnode = node.get('istopnode','')
            newNode.crmclass = node.get('crmclass','')
            newNode.datatype = node.get('datatype','')
            newNode.status = node.get('status','')

            node['nodeid'] = newNode.nodeid
            newNode.save()


        for edge in self.edges:
            newEdge = archesmodels.Edge()
            # self.get_node_id_from_text()

            try:
                uuid.UUID(edge['edgeid'])
            except(ValueError):
                edge['edgeid'] = str(uuid.uuid4())

            newEdge.edgeid = edge.get('edgeid')
            newEdge.rangenodeid_id = edge.get('rangenodeid')
            newEdge.domainnodeid_id = edge.get('domainnodeid')
            newEdge.ontologyproperty = edge.get('ontologyproperty', '')
            newEdge.branchmetadataid = edge.get('branchmetadataid', '')

            edge['edgeid'] = newEdge.edgeid
            newEdge.save()


    def get_node_id_from_text(self):
        for edge in self.edges:
            for node in self.nodes:
                if edge['domainnodeid'] == node['name']:
                    edge['domainnodeid'] = node['nodeid']
                if edge['rangenodeid'] == node['name']:
                    edge['rangenodeid'] = node['nodeid']

