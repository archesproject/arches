import uuid
import re
from itertools import chain
from django.db.models import Q
from django.db import transaction
from rdflib import Namespace, RDF
from rdflib.namespace import SKOS, DCTERMS
from rdflib.graph import Graph
from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.utils.skos import SKOSReader
from arches_controlled_lists.models import List, ListItem, ListItemValue

# define the ARCHES namespace
ARCHES = Namespace(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)


class SKOSReader(SKOSReader):
    def __init__(self):
        super().__init__()
        self.lists = {}
        self.list_items = {}
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
        allowed_languages = {}
        for lang in models.Language.objects.all():
            allowed_languages[lang.code] = lang
        default_lang = allowed_languages[settings.LANGUAGE_CODE]

        # if the graph is of the type rdflib.graph.Graph
        if isinstance(graph, Graph):

            ### Lists ###
            # Search for ConceptSchemes first - these will become Lists
            for scheme, v, o in graph.triples((None, RDF.type, SKOS.ConceptScheme)):
                list_id = self.generate_uuidv5_from_subject(baseuuid, scheme)
                new_list = List(list_id)

                for predicate, object in graph.predicate_objects(subject=scheme):
                    # Get List name from a ConceptScheme's title element
                    if predicate == DCTERMS.title:

                        if not self.language_exists(object, allowed_languages):
                            for lang in models.Language.objects.all():
                                allowed_languages[lang.code] = lang

                        val = self.unwrapJsonLiteral(object)
                        new_list.name = val["value"]

                self.lists[scheme] = new_list

            # Create lookups for valuetypes used during Concept processing
            value_types = models.DValueType.objects.all()
            skos_value_types = value_types.filter(
                Q(namespace="skos") | Q(namespace="arches")
            )
            skos_note_and_label_types = skos_value_types.filter(
                Q(category="note") | Q(category="label")
            )
            skos_value_types = {
                valuetype.valuetype: valuetype for valuetype in skos_value_types
            }
            skos_note_and_label_types = {
                valuetype.valuetype: valuetype
                for valuetype in skos_note_and_label_types
            }

            ### List items & values ###
            # Concepts become ListItems & ListItemValues
            for concept, v, o in graph.triples((None, RDF.type, SKOS.Concept)):
                list_item_id = self.generate_uuidv5_from_subject(baseuuid, concept)
                list_item = ListItem(id=list_item_id)

                # rdf:about is fallback URI for a concept, unless it has dcterms:identifier
                uri = self.unwrapJsonLiteral(str(concept))
                sortorder = 0

                for predicate, object in graph.predicate_objects(subject=concept):
                    if predicate == DCTERMS.identifier:
                        uri = self.unwrapJsonLiteral(str(object))["value"]

                    elif predicate == SKOS.inScheme:
                        list_item.list = self.lists[object]

                    elif any(
                        type in predicate for type in skos_note_and_label_types.keys()
                    ):
                        if not self.language_exists(object, allowed_languages):
                            for lang in models.Language.objects.all():
                                allowed_languages[lang.code] = lang

                        object_language = (
                            allowed_languages[object.language] or default_lang
                        )
                        relation_or_value_type = predicate.replace(SKOS, "").replace(
                            ARCHES, ""
                        )
                        list_item_value = ListItemValue(
                            list_item=list_item,
                            valuetype=skos_value_types.get(relation_or_value_type),
                            language=object_language,
                            value=self.unwrapJsonLiteral(str(object))["value"],
                        )
                        self.list_item_values.append(list_item_value)

                    elif predicate == SKOS.broader:
                        self.relations.append(
                            {
                                "source": self.generate_uuidv5_from_subject(
                                    baseuuid, object
                                ),
                                "type": "broader",
                                "target": list_item,
                            }
                        )
                    elif predicate == SKOS.narrower:
                        self.relations.append(
                            {
                                "source": list_item,
                                "type": "narrower",
                                "target": self.generate_uuidv5_from_subject(
                                    baseuuid, object
                                ),
                            }
                        )

                    elif predicate == ARCHES.sortOrder:
                        sortorder = int(self.unwrapJsonLiteral(str(object))["value"])

                list_item.uri = uri
                list_item.sortorder = sortorder
                self.list_items[list_item_id] = list_item

            ### Relationships ###
            for relation in self.relations:
                source = relation["source"]
                target = relation["target"]
                type = relation["type"]
                if type == "narrower":
                    self.list_items[target].parent = source
                elif type == "broader":
                    self.list_items[source].parent = target

            with transaction.atomic():
                List.objects.bulk_create(self.lists.values())
                ListItem.objects.bulk_create(self.list_items.values())
                ListItemValue.objects.bulk_create(self.list_item_values)

                # TODO: Handle list item pk collisions in polyhierarhcies

                ### Sort order ###
                new_list_items = ListItem.objects.filter(
                    list_id__in=[new_list.pk for new_list in self.lists.values()]
                ).prefetch_related("children")

                parents = set(
                    chain(
                        new_list_items.filter(parent__isnull=True),  # root items
                        new_list_items.exclude(children__isnull=True),  # with children
                    )
                )
                list_items_with_sortorder = []
                for parent in parents:
                    children = {}
                    for child in parent.children.all().prefetch_related(
                        "list_item_values"
                    ):
                        try:
                            prefLabel = child.list_item_values.get(
                                valuetype="prefLabel", language=default_lang
                            )
                        except ListItemValue.DoesNotExist:
                            prefLabel = child.list_item_values.filter(
                                valuetype="prefLabel"
                            ).first()
                        children[prefLabel.value] = child

                    children = [val for key, val in sorted(children.items())]
                    for i, child in enumerate(children):
                        child.sortorder = i
                        list_items_with_sortorder.append(child)

                ListItem.objects.bulk_update(list_items_with_sortorder, ["sortorder"])

    def generate_uuidv5_from_subject(self, baseuuid, subject):
        uuidregx = re.compile(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
        )
        matches = uuidregx.search(str(subject))
        if matches:
            return uuid.UUID(matches.group(0))
        else:
            return uuid.uuid5(baseuuid, str(subject))
