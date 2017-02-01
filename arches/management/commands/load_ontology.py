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
import uuid
import xml.etree.ElementTree as ET
import networkx as nx
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.files import File
from django.db import transaction
from arches.app.models import models

class Command(BaseCommand):
    """
    Commands for managing the loading and running of packages in Arches

    """

    def add_arguments(self, parser):
        parser.add_argument('-s', '--source', action='store', dest='source', default=None,
            help='An XML file of describing an ontology graph')
        parser.add_argument('-vn', '--vernum', action='store', dest='version', default=None,
            help='The version of the ontology being loaded')
        parser.add_argument('-n', '--name', action='store', dest='ontology_name', default=None,
            help='Name to use to identify the ontology')
        parser.add_argument('-id', '--id', action='store', dest='id', default=None,
            help='UUID to use as the primary key to the ontology')
        parser.add_argument('-x', '--extensions', action='store', dest='extensions', default=None,
            help='Extensions to append to the base ontology')

    def handle(self, *args, **options):
        if options['source'] is not None:
            self.run_loader(data_source=options['source'], name=options['ontology_name'], version=options['version'], id=options['id'], extensions=options['extensions'])
            return

        if options['extensions'] is not None:
            available_ontologies = []
            selections = []
            index = 1
            for ontology in models.Ontology.objects.filter(parentontology=None):
                available_ontologies.append(ontology)
                selections.append(('%s. %s (%s)') % (index, ontology.name, ontology.pk))
                index += 1

            selected_ontology = raw_input('Select the number corresponding to the\nbase ontology to which you want to add the extension\n' + '\n'.join(selections)+'\n')

            ontology = available_ontologies[int(selected_ontology)-1]
            data_source = ontology.path.path
            self.run_loader(data_source=data_source, version=options['version'], id=ontology.pk, extensions=options['extensions'])


    def run_loader(self, data_source=None, version=None, name=None, id=None, extensions=None):
        """
        load the given ontology file in xml format into the database

        Keyword Arguments:
        data_source -- path to the source file

        version -- version of the ontology being loaded

        """

        if data_source is not None and version is not None:
            self.ontology_class_graph = nx.DiGraph()
            self.ontology_property_graph = nx.MultiDiGraph()
            
            with transaction.atomic():
                ontology = self.add_ontology(id=id, data_source=data_source, version=version, name=name)
                loaded_extensions = [extension.path.path for extension in models.Ontology.objects.filter(parentontology=ontology)]

                if extensions is None:
                    extensions = loaded_extensions
                else:
                    extensions = extensions.split(',') + loaded_extensions

                for extension in extensions:
                    if extension:
                        self.add_ontology(data_source=extension, version=version, name=name, parentontology=ontology)

                for ontology_class, data in self.crawl_graph().iteritems():
                    models.OntologyClass.objects.update_or_create(source=ontology_class, ontology=ontology, defaults={'target': data})
    
    def add_ontology(self, id=None, data_source=None, version=None, name=None, parentontology=None):
        filepath = os.path.split(os.path.abspath(data_source))[0]
        filename = os.path.split(data_source)[1]
        if name is None:
            name = os.path.splitext(filename)[0]
        self.parse_xml(data_source)
        if models.get_ontology_storage_system().location in filepath:
            # if the file we're referencing already exists in the location where we 
            # usually store them then leave it there and just save a reference to it
            path = '.%s' % os.path.join(filepath.replace(models.get_ontology_storage_system().location, ''), filename)
        else:
            path = File(open(data_source))

        ontology, created = models.Ontology.objects.get_or_create(path=path, parentontology=parentontology, defaults={'version': version, 'name': name, 'path': path, 'pk': id})
        return ontology

    def parse_xml(self, filepath):
        """
        parses the xml file into a dictionary object keyed off of the ontology class name found in the rdf:about attributes
        object values are dictionaries with 2 properties, 'down' and 'up' and within each of those another 2 properties, 
        'ontology_property' and 'ontology_classes'

        "down" assumes a known domain class, while "up" assumes a known range class

        .. code-block:: python

            "down":[
                {
                    "ontology_property": "P1_is_identified_by",
                    "ontology_classes": [
                        "E51_Contact_Point",
                        "E75_Conceptual_Object_Appellation",
                        "E42_Identifier",
                        "E45_Address",
                        "E41_Appellation",
                        ....
                    ]
                }
            ]
            "up":[
                    "ontology_property": "P1i_identifies",
                    "ontology_classes": [
                        "E51_Contact_Point",
                        "E75_Conceptual_Object_Appellation",
                        "E42_Identifier"
                        ....
                    ]
                }
            ]

        Keyword Arguments:
        filepath -- the path to the file to parse

        """

        ns = {
            'RDF': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'RDFS': 'http://www.w3.org/2000/01/rdf-schema#'
        }

        root = ET.parse(filepath).getroot()
        # populates a graph with class/subclass relations
        for concept in root.findall('RDFS:Class', ns):
            self.ontology_class_graph.add_node(self.get_attr(concept, ns, 'RDF:about'))
            for subclass in concept.findall('RDFS:subClassOf', ns):
                self.ontology_class_graph.add_edge(self.get_attr(subclass, ns, 'RDF:resource'), self.get_attr(concept, ns, 'RDF:about'))

        # populates a graph with class/property/class relations
        for concept in root.findall('RDF:Property', ns):
            domain = self.get_attr(concept.find('RDFS:domain', ns), ns, 'RDF:resource')
            range = self.get_attr(concept.find('RDFS:range', ns), ns, 'RDF:resource')
            if domain and range:
                self.ontology_property_graph.add_edge(domain, range, name=self.get_attr(concept, ns, 'RDF:about'))

    def crawl_graph(self):
        ret = {}
        lookup = {'down':{}, 'up':{}}
        for ontology_class in self.ontology_class_graph.nodes_iter():
            ret[ontology_class] = {'down':{}, 'up':{}}
            for direction in ['down', 'up']:
                if ontology_class not in lookup[direction]:
                    lookup[direction][ontology_class] = self.get_properties_and_relatedclasses(ontology_class, direction=direction)

                ret[ontology_class][direction] = lookup[direction][ontology_class]

                for superclass in nx.ancestors(self.ontology_class_graph, ontology_class):
                    if superclass not in lookup[direction]:
                        lookup[direction][superclass] = self.get_properties_and_relatedclasses(superclass, direction=direction)
                    ret[ontology_class][direction] = ret[ontology_class][direction] + lookup[direction][superclass]
                
        return ret
        
        # print len(list(nx.simple_cycles(self.ontology_property_graph)))
        # print list(nx.all_shortest_paths(self.ontology_class_graph,source='E1_CRM_Entity', target='E12_Production'))

    def get_attr(self, element, namespace, key):
        key = key.split(':')
        if element is not None:
            return element.get('{%s}%s' % (namespace[key[0]], key[1]))
        else:
            return None

    def get_properties_and_relatedclasses(self, ontology_class, direction='down'):
        ret = []
        if direction == 'down':
            for ontology_property in self.ontology_property_graph.out_edges([ontology_class], data=True):
                subclasses = nx.descendants(self.ontology_class_graph, ontology_property[1])
                subclasses.add(ontology_property[1])
                ret.append({
                    'ontology_property':ontology_property[2]['name'],
                    'ontology_classes':list(subclasses)
                })
        if direction == 'up':
            for ontology_property in self.ontology_property_graph.in_edges([ontology_class], data=True):
                subclasses = nx.descendants(self.ontology_class_graph, ontology_property[0])
                subclasses.add(ontology_property[0])
                ret.append({
                    'ontology_property':ontology_property[2]['name'],
                    'ontology_classes':list(subclasses)
                })
            
        return ret
