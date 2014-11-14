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
    
    def get_concepts(self, graph, concept_scheme_group='00000000-0000-0000-0000-000000000006'):
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
                                concept.addvalue({'value':object, 'language': object.language, 'type': 'prefLabel', 'datatype': 'text', 'category': value_type.category}) 
                                print 'Casting dcterms:title to skos:prefLabel'
                            if predicate == DCTERMS.description:
                                concept.addvalue({'value':object, 'language': object.language, 'type': 'scopeNote', 'datatype': 'text', 'category': value_type.category}) 
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
                            concept.addvalue({'value':object, 'language': object.language, 'type': value_type.valuetype, 'datatype': 'text', 'category': value_type.category}) 
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

from rdflib import exceptions
from rdflib import URIRef, RDFS, RDF, BNode
class OntoInspector(object):
    """Class that includes methods for querying an RDFS/OWL ontology"""        

    def __init__(self, uri, language=""):
        super(OntoInspector, self).__init__()
        #self.rdfGraph = rdflib.Graph()
        self.ontologyURI = None
        self.ontologyPrettyURI = None
        self.ontologyPhysicalLocation = None
        self.ontologyNamespaces = None

        self.allclasses = None      
        self.allinstances = None
        self.allrdfproperties = None
        self.allobjproperties = None
        self.alldataproperties = None
        self.allinferredproperties = None
        self.allproperties = None

        self.toplayer = None
        self.classTreeMaxDepth = None
        self.sessionGraph = None
        self.sessionNS = None   
        # self.testallclasses = None    
        self.topObjProperties = None
        self.topDataProperties = None
        self.ontologyClassTree = None

        self.rdfGraph = Graph()
        try:
            self.rdfGraph.parse(uri, format="xml")
        except:
            try:
                self.rdfGraph.parse(uri, format="n3")
            except:
                raise exceptions.Error("Could not parse the file! Is it a valid RDF/OWL ontology?")

        finally:
            # let's cache some useful info for faster access
            self.baseURI = self.get_OntologyURI() or uri            
            self.allclasses = self.__getAllClasses(classPredicate='skos')
            #self.toplayer = self.__getTopclasses(classPredicate='skos')
            # self.tree = self.__getTree()


    def get_OntologyURI(self, return_as_string=True):
        """ 
        In [15]: [x for x in o.rdfGraph.triples((None, RDF.type, OWL.Ontology))]
        Out[15]: 
        [(rdflib.URIRef('http://purl.com/net/sails'),
          rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
          rdflib.URIRef('http://www.w3.org/2002/07/owl#Ontology'))]

        Mind that this will work only for OWL ontologies.
        In other cases we just return None, and use the URI passed at loading time
        """

        test = [x for x, y, z in self.rdfGraph.triples((None, RDF.type, OWL.Ontology))]

        if test:
            if return_as_string:
                return str(test[0])
            else:
                return test[0]
        else:
            return None

    def __getAllClasses(self, classPredicate = "", removeBlankNodes = True):
        """  
        Extracts all the classes from a model
        We use the RDFS and OWL predicate by default; also, we extract non explicitly declared classes
        """

        rdfGraph = self.rdfGraph
        exit = []       

        if not classPredicate:          
            for s, v, o in rdfGraph.triples((None, RDF.type , OWL.Class)): 
                exit.append(s)
            for s, v, o in rdfGraph.triples((None, RDF.type , RDFS.Class)):
                exit.append(s)

            # this extra routine makes sure we include classes not declared explicitly
            # eg when importing another onto and subclassing one of its classes...
            for s, v, o in rdfGraph.triples((None, RDFS.subClassOf , None)):
                if s not in exit:
                    exit.append(s)
                if o not in exit:
                    exit.append(o)

            # this extra routine includes classes found only in rdfs:domain and rdfs:range definitions
            for s, v, o in rdfGraph.triples((None, RDFS.domain , None)):
                if o not in exit:
                    exit.append(o)
            for s, v, o in rdfGraph.triples((None, RDFS.range , None)):
                if o not in exit:
                    exit.append(o)

        else:
            if classPredicate == "rdfs" or classPredicate == "rdf":
                for s, v, o in rdfGraph.triples((None, RDF.type , RDFS.Class)):
                    exit.append(s)
            elif classPredicate == "owl":
                for s, v, o in rdfGraph.triples((None, RDF.type , OWL.Class)): 
                    exit.append(s)
            elif classPredicate == "skos":
                for s, v, o in rdfGraph.triples((None, RDF.type , SKOS.Concept)): 
                    exit.append(s)
            else:
                raise exceptions.Error("ClassPredicate must be either rdf, rdfs, skos, or owl")

        exit = remove_duplicates(exit)

        if removeBlankNodes:
            exit = [x for x in exit if not self.__isBlankNode(x)]

        return sort_uri_list_by_name(exit)

    # methods for getting ancestores and descendants of classes: by default, we do not include blank nodes

    def get_classDirectSupers(self, aClass, excludeBnodes = True):
        returnlist = []
        for s, v, o in self.rdfGraph.triples((aClass, RDFS.subClassOf , None)):
            if excludeBnodes:
                if not self.__isBlankNode(o):
                    returnlist.append(o)
            else:
                returnlist.append(o)

        return sort_uri_list_by_name(remove_duplicates(returnlist)) 


    def get_classDirectSubs(self, aClass, excludeBnodes = True):
        returnlist = []
        for s, v, o in self.rdfGraph.triples((None, RDFS.subClassOf , aClass)):
            if excludeBnodes:
                if not self.__isBlankNode(s):
                    returnlist.append(s)

            else:
                returnlist.append(s)

        return sort_uri_list_by_name(remove_duplicates(returnlist))


    def get_classAllSubs(self, aClass, returnlist = [], excludeBnodes = True):
        for sub in self.get_classDirectSubs(aClass, excludeBnodes):
            returnlist.append(sub)
            self.get_classAllSubs(sub, returnlist, excludeBnodes)
        return sort_uri_list_by_name(remove_duplicates(returnlist))



    def get_classAllSupers(self, aClass, returnlist = [], excludeBnodes = True ):
        for ssuper in self.get_classDirectSupers(aClass, excludeBnodes):
            returnlist.append(ssuper)
            self.get_classAllSupers(ssuper, returnlist, excludeBnodes)
        return sort_uri_list_by_name(remove_duplicates(returnlist))



    def get_classSiblings(self, aClass, excludeBnodes = True):
        returnlist = []
        for father in self.get_classDirectSupers(aClass, excludeBnodes):
            for child in self.get_classDirectSubs(father, excludeBnodes):
                if child != aClass:
                    returnlist.append(child)

        return sort_uri_list_by_name(remove_duplicates(returnlist))

    def __getTopclasses(self, classPredicate = ''):

        """ Finds the topclass in an ontology (works also when we have more than on superclass)
        """

        returnlist = []

        # gets all the classes
        for eachclass in self.__getAllClasses(classPredicate):
            x = self.get_classDirectSupers(eachclass)
            if not x:
                returnlist.append(eachclass)

        return sort_uri_list_by_name(returnlist)


    def __getTree(self, father=None, out=None):

        """ Reconstructs the taxonomical tree of an ontology, from the 'topClasses' (= classes with no supers, see below)
            Returns a dictionary in which each class is a key, and its direct subs are the values.
            The top classes have key = 0

            Eg.
            {'0' : [class1, class2], class1: [class1-2, class1-3], class2: [class2-1, class2-2]}
        """

        if not father:
            out = {}
            topclasses = self.toplayer
            out[0] = topclasses

            for top in topclasses:
                children = self.get_classDirectSubs(top)
                out[top] = children
                for potentialfather in children:
                    self.__getTree(potentialfather, out)

            return out

        else:
            children = self.get_classDirectSubs(father)
            out[father] = children
            for ch in children:
                self.__getTree(ch, out)

    def __isBlankNode(self, aClass):
        """ small utility that checks if a class is a blank node """
        if type(aClass) == BNode:
            return True
        else:
            return False

