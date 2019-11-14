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
import re
import logging
from django.db import transaction, IntegrityError
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
ARCHES = Namespace(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)


class SKOSReader(object):
    def __init__(self):
        self.nodes = []
        self.relations = []
        self.member_relations = []
        self.logger = logging.getLogger(__name__)

    def read_file(self, path_to_file, format="xml"):
        """
        parse the skos file and extract all available data

        """

        rdf_graph = Graph()

        # bind the namespaces
        rdf_graph.bind("arches", ARCHES)

        try:
            rdf = rdf_graph.parse(source=path_to_file, format=format)
        except:
            raise Exception("Error occurred while parsing the file %s" % path_to_file)
        return rdf

    def save_concepts_from_skos(self, graph, overwrite_options="overwrite", staging_options="keep", bulk_load=False, path=""):
        """
        given an RDF graph, tries to save the concpets to the system

        Keyword arguments:
        overwrite_options -- 'overwrite', 'ignore'
        staging_options -- 'stage', 'keep'

        """

        baseuuid = uuid.uuid4()
        allowed_languages = models.DLanguage.objects.values_list("pk", flat=True)
        default_lang = settings.LANGUAGE_CODE
        if bulk_load is True:
            self.logger.setLevel(logging.ERROR)

        value_types = models.DValueType.objects.all()
        skos_value_types = value_types.filter(Q(namespace="skos") | Q(namespace="arches"))
        skos_value_types_list = list(skos_value_types.values_list("valuetype", flat=True))
        skos_value_types = {valuetype.valuetype: valuetype for valuetype in skos_value_types}
        dcterms_value_types = value_types.filter(namespace="dcterms")
        dcterms_identifier_type = dcterms_value_types.get(valuetype=str(DCTERMS.identifier).replace(str(DCTERMS), ""))

        # if the graph is of the type rdflib.graph.Graph
        if isinstance(graph, Graph):
            values = []

            # Search for ConceptSchemes first
            for scheme, v, o in graph.triples((None, RDF.type, SKOS.ConceptScheme)):
                identifier = self.unwrapJsonLiteral(str(scheme))
                scheme_id = self.generate_uuid_from_subject(baseuuid, scheme)
                if bulk_load is True:
                    concept_scheme = models.Concept(pk=scheme_id, legacyoid=str(scheme), nodetype_id="ConceptScheme")
                else:
                    concept_scheme = Concept({"id": scheme_id, "legacyoid": str(scheme), "nodetype": "ConceptScheme"})

                for predicate, object in graph.predicate_objects(subject=scheme):
                    if str(DCTERMS) in predicate and predicate.replace(DCTERMS, "") in dcterms_value_types.values_list(
                        "valuetype", flat=True
                    ):
                        if not self.language_exists(object, allowed_languages):
                            allowed_languages = models.DLanguage.objects.values_list("pk", flat=True)

                        try:
                            # first try and get any values associated with the concept_scheme
                            # predicate.replace(SKOS, '') should yield something like 'prefLabel' or 'scopeNote', etc..
                            value_type = dcterms_value_types.get(valuetype=predicate.replace(DCTERMS, ""))
                            val = self.unwrapJsonLiteral(object)
                            if predicate == DCTERMS.title:
                                if bulk_load is True:
                                    values.append(
                                        models.Value(
                                            pk=val["value_id"]
                                            if (val["value_id"] != "" and val["value_id"] is not None)
                                            else str(uuid.uuid4()),
                                            concept_id=concept_scheme.pk,
                                            value=val["value"],
                                            language_id=object.language or default_lang,
                                            valuetype_id="prefLabel",
                                        )
                                    )
                                else:
                                    concept_scheme.addvalue(
                                        {
                                            "id": val["value_id"],
                                            "value": val["value"],
                                            "language": object.language or default_lang,
                                            "type": "prefLabel",
                                            "category": value_type.category,
                                        }
                                    )
                                # print('Casting dcterms:title to skos:prefLabel')
                            elif predicate == DCTERMS.description:
                                if bulk_load is True:
                                    values.append(
                                        models.Value(
                                            pk=val["value_id"]
                                            if (val["value_id"] != "" and val["value_id"] is not None)
                                            else str(uuid.uuid4()),
                                            concept_id=concept_scheme.pk,
                                            value=val["value"],
                                            language_id=object.language or default_lang,
                                            valuetype_id="scopeNote",
                                        )
                                    )
                                else:
                                    concept_scheme.addvalue(
                                        {
                                            "id": val["value_id"],
                                            "value": val["value"],
                                            "language": object.language or default_lang,
                                            "type": "scopeNote",
                                            "category": value_type.category,
                                        }
                                    )
                                # print('Casting dcterms:description to skos:scopeNote')
                            elif predicate == DCTERMS.identifier:
                                identifier = self.unwrapJsonLiteral(str(object))
                        except:
                            pass

                    if str(SKOS) in predicate:
                        # print predicate
                        if predicate == SKOS.hasTopConcept:
                            top_concept_id = self.generate_uuid_from_subject(baseuuid, object)
                            self.relations.append(
                                {"source": scheme_id, "type": "hasTopConcept", "target": top_concept_id,}
                            )

                if bulk_load is True:
                    values.append(
                        models.Value(
                            pk=identifier["value_id"]
                            if (identifier["value_id"] != "" and identifier["value_id"] is not None)
                            else str(uuid.uuid4()),
                            concept_id=concept_scheme.pk,
                            value=identifier["value"],
                            language_id=default_lang,
                            valuetype_id=dcterms_identifier_type.valuetype,
                        )
                    )
                else:
                    concept_scheme.addvalue(
                        {
                            "id": identifier["value_id"],
                            "value": identifier["value"],
                            "language": default_lang,
                            "type": dcterms_identifier_type.valuetype,
                            "category": dcterms_identifier_type.category,
                        }
                    )
                self.nodes.append(concept_scheme)

                # Search for Concepts
                for s, v, o in graph.triples((None, SKOS.inScheme, scheme)):
                    identifier = self.unwrapJsonLiteral(str(s))
                    if bulk_load is True:
                        concept = models.Concept(pk=self.generate_uuid_from_subject(baseuuid, s), legacyoid=str(s), nodetype_id="Concept",)
                    else:
                        concept = Concept({"id": self.generate_uuid_from_subject(baseuuid, s), "legacyoid": str(s), "nodetype": "Concept"})

                    # loop through all the elements within a <skos:Concept> element
                    for predicate, object in graph.predicate_objects(subject=s):
                        if str(SKOS) in predicate or str(ARCHES) in predicate:
                            if not self.language_exists(object, allowed_languages):
                                allowed_languages = models.DLanguage.objects.values_list("pk", flat=True)

                            # this is essentially the skos element type within a <skos:Concept>
                            # element (eg: prefLabel, broader, etc...)
                            relation_or_value_type = predicate.replace(SKOS, "").replace(ARCHES, "")

                            if relation_or_value_type in skos_value_types_list:
                                value_type = skos_value_types[relation_or_value_type]
                                val = self.unwrapJsonLiteral(object)
                                if bulk_load is True:
                                    values.append(
                                        models.Value(
                                            pk=val["value_id"]
                                            if (val["value_id"] != "" and val["value_id"] is not None)
                                            else str(uuid.uuid4()),
                                            concept_id=concept.pk,
                                            value=val["value"],
                                            language_id=object.language or default_lang,
                                            valuetype_id=value_type.valuetype,
                                        )
                                    )
                                else:
                                    concept.addvalue(
                                        {
                                            "id": val["value_id"],
                                            "value": val["value"],
                                            "language": object.language or default_lang,
                                            "type": value_type.valuetype,
                                            "category": value_type.category,
                                        }
                                    )
                            elif predicate == SKOS.broader:
                                self.relations.append(
                                    {
                                        "source": self.generate_uuid_from_subject(baseuuid, object),
                                        "type": "narrower",
                                        "target": self.generate_uuid_from_subject(baseuuid, s),
                                    }
                                )
                            elif predicate == SKOS.narrower:
                                self.relations.append(
                                    {
                                        "source": self.generate_uuid_from_subject(baseuuid, s),
                                        "type": relation_or_value_type,
                                        "target": self.generate_uuid_from_subject(baseuuid, object),
                                    }
                                )
                            elif predicate == SKOS.related:
                                self.relations.append(
                                    {
                                        "source": self.generate_uuid_from_subject(baseuuid, s),
                                        "type": relation_or_value_type,
                                        "target": self.generate_uuid_from_subject(baseuuid, object),
                                    }
                                )

                        elif predicate == DCTERMS.identifier:
                            identifier = self.unwrapJsonLiteral(str(object))

                    if bulk_load is True:
                        values.append(
                            models.Value(
                                pk=identifier["value_id"]
                                if (identifier["value_id"] != "" and identifier["value_id"] is not None)
                                else str(uuid.uuid4()),
                                concept_id=concept.pk,
                                value=identifier["value"],
                                language_id=default_lang,
                                valuetype_id=dcterms_identifier_type.valuetype,
                            )
                        )
                    else:
                        concept.addvalue(
                            {
                                "id": identifier["value_id"],
                                "value": identifier["value"],
                                "language": default_lang,
                                "type": dcterms_identifier_type.valuetype,
                                "category": dcterms_identifier_type.category,
                            }
                        )
                    self.nodes.append(concept)

            # Search for SKOS.Collections
            for s, v, o in graph.triples((None, RDF.type, SKOS.Collection)):
                # print "%s %s %s " % (s,v,o)
                if bulk_load is True:
                    concept = models.Concept(pk=self.generate_uuid_from_subject(baseuuid, s), legacyoid=str(s), nodetype_id="Collection",)
                else:
                    concept = Concept({"id": self.generate_uuid_from_subject(baseuuid, s), "legacyoid": str(s), "nodetype": "Collection"})
                # loop through all the elements within a <skos:Concept> element
                for predicate, object in graph.predicate_objects(subject=s):
                    if str(SKOS) in predicate or str(ARCHES) in predicate:
                        if not self.language_exists(object, allowed_languages):
                            allowed_languages = models.DLanguage.objects.values_list("pk", flat=True)

                        # this is essentially the skos element type within a <skos:Concept>
                        # element (eg: prefLabel, broader, etc...)
                        relation_or_value_type = predicate.replace(SKOS, "").replace(ARCHES, "")

                        if relation_or_value_type in skos_value_types_list:
                            value_type = skos_value_types[relation_or_value_type]
                            val = self.unwrapJsonLiteral(object)
                            if bulk_load is True:
                                values.append(
                                    models.Value(
                                        pk=val["value_id"],
                                        concept_id=concept.pk,
                                        value=val["value"],
                                        language_id=object.language or default_lang,
                                        valuetype_id=value_type.valuetype,
                                    )
                                )
                            else:
                                concept.addvalue(
                                    {
                                        "id": val["value_id"],
                                        "value": val["value"],
                                        "language": object.language or default_lang,
                                        "type": value_type.valuetype,
                                        "category": value_type.category,
                                    }
                                )

                self.nodes.append(concept)

            for s, v, o in graph.triples((None, SKOS.member, None)):
                # print "%s %s %s " % (s,v,o)
                self.member_relations.append(
                    {
                        "source": self.generate_uuid_from_subject(baseuuid, s),
                        "type": "member",
                        "target": self.generate_uuid_from_subject(baseuuid, o),
                    }
                )

            # insert and index the concpets
            scheme_node = None
            orphaned_concepts = {}
            concepts = []
            # bulk_create() does NOT call the object's save() method, nor pre_save/post_save
            # TODO: figure out how to ensure functions get called with bulk_create()
            with transaction.atomic():
                if bulk_load is True:
                    models.Concept.objects.bulk_create(self.nodes, ignore_conflicts=True)
                    models.Value.objects.bulk_create(values, ignore_conflicts=True)
                    self.logger.info(f"Bulk created: {len(self.nodes)} concepts and {len(values)} values from {path}")
                    for node in self.nodes:
                        if node.nodetype.nodetype == "ConceptScheme":
                            scheme_node = Concept({"id": node.conceptid, "legacyoid": str(scheme), "nodetype": "ConceptScheme",})
                        elif node.nodetype.nodetype == "Concept":
                            orphaned_concepts[str(node.conceptid)] = node
                        if staging_options == "stage":
                            try:
                                models.Concept.objects.get(pk=node.conceptid)
                            except:
                                # this is a new concept, so add a reference to it in the Candiates schema
                                if node.nodetype.nodetype != "ConceptScheme":
                                    self.relations.append(
                                        {"source": "00000000-0000-0000-0000-000000000006", "type": "narrower", "target": node.conceptid,}
                                    )

                        if overwrite_options == "overwrite":
                            node.save()
                            # concepts.append(node)
                        elif overwrite_options == "ignore":
                            try:
                                # don't do anything if the concept already exists
                                models.Concept.objects.get(pk=node.conceptid)
                            except:
                                # else save it
                                node.save()
                                # concepts.append(node)
                else:
                    for node in self.nodes:
                        if node.nodetype == "ConceptScheme":
                            scheme_node = node
                        elif node.nodetype == "Concept":
                            orphaned_concepts[str(node.id)] = node
                        if staging_options == "stage":
                            try:
                                models.Concept.objects.get(pk=node.id)
                            except:
                                # this is a new concept, so add a reference to it in the Candiates schema
                                if node.nodetype != "ConceptScheme":
                                    self.relations.append(
                                        {"source": "00000000-0000-0000-0000-000000000006", "type": "narrower", "target": node.id}
                                    )

                        if overwrite_options == "overwrite":
                            node.save()
                        elif overwrite_options == "ignore":
                            try:
                                # don't do anything if the concept already exists
                                models.Concept.objects.get(pk=node.id)
                            except:
                                # else save it
                                node.save()

                # Concept().bulk_save(concepts, None)

                # insert the concept relations
                # TODO: make sure this still works with code commented out, then remove
                # relation_objs = []
                for relation in self.relations:
                    newrelation, created = models.Relation.objects.get_or_create(
                        conceptfrom_id=relation["source"], conceptto_id=relation["target"], relationtype_id=relation["type"],
                    )
                    # models.Relation.objects.bulk_create(relation_objs)
                    # check for orphaned concepts, every concept except the concept scheme should have an edge pointing to it
                    if (relation["type"] == "narrower" or relation["type"] == "hasTopConcept") and orphaned_concepts.get(
                        relation["target"]
                    ) is not None:
                        orphaned_concepts.pop(str(relation["target"]))
                    # relation_objs.append(newrelation)

                if len(orphaned_concepts.keys()) > 0:
                    if scheme_node:
                        orphaned_scheme = Concept({"id": uuid.uuid4(), "legacyoid": uuid.uuid4(), "nodetype": "ConceptScheme",})
                        orphaned_scheme_value = None
                        for value in scheme_node.values:
                            if value.type == "prefLabel":
                                orphaned_scheme.addvalue(
                                    {
                                        "id": uuid.uuid4(),
                                        "value": "ORPHANS - " + value.value,
                                        "language": value.language,
                                        "type": value.type,
                                        "category": value.category,
                                    }
                                )
                        orphaned_scheme.save()
                        for (orphaned_concept_id, orphaned_concept,) in orphaned_concepts.items():
                            models.Relation.objects.create(
                                conceptfrom_id=str(orphaned_scheme.id), conceptto_id=orphaned_concept_id, relationtype_id="narrower",
                            )
                        self.logger.warning("The SKOS file appears to have orphaned concepts.")

                # need to index after the concepts and relations have been entered into the db
                # so that the proper context gets indexed with the concept
                if scheme_node:
                    scheme_node.bulk_index()

            # insert the concept collection relations
            # we do this outide a transaction so that we can load incomplete collections
            # relation_objs = []
            # TODO: debug bulk_create to speed up this section of skos
            for relation in self.member_relations:
                try:
                    # if bulk_load is True:
                    # newrelation = models.Relation(
                    #     conceptfrom_id=relation['source'],
                    #     conceptto_id=relation['target'],
                    #     relationtype_id=relation['type']
                    # )
                    # relation_objs.append(newrelation)
                    # else:
                    newrelation, created = models.Relation.objects.get_or_create(
                        conceptfrom_id=relation["source"], conceptto_id=relation["target"], relationtype_id=relation["type"],
                    )
                except IntegrityError as e:
                    self.logger.warning(e)
                    pass

            # if bulk_load is True:
            #   models.Relation.objects.bulk_create(relation_objs, ignore_conflicts=True)

            return scheme_node
        else:
            raise Exception("graph argument should be of type rdflib.graph.Graph")

    def unwrapJsonLiteral(self, jsonObj):
        ret = {"value_id": "", "value": jsonObj}

        try:
            jsonLiteralValue = JSONDeserializer().deserialize(jsonObj)
            ret["value_id"] = str(jsonLiteralValue["id"])
            ret["value"] = jsonLiteralValue["value"]
        except:
            pass

        return ret

    def generate_uuid_from_subject(self, baseuuid, subject):
        uuidregx = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
        matches = uuidregx.search(str(subject))
        if matches:
            return matches.group(0)
        else:
            return str(uuid.uuid3(baseuuid, str(subject)))

    def language_exists(self, rdf_tag, allowed_languages):
        if (
            hasattr(rdf_tag, "language")
            and rdf_tag.language not in allowed_languages
            and rdf_tag.language is not None
            and rdf_tag.language.strip() != ""
        ):
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

    def write(self, concept_graphs, format="pretty-xml"):
        serializer = JSONSerializer()

        # get empty RDF graph
        rdf_graph = Graph()

        # bind the namespaces
        rdf_graph.bind("arches", ARCHES)
        rdf_graph.bind("skos", SKOS)
        rdf_graph.bind("dcterms", DCTERMS)

        """
        #add main concept to the graph
        rdf_graph.add((subject, predicate, object))
        rdf_graph.add((ARCHES[node.id], RDF['type'], SKOS.Concept))
        rdf_graph.add((Arches guid, SKOS.prefLabel, Literal('Stone',lang=en)))
        """

        if not isinstance(concept_graphs, list):
            concept_graphs = [concept_graphs]

        for concept_graph in concept_graphs:
            if concept_graph.nodetype == "ConceptScheme" or concept_graph.nodetype == "Concept":
                scheme_id = concept_graph.id
                if concept_graph.nodetype == "Concept":
                    scheme = concept_graph.get_scheme()
                    scheme_id = scheme.id if scheme is not None else None

                def build_skos(node):
                    if node.nodetype == "Concept":
                        rdf_graph.add((ARCHES[node.id], SKOS.inScheme, ARCHES[scheme_id]))

                    for subconcept in node.subconcepts:
                        rdf_graph.add((ARCHES[node.id], SKOS[subconcept.relationshiptype], ARCHES[subconcept.id],))

                    for relatedconcept in node.relatedconcepts:
                        rdf_graph.add((ARCHES[node.id], SKOS[relatedconcept.relationshiptype], ARCHES[relatedconcept.id],))

                    for value in node.values:
                        jsonLiteralValue = serializer.serialize({"value": value.value, "id": value.id})
                        if value.category == "label" or value.category == "note":
                            if node.nodetype == "ConceptScheme":
                                if value.type == "prefLabel":
                                    # TODO: remove lowercasing of value.language once the pyld module
                                    # can accept mixedcase language tags
                                    rdf_graph.add(
                                        (ARCHES[node.id], DCTERMS.title, Literal(jsonLiteralValue, lang=value.language.lower(),),)
                                    )
                                elif value.type == "scopeNote":
                                    rdf_graph.add(
                                        (ARCHES[node.id], DCTERMS.description, Literal(jsonLiteralValue, lang=value.language.lower(),),)
                                    )
                            else:
                                rdf_graph.add((ARCHES[node.id], SKOS[value.type], Literal(jsonLiteralValue, lang=value.language.lower(),),))
                        elif value.type == "identifier":
                            rdf_graph.add((ARCHES[node.id], DCTERMS.identifier, Literal(jsonLiteralValue, lang=value.language.lower()),))
                        else:
                            rdf_graph.add(
                                (
                                    ARCHES[node.id],
                                    ARCHES[value.type.replace(" ", "_")],
                                    Literal(jsonLiteralValue, lang=value.language.lower()),
                                )
                            )

                    rdf_graph.add((ARCHES[node.id], RDF.type, SKOS[node.nodetype]))

                concept_graph.traverse(build_skos)

            elif concept_graph.nodetype == "Collection":
                scheme_id = concept_graph.id

                def build_skos(node):
                    for subconcept in node.subconcepts:
                        rdf_graph.add((ARCHES[node.id], SKOS[subconcept.relationshiptype], ARCHES[subconcept.id],))

                    rdf_graph.add((ARCHES[node.id], RDF.type, SKOS[node.nodetype]))
                    if node.nodetype == "Collection":
                        for value in node.values:
                            if value.category == "label" or value.category == "note":
                                jsonLiteralValue = serializer.serialize({"value": value.value, "id": value.id})
                                rdf_graph.add((ARCHES[node.id], SKOS[value.type], Literal(jsonLiteralValue, lang=value.language.lower(),),))

                concept_graph.traverse(build_skos)
            else:
                raise Exception("Only ConceptSchemes and Collections can be written to SKOS RDF files.")

        return rdf_graph.serialize(format=format)
