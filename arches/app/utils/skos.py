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

import uuid
from django.db import transaction
from django.utils.http import urlencode
from rdflib import Literal, Namespace, RDF, URIRef
from rdflib.namespace import SKOS, DCTERMS
from rdflib.graph import Graph
from time import time
from arches.app.models.concept import Concept
from arches.app.models import models

class SKOSReader(object):
    def __init__(self):
        self.nodes = []
        self.relations = []
            
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
    
    def save_concepts_from_skos(self, graph, concept_scheme_group='00000000-0000-0000-0000-000000000006'):
        """
        given an RDF graph, tries to save the concpets to the system

        """

        baseuuid = uuid.uuid4()
        allowed_languages = models.DLanguages.objects.values_list('pk', flat=True)

        value_types = models.ValueTypes.objects.all()
        skos_value_types = value_types.filter(namespace = 'skos')
        skos_value_types_list = skos_value_types.values_list('valuetype', flat=True)
        dcterms_value_types = value_types.filter(namespace = 'dcterms')

        relation_types = models.DRelationtypes.objects.all()
        skos_relation_types = relation_types.filter(namespace = 'skos')

        
        # if the graph is of the type rdflib.graph.Graph
        if isinstance(graph, Graph):

            # Search for ConceptSchemes first
            for s, v, o in graph.triples((None, RDF.type , SKOS.ConceptScheme)):
                scheme_id = self.generate_uuid_from_subject(baseuuid, s)
                concept = Concept({
                    'id': scheme_id,
                    'legacyoid': str(s),
                    'nodetype': 'ConceptScheme'
                })

                # associate the ConceptScheme with the provided ConceptSchemeGroup 
                self.relations.append({'source': concept_scheme_group, 'type': 'narrower', 'target': scheme_id})
                
                for predicate, object in graph.predicate_objects(subject = s):
                    if str(DCTERMS) in predicate and predicate.replace(DCTERMS, '') in dcterms_value_types.values_list('valuetype', flat=True):
                        if hasattr(object, 'language') and object.language not in allowed_languages: 
                            newlang = models.DLanguages()
                            newlang.pk = object.language
                            newlang.languagename = object.language
                            newlang.isdefault = False
                            newlang.save()
                            allowed_languages = models.DLanguages.objects.values_list('pk', flat=True)

                        try:
                            # first try and get any values associated with the concept
                            value_type = dcterms_value_types.get(valuetype=predicate.replace(DCTERMS, '')) # predicate.replace(SKOS, '') should yield something like 'prefLabel' or 'scopeNote', etc..
                            if predicate == DCTERMS.title:
                                concept.addvalue({'value':object, 'language': object.language, 'type': 'prefLabel', 'category': value_type.category}) 
                                print 'Casting dcterms:title to skos:prefLabel'
                            if predicate == DCTERMS.description:
                                concept.addvalue({'value':object, 'language': object.language, 'type': 'scopeNote', 'category': value_type.category}) 
                                print 'Casting dcterms:description to skos:scopeNote'
                        except:
                            pass

                    if str(SKOS) in predicate:
                        if predicate == SKOS.hasTopConcept:
                            self.relations.append({'source': scheme_id, 'type': 'narrower', 'target': self.generate_uuid_from_subject(baseuuid, object)})

                self.nodes.append(concept)   

            if len(self.nodes) == 0:
                raise Exception('No ConceptScheme found in file.')         

            # Search for Concepts
            for s, v, o in graph.triples((None, RDF.type , SKOS.Concept)):
                concept = Concept({
                    'id': self.generate_uuid_from_subject(baseuuid, s),
                    'legacyoid': str(s),
                    'nodetype': 'Concept'
                })

                # loop through all the elements within a <skos:Concept> element
                for predicate, object in graph.predicate_objects(subject = s):
                    if str(SKOS) in predicate:
                        if hasattr(object, 'language') and object.language not in allowed_languages: 
                            newlang = models.DLanguages()
                            newlang.pk = object.language
                            newlang.languagename = object.language
                            newlang.isdefault = False
                            newlang.save()
                            allowed_languages = models.DLanguages.objects.values_list('pk', flat=True)

                        relation_or_value_type = predicate.replace(SKOS, '') # this is essentially the skos element type within a <skos:Concept> element (eg: prefLabel, broader, etc...)

                        if relation_or_value_type in skos_value_types_list:
                            value_type = skos_value_types.get(valuetype=relation_or_value_type)
                            concept.addvalue({'value':object, 'language': object.language, 'type': value_type.valuetype, 'category': value_type.category}) 
                        elif predicate == SKOS.broader:
                            self.relations.append({'source': self.generate_uuid_from_subject(baseuuid, object), 'type': 'narrower', 'target': self.generate_uuid_from_subject(baseuuid, s)})
                        elif predicate == SKOS.narrower:
                            self.relations.append({'source': self.generate_uuid_from_subject(baseuuid, s), 'type': relation_or_value_type, 'target': self.generate_uuid_from_subject(baseuuid, object)})
                        elif predicate == SKOS.related:
                            self.relations.append({'source': self.generate_uuid_from_subject(baseuuid, s), 'type': relation_or_value_type, 'target': self.generate_uuid_from_subject(baseuuid, object)})

                self.nodes.append(concept)


            # insert and index the concpets
            with transaction.atomic():
                for node in self.nodes:
                    node.save()
                    node.index(scheme=scheme_id)            

                # insert the concept relations
                for relation in self.relations:
                    newrelation = models.ConceptRelations()
                    newrelation.relationid = str(uuid.uuid4())
                    newrelation.conceptidfrom_id = relation['source']
                    newrelation.conceptidto_id = relation['target']
                    newrelation.relationtype_id = relation['type']
                    newrelation.save()

            return self
        else:
            raise Exception('graph argument should be of type rdflib.graph.Graph')

    def generate_uuid_from_subject(self, baseuuid, subject):
        return str(uuid.uuid3(baseuuid, str(subject)))