def sort_uri_list_by_name(uri_list, bypassNamespace=False):
    """ 
     Sorts a list of uris 
     
     bypassNamespace: 
        based on the last bit (usually the name after the namespace) of a uri
        It checks whether the last bit is specified using a # or just a /, eg:
             rdflib.URIRef('http://purl.org/ontology/mo/Vinyl'),
             rdflib.URIRef('http://purl.org/vocab/frbr/core#Work')
     """
    def get_last_bit(uri_string):
        try:
            x = uri_string.split("#")[1]
        except:
            x = uri_string.split("/")[-1]
        return x

    try:
        if bypassNamespace:
            return sorted(uri_list, key=lambda x: get_last_bit(x.__str__()))
        else:
            return sorted(uri_list)
    except:
        # TODO: do more testing.. maybe use a unicode-safe method instead of __str__
        print "Error in <sort_uri_list_by_name>: possibly a UnicodeEncodeError"
        return uri_list

def remove_duplicates(seq, idfun=None):
    """ removes duplicates from a list, order preserving, as found in
    http://www.peterbe.com/plog/uniqifiers-benchmark
    """
    if seq:
        if idfun is None:
            def idfun(x): return x
        seen = {}
        result = []
        for item in seq:
            marker = idfun(item)
            # in old Python versions:
            # if seen.has_key(marker)
            # but in new ones:
            if marker in seen: continue
            seen[marker] = 1
            result.append(item)
        return result
    else:
        return []