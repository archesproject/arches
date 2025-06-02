import os
import uuid
import re
import logging
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.utils import translation
from django.utils.http import urlencode
from rdflib import Literal, Namespace, RDF, URIRef
from rdflib.namespace import SKOS, DCTERMS
from rdflib.graph import Graph
from time import time
from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.i18n import capitalize_region
from arches.app.utils.skos import SKOSReader
from arches_controlled_lists.models import List, ListItem, ListItemValue

# define the ARCHES namespace
ARCHES = Namespace(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)


class SKOSReader(SKOSReader):
    def __init__(self):
        super().__init__()
        self.lists = []
        self.list_items = []
        self.list_item_values = []

    """
    This class extends the SKOSReader to provide additional functionality
    specific to the Arches controlled lists application.
    """

    def save_controlled_lists_from_skos(
        self,
        graph,
        # overwrite_options="overwrite",
    ):
        baseuuid = uuid.uuid4()
        allowed_languages = models.Language.objects.values_list("code", flat=True)
        default_lang = settings.LANGUAGE_CODE

        # if the graph is of the type rdflib.graph.Graph
        if isinstance(graph, Graph):

            # Search for ConceptSchemes first - these will become Lists
            for scheme, v, o in graph.triples((None, RDF.type, SKOS.ConceptScheme)):
                scheme_id = self.generate_uuidv5_from_subject(baseuuid, scheme)
                new_list = List(scheme_id)

                for predicate, object in graph.predicate_objects(subject=scheme):
                    # Get List name from a ConceptScheme's title element
                    if predicate == DCTERMS.title:

                        if not self.language_exists(object, allowed_languages):
                            allowed_languages = models.Language.objects.values_list(
                                "code", flat=True
                            )

                        val = self.unwrapJsonLiteral(object)
                        new_list.name = val["value"]

                # TODO: Bulk create (and blessed overwrite)
                # list.save()
                self.lists.append(new_list)

            # Create lookups for valuetypes used during Concept processing
            value_types = models.DValueType.objects.all()
            skos_value_types = value_types.filter(
                Q(namespace="skos") | Q(namespace="arches")
            )
            skos_value_types_list = list(
                skos_value_types.values_list("valuetype", flat=True)
            )
            skos_value_types = {
                valuetype.valuetype: valuetype for valuetype in skos_value_types
            }
            dcterms_value_types = value_types.filter(namespace="dcterms")
            dcterms_identifier_type = dcterms_value_types.get(
                valuetype=str(DCTERMS.identifier).replace(str(DCTERMS), "")
            )

            # Concepts become ListItems & ListItemValues
            for concept, v, o in graph.triples((None, RDF.type, SKOS.Concept)):
                list_item_id = self.generate_uuidv5_from_subject(baseuuid, concept)
                list_item = ListItem(id=list_item_id)

                # rdf:about is fallback URI for a concept, unless it has dcterms:identifier
                # which overwrites this value below
                uri = self.unwrapJsonLiteral(str(concept))

                for predicate, object in graph.predicate_objects(subject=concept):
                    if predicate == DCTERMS.identifier:
                        uri = self.unwrapJsonLiteral(str(object))

                    elif str(SKOS) in predicate or str(ARCHES) in predicate:
                        if not self.language_exists(object, allowed_languages):
                            allowed_languages = models.Language.objects.values_list(
                                "code", flat=True
                            )

                        # Get skos element type from predicate (e.g. prefLabel, broader, etc.)
                        relation_or_value_type = predicate.replace(SKOS, "").replace(
                            ARCHES, ""
                        )

                list_item.uri = uri

                # TODO: Tie the list_item to a list
                # list_item.list =
                # list_item.sortorder = # not sure how to determine this from SKOS
                # list_item.guide = False # safe to fall back to False?

                self.list_items.append(list_item)

    def generate_uuidv5_from_subject(self, baseuuid, subject):
        uuidregx = re.compile(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
        )
        matches = uuidregx.search(str(subject))
        if matches:
            return matches.group(0)
        else:
            return str(uuid.uuid5(baseuuid, str(subject)))
