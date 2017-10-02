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

import uuid, re
from django.db import transaction
from django.db.models import Q
from django.utils.http import urlencode
from rdflib import Literal, Namespace, RDF, URIRef
from rdflib.namespace import SKOS, DCTERMS
from rdflib.graph import Graph
from time import time
from arches.app.models import models
from arches.app.models.concept import Concept
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

# define the ARCHES namespace
ARCHES = Namespace('http://www.archesproject.org/')

class SKOSReader(object):
    def __init__(self):
        self.nodes = []
        self.relations = []

    def read_file(self, path_to_file, format='xml'):
        """
        parse the skos file and extract all available data

        """

        rdf_graph = Graph()

        #bind the namespaces
        rdf_graph.bind('arches',ARCHES)

        start = time()
        try:
            rdf = rdf_graph.parse(source=path_to_file, format=format)
            print 'time elapsed to parse rdf graph %s s'%(time()-start)
        except:
            raise Exception('Error occurred while parsing the file %s' % path_to_file)
        return rdf

    def save_concepts_from_skos(self, graph, overwrite_options='overwrite', staging_options='keep'):
        """
        given an RDF graph, tries to save the concpets to the system

        Keyword arguments: 
        overwrite_options -- 'overwrite', 'ignore'
        staging_options -- 'stage', 'keep'

        """

        baseuuid = uuid.uuid4()
        allowed_languages = models.DLanguage.objects.values_list('pk', flat=True)
        default_lang = settings.LANGUAGE_CODE

        value_types = models.DValueType.objects.all()
        skos_value_types = value_types.filter(Q(namespace = 'skos') | Q(namespace = 'arches'))
        skos_value_types_list = list(skos_value_types.values_list('valuetype', flat=True))
        skos_value_types = {valuetype.valuetype: valuetype for valuetype in skos_value_types}
        dcterms_value_types = value_types.filter(namespace = 'dcterms')
        dcterms_identifier_type = dcterms_value_types.get(valuetype=str(DCTERMS.identifier).replace(str(DCTERMS), ''))


        # if the graph is of the type rdflib.graph.Graph
        if isinstance(graph, Graph):

            # Search for ConceptSchemes first
            for scheme, v, o in graph.triples((None, RDF.type , SKOS.ConceptScheme)):
                identifier = self.unwrapJsonLiteral(str(scheme))
                scheme_id = self.generate_uuid_from_subject(baseuuid, scheme)
                concept_scheme = Concept({
                    'id': scheme_id,
                    'legacyoid': str(scheme),
                    'nodetype': 'ConceptScheme'
                })

                for predicate, object in graph.predicate_objects(subject = scheme):
                    if str(DCTERMS) in predicate and predicate.replace(DCTERMS, '') in dcterms_value_types.values_list('valuetype', flat=True):
                        if not self.language_exists(object, allowed_languages):
                            allowed_languages = models.DLanguage.objects.values_list('pk', flat=True)

                        try:
                            # first try and get any values associated with the concept_scheme
                            value_type = dcterms_value_types.get(valuetype=predicate.replace(DCTERMS, '')) # predicate.replace(SKOS, '') should yield something like 'prefLabel' or 'scopeNote', etc..
                            val = self.unwrapJsonLiteral(object)
                            if predicate == DCTERMS.title:
                                concept_scheme.addvalue({'id': val['value_id'], 'value':val['value'], 'language': object.language or default_lang, 'type': 'prefLabel', 'category': value_type.category})
                                print 'Casting dcterms:title to skos:prefLabel'
                            elif predicate == DCTERMS.description:
                                concept_scheme.addvalue({'id': val['value_id'], 'value':val['value'], 'language': object.language or default_lang, 'type': 'scopeNote', 'category': value_type.category})
                                print 'Casting dcterms:description to skos:scopeNote'
                            elif predicate == DCTERMS.identifier:
                                identifier = self.unwrapJsonLiteral(str(object))
                        except:
                            pass

                    if str(SKOS) in predicate:
                        #print predicate
                        if predicate == SKOS.hasTopConcept:
                            top_concept_id = self.generate_uuid_from_subject(baseuuid, object)
                            self.relations.append({'source': scheme_id, 'type': 'hasTopConcept', 'target': top_concept_id})

                concept_scheme.addvalue({'id': identifier['value_id'], 'value':identifier['value'], 'language': default_lang, 'type': dcterms_identifier_type.valuetype, 'category': dcterms_identifier_type.category})
                self.nodes.append(concept_scheme)

                # Search for Concepts
                for s, v, o in graph.triples((None, SKOS.inScheme , scheme)):
                    identifier = self.unwrapJsonLiteral(str(s))
                    concept = Concept({
                        'id': self.generate_uuid_from_subject(baseuuid, s),
                        'legacyoid': str(s),
                        'nodetype': 'Concept'
                    })


                    # loop through all the elements within a <skos:Concept> element
                    for predicate, object in graph.predicate_objects(subject = s):
                        if str(SKOS) in predicate or str(ARCHES) in predicate:
                            if not self.language_exists(object, allowed_languages):
                                allowed_languages = models.DLanguage.objects.values_list('pk', flat=True)

                            relation_or_value_type = predicate.replace(SKOS, '').replace(ARCHES, '')  # this is essentially the skos element type within a <skos:Concept> element (eg: prefLabel, broader, etc...)

                            if relation_or_value_type in skos_value_types_list:
                                value_type = skos_value_types[relation_or_value_type]
                                val = self.unwrapJsonLiteral(object)
                                concept.addvalue({'id': val['value_id'], 'value':val['value'], 'language': object.language or default_lang, 'type': value_type.valuetype, 'category': value_type.category})
                            elif predicate == SKOS.broader:
                                self.relations.append({'source': self.generate_uuid_from_subject(baseuuid, object), 'type': 'narrower', 'target': self.generate_uuid_from_subject(baseuuid, s)})
                            elif predicate == SKOS.narrower:
                                self.relations.append({'source': self.generate_uuid_from_subject(baseuuid, s), 'type': relation_or_value_type, 'target': self.generate_uuid_from_subject(baseuuid, object)})
                            elif predicate == SKOS.related:
                                self.relations.append({'source': self.generate_uuid_from_subject(baseuuid, s), 'type': relation_or_value_type, 'target': self.generate_uuid_from_subject(baseuuid, object)})

                        elif predicate == DCTERMS.identifier:
                            identifier = self.unwrapJsonLiteral(str(object))

                    concept.addvalue({'id': identifier['value_id'], 'value':identifier['value'], 'language': default_lang, 'type': dcterms_identifier_type.valuetype, 'category': dcterms_identifier_type.category})
                    self.nodes.append(concept)


            # Search for SKOS.Collections
            for s, v, o in graph.triples((None, RDF.type , SKOS.Collection)):
                #print "%s %s %s " % (s,v,o)
                concept = Concept({
                    'id': self.generate_uuid_from_subject(baseuuid, s),
                    'legacyoid': str(s),
                    'nodetype': 'Collection'
                })
                # loop through all the elements within a <skos:Concept> element
                for predicate, object in graph.predicate_objects(subject = s):
                    if str(SKOS) in predicate or str(ARCHES) in predicate:
                        if not self.language_exists(object, allowed_languages):
                            allowed_languages = models.DLanguage.objects.values_list('pk', flat=True)

                        relation_or_value_type = predicate.replace(SKOS, '').replace(ARCHES, '')  # this is essentially the skos element type within a <skos:Concept> element (eg: prefLabel, broader, etc...)

                        if relation_or_value_type in skos_value_types_list:
                            value_type = skos_value_types[relation_or_value_type]
                            val = self.unwrapJsonLiteral(object)
                            concept.addvalue({'id': val['value_id'], 'value':val['value'], 'language': object.language or default_lang, 'type': value_type.valuetype, 'category': value_type.category})
                
                self.nodes.append(concept)
            
            for s, v, o in graph.triples((None, SKOS.member, None)):
                #print "%s %s %s " % (s,v,o)
                self.relations.append({'source': self.generate_uuid_from_subject(baseuuid, s), 'type': 'member', 'target': self.generate_uuid_from_subject(baseuuid, o)})

            # insert and index the concpets
            scheme_node = None
            with transaction.atomic():
                for node in self.nodes:
                    if node.nodetype == 'ConceptScheme':
                        scheme_node = node
                    if staging_options == 'stage':
                        try:
                            models.Concept.objects.get(pk=node.id)
                        except:
                            # this is a new concept, so add a reference to it in the Candiates schema
                            if node.nodetype != 'ConceptScheme':
                                self.relations.append({'source': '00000000-0000-0000-0000-000000000006', 'type': 'narrower', 'target': node.id})
                    
                    if overwrite_options == 'overwrite':
                        node.save()
                    elif overwrite_options == 'ignore':
                        try:
                            # don't do anything if the concept already exists
                            models.Concept.objects.get(pk=node.id)
                        except:
                            # else save it
                            node.save()

                # insert the concept relations
                for relation in self.relations:
                    newrelation = models.Relation.objects.get_or_create(
                        conceptfrom_id = relation['source'],
                        conceptto_id = relation['target'],
                        relationtype_id = relation['type']
                    )

                # need to index after the concepts and relations have been entered into the db
                # so that the proper context gets indexed with the concept
                if scheme_node:
                    scheme_node.bulk_index()


            return scheme_node
        else:
            raise Exception('graph argument should be of type rdflib.graph.Graph')

    def unwrapJsonLiteral(self, jsonObj):
        ret = {
            'value_id': '',
            'value': jsonObj
        }

        try:
            jsonLiteralValue = JSONDeserializer().deserialize(jsonObj)
            ret['value_id'] = str(jsonLiteralValue['id'])
            ret['value'] = jsonLiteralValue['value']
        except:
            pass

        return ret

    def generate_uuid_from_subject(self, baseuuid, subject):
        uuidregx = re.compile(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}')
        matches = uuidregx.search(str(subject))
        if matches:
            return matches.group(0)
        else:
            return str(uuid.uuid3(baseuuid, str(subject)))


    def language_exists(self, rdf_tag, allowed_languages):
        if hasattr(rdf_tag, 'language') and rdf_tag.language not in allowed_languages and rdf_tag.language is not None and rdf_tag.language.strip() != '':
            newlang = models.DLanguage()
            newlang.pk = rdf_tag.language
            newlang.languagename = rdf_tag.language
            newlang.isdefault = False
            newlang.save()
            return False
        return True