class SKOSWriter(object):
    def __init__(self):
        self.concept_list = []

    def write(self, concept_graph, format='pretty-xml'):
        #get empty RDF graph
        rdf_graph = Graph()

        #define namespaces
        ARCHES = Namespace('http://www.archesproject.org/')

        #bind the namespaces
        rdf_graph.bind('arches',ARCHES)
        rdf_graph.bind('skos',SKOS)
        
        """
        #add main concept to the graph
        rdf_graph.add((subject, predicate, object))
        rdf_graph.add((ARCHES[node.id], RDF['type'], SKOS.Concept))
        rdf_graph.add((Arches guid, SKOS.prefLabel, Literal('Stone',lang=en)))
        """

        def build_skos(node):
            conceptid = node.id
            rdf_graph.add((ARCHES[node.id], RDF.type, SKOS[node.nodetype]))

            for value in node.values:
                if value.category == 'label' or value.category == 'note':
                    rdf_graph.add((ARCHES[node.id], SKOS[value.type], Literal(value.value, lang = value.language)))
                else:
                    rdf_graph.add((ARCHES[node.id], ARCHES[value.type.replace(' ', '_')], Literal(value.value, lang = value.language)))

            for subconcept in node.subconcepts:
                if node.nodetype == 'ConceptScheme':
                    rdf_graph.add((ARCHES[node.id], SKOS.hasTopConcept, ARCHES[subconcept.id]))
                elif node.nodetype == 'Concept':
                    rdf_graph.add((ARCHES[node.id], SKOS.narrower, ARCHES[subconcept.id]))

            for relatedconcept in node.relatedconcepts:
                rdf_graph.add((ARCHES[node.id], SKOS.related, ARCHES[relatedconcept.id]))


        concept_graph.traverse(build_skos)
        return rdf_graph.serialize(format=format)