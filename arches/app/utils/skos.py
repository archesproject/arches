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

from django.utils.http import urlencode
from rdflib import Literal, Namespace, RDF, URIRef
from rdflib.graph import Graph
from time import time

class SKOSReader(object):
            
    def read_file(self, path_to_file, format='xml'):
        """
        parse the skos file and extract all available data

        """       

        rdf_graph = Graph()
        start = time()
        try:
            rdf = rdf_graph.parse(source=path_to_file, format=format)
            print 'time elapsed to parse rdf graph %s s'%(time()-start)
        except:
            raise Exception('Error occurred while parsing the file %s'%path_to_file)
        return rdf
    
    def extract_concepts(self,graph):
        """
        return a list of extracted concepts
        each concept is modeled as a set of dictionaries. So the outcome is a dictionary of dictionaries.
        
        Eg:
        concept_dictionary = {   
            'uuid_1' : {},
            'uuid_2' : {},
            'uuid_3' : {},
            ...
        }

        """

        concept_dictionary={}
        
        # if the graph is of the type rdflib.graph.Graph
        if isinstance(graph, Graph):
            
            for subject in graph.subjects():
                if subject not in concept_dictionary.keys():
                    concept_dictionary[subject.__str__()]= {}
                for tuple in graph.predicate_objects(subject = subject):
                    # add predicate, object pair to the corresponding value dictionary
                    concept_dictionary[subject.__str__()][tuple[0].__str__()] = tuple[1].__str__()
            #print concept_dictionary        
            return concept_dictionary
        else:
            raise Exception('graph argument should be of type rdflib.graph.Graph')


class SKOSWriter(object):
    def __init__(self):
        self.concept_list = []

    def write(self, concept_graph, format='pretty-xml'):
        #get empty RDF graph
        rdf_graph = Graph()
        #define namespaces
        skos = Namespace('http://www.w3.org/2004/02/skos/core#')
        arches = Namespace('http://www.archesns.com/')
        #bind the namespaces
        rdf_graph.bind('skos', skos)
        rdf_graph.bind('arches',arches)
        
        """
        #add main concept to the graph
        rdf_graph.add((arches[concept_data[0][0]], RDF['type'], skos['Concept']))
        rdf_graph.add((arches[concept_data[0][0]], skos['prefLabel'], Literal(concept_data[0][1],lang= concept_data[0][2])))
        """
        #add subconcepts to the graph

        def traverse(graph):
            conceptid = graph.id
            rdf_graph.add((arches[graph.id],RDF['type'],skos['Concept']))

            for parentconcept in graph.parentconcepts:
                rdf_graph.add((arches[graph.id],skos['broader'],arches[parentconcept.id]))
            
            for value in graph.values:
                if value.category == 'label' or value.category == 'note':
                    rdf_graph.add((arches[graph.id], skos[value.type], Literal(value.value, lang = value.language)))
                else:
                    rdf_graph.add((arches[graph.id], arches[value.type.replace(' ', '_')], Literal(value.value, lang = value.language)))

            for concept in graph.subconcepts:
                traverse(concept)


        traverse(concept_graph)
        return rdf_graph.serialize(format=format)

    def write_file(self,rdf_graph, file_path):
        try:
            file = open(file_path, 'w+')
            file.write(rdf_graph)
            file.close()
        except:
            raise Exception('Error occurred while writing RDF/XML file.')