class SKOSWriter(object):
    def __init__(self):
        self.concept_list = []

    def write(self, concept_graphs, format='pretty-xml'):
        serializer = JSONSerializer()

        #get empty RDF graph
        rdf_graph = Graph()

        #bind the namespaces
        rdf_graph.bind('arches',ARCHES)
        rdf_graph.bind('skos',SKOS)
        rdf_graph.bind('dcterms',DCTERMS)

        """
        #add main concept to the graph
        rdf_graph.add((subject, predicate, object))
        rdf_graph.add((ARCHES[node.id], RDF['type'], SKOS.Concept))
        rdf_graph.add((Arches guid, SKOS.prefLabel, Literal('Stone',lang=en)))
        """

        if not isinstance(concept_graphs, list):
            concept_graphs = [concept_graphs]

        for concept_graph in concept_graphs:
            if concept_graph.nodetype == 'ConceptScheme':
                scheme_id = concept_graph.id

                def build_skos(node):
                    if node.nodetype == 'Concept':
                        rdf_graph.add((ARCHES[node.id], SKOS.inScheme, ARCHES[scheme_id]))

                    for subconcept in node.subconcepts:
                        rdf_graph.add((ARCHES[node.id], SKOS[subconcept.relationshiptype], ARCHES[subconcept.id]))

                    for relatedconcept in node.relatedconcepts:
                        rdf_graph.add((ARCHES[node.id], SKOS[relatedconcept.relationshiptype], ARCHES[relatedconcept.id]))

                    for value in node.values:
                        jsonLiteralValue = serializer.serialize({'value': value.value, 'id': value.id})
                        if value.category == 'label' or value.category == 'note':
                            if node.nodetype == 'ConceptScheme':
                                if value.type == 'prefLabel':
                                    rdf_graph.add((ARCHES[node.id], DCTERMS.title, Literal(jsonLiteralValue, lang = value.language)))
                                elif value.type == 'scopeNote':
                                    rdf_graph.add((ARCHES[node.id], DCTERMS.description, Literal(jsonLiteralValue, lang = value.language)))
                            else:
                                rdf_graph.add((ARCHES[node.id], SKOS[value.type], Literal(jsonLiteralValue, lang = value.language)))
                        elif value.type == 'identifier':
                            rdf_graph.add((ARCHES[node.id], DCTERMS.identifier, Literal(jsonLiteralValue, lang = value.language)))
                        else:
                            rdf_graph.add((ARCHES[node.id], ARCHES[value.type.replace(' ', '_')], Literal(jsonLiteralValue, lang = value.language)))

                    rdf_graph.add((ARCHES[node.id], RDF.type, SKOS[node.nodetype]))

                concept_graph.traverse(build_skos)

            elif concept_graph.nodetype == 'Collection':
                scheme_id = concept_graph.id

                def build_skos(node):
                    for subconcept in node.subconcepts:
                        rdf_graph.add((ARCHES[node.id], SKOS[subconcept.relationshiptype], ARCHES[subconcept.id]))

                    rdf_graph.add((ARCHES[node.id], RDF.type, SKOS[node.nodetype]))
                    if node.nodetype == 'Collection':
                        for value in node.values:
                            if value.category == 'label' or value.category == 'note':
                                jsonLiteralValue = serializer.serialize({'value': value.value, 'id': value.id})
                                rdf_graph.add((ARCHES[node.id], SKOS[value.type], Literal(jsonLiteralValue, lang = value.language)))
        
                concept_graph.traverse(build_skos)
            else:
                raise Exception('Only ConceptSchemes and Collections can be written to SKOS RDF files.')
            
        return rdf_graph.serialize(format=format)
