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

"""This module contains commands for building Arches."""

import os
import xml.etree.ElementTree as ET
import networkx as nx
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from arches.app.models import models

class Command(BaseCommand):
    """
    Commands for managing the loading and running of packages in Arches

    """
    
    def add_arguments(self, parser):
        parser.add_argument('-s', '--source', action='store', dest='source', default='',
            help='An XML file of describing an ontology graph')
        parser.add_argument('-vn', '--vernum', action='store', dest='version', default='',
            help='The version of the ontology being loaded')

    def handle(self, *args, **options):
        self.run_loader(data_source=options['source'], version=options['version'])

    def run_loader(self, data_source=None, version=None):
        """
        load the given ontology file in xml format into the database

        Keyword Arguments:
        data_source -- path to the source file

        version -- version of the ontology being loaded

        """

        data_source = None if data_source == '' else data_source
        if data_source and version:
            for direction in ['down', 'up']:
                for ontology_class, data in self.parse_xml(data_source, direction=direction).iteritems():
                    models.Ontology.objects.create(source=ontology_class, target=data, direction=direction, version=version)

    def parse_xml(self, file, direction='down'):
        """
        parses the xml file into a dictionary object keyed off of the ontology class name found in the rdf:about attributes
        object values are dictionaries with 2 properties, 'ontology_property' and 'ontology_classes'

        .. code-block:: python

            {
                "ontology_property": "P1_is_identified_by",
                "ontology_classes": [
                    "E51_Contact_Point",
                    "E75_Conceptual_Object_Appellation",
                    "E42_Identifier",
                    "E45_Address",
                    "E41_Appellation",
                    "E44_Place_Appellation",
                    "E35_Title",
                    "E50_Date",
                    "E82_Actor_Appellation",
                    "E48_Place_Name",
                    "E49_Time_Appellation",
                    "E47_Spatial_Coordinates",
                    "E46_Section_Definition"
                ]
            }

        Keyword Arguments:
        file -- the file to parse

        direction -- "down" {default}, or "up".  "down" assumes a known domain class, while "up" assumes a known range class

        """

        ns = {
            'RDF': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'RDFS': 'http://www.w3.org/2000/01/rdf-schema#'
        }
        ontology_class_graph = nx.DiGraph()
        ontology_property_graph = nx.MultiDiGraph()

        root = ET.parse(file).getroot()
        # populates a graph with class/subclass relations
        for concept in root.findall('RDFS:Class', ns):
            ontology_class_graph.add_node(self.get_attr(concept, ns, 'RDF:about'))
            for subclass in concept.findall('RDFS:subClassOf', ns):
                ontology_class_graph.add_edge(self.get_attr(subclass, ns, 'RDF:resource'), self.get_attr(concept, ns, 'RDF:about'))

        # populates a graph with class/property/class relations
        for concept in root.findall('RDF:Property', ns):
            domain = self.get_attr(concept.find('RDFS:domain', ns), ns, 'RDF:resource')
            range = self.get_attr(concept.find('RDFS:range', ns), ns, 'RDF:resource')
            ontology_property_graph.add_edge(domain, range, name=self.get_attr(concept, ns, 'RDF:about'))

        ret = {}
        lookup = {}
        for ontology_class in ontology_property_graph.nodes_iter():
            if ontology_class not in lookup:
                lookup[ontology_class] = self.get_properties_and_relatedclasses(ontology_class_graph, ontology_property_graph, ontology_class, direction=direction)
            
            ret[ontology_class] = lookup[ontology_class]

            for superclass in nx.ancestors(ontology_class_graph, ontology_class):
                if superclass not in lookup:
                    lookup[superclass] = self.get_properties_and_relatedclasses(ontology_class_graph, ontology_property_graph, superclass, direction=direction)
                ret[ontology_class] = ret[ontology_class] + lookup[superclass]
                
        return ret
        
        # print len(list(nx.simple_cycles(ontology_property_graph)))
        # print list(nx.all_shortest_paths(ontology_class_graph,source='E1_CRM_Entity', target='E12_Production'))

    def get_attr(self, element, namespace, key):
        key = key.split(':')
        return element.get('{%s}%s' % (namespace[key[0]], key[1]))

    def get_properties_and_relatedclasses(self, ontology_class_graph, ontology_property_graph, ontology_class, direction='down'):
        ret = []
        if direction == 'down':
            for ontology_property in ontology_property_graph.out_edges([ontology_class], data=True):
                subclasses = nx.descendants(ontology_class_graph, ontology_property[1])
                subclasses.add(ontology_property[1])
                ret.append({
                    'ontology_property':ontology_property[2]['name'],
                    'ontology_classes':list(subclasses)
                })
        if direction == 'up':
            for ontology_property in ontology_property_graph.in_edges([ontology_class], data=True):
                subclasses = nx.descendants(ontology_class_graph, ontology_property[0])
                subclasses.add(ontology_property[0])
                ret.append({
                    'ontology_property':ontology_property[2]['name'],
                    'ontology_classes':list(subclasses)
                })
            
        return ret
