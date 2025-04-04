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

import datetime
import logging
from time import time
from uuid import UUID
from types import SimpleNamespace
from django.db import transaction
from django.db.models import Count, Prefetch, Q
from django.contrib.auth.models import User, Group
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.utils.translation import gettext as _
from django.utils.translation import get_language
from arches.app.models import models
from arches.app.models.models import EditLog
from arches.app.models.models import TileModel
from arches.app.models.system_settings import settings
from arches.app.models.utils import add_to_update_fields
from arches.app.search.search_engine_factory import SearchEngineInstance as se
from arches.app.search.mappings import TERMS_INDEX, RESOURCES_INDEX
from arches.app.search.elasticsearch_dsl_builder import Query, Bool, Terms, Nested
from arches.app.search.es_mapping_modifier import EsMappingModifierFactory
from arches.app.tasks import index_resource
from arches.app.utils import import_class_from_string, task_management
from arches.app.utils import permission_backend
from arches.app.utils.i18n import rank_label
from arches.app.utils.label_based_graph import LabelBasedGraph
from arches.app.utils.label_based_graph_v2 import LabelBasedGraph as LabelBasedGraphV2
from arches.app.utils.permission_backend import (
    assign_perm,
    remove_perm,
)
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.exceptions import (
    InvalidNodeNameException,
    MultipleNodesFoundException,
)
from arches.app.utils.permission_backend import (
    user_is_resource_reviewer,
    get_filtered_instances,
    get_nodegroups_by_perm,
)
import django.dispatch
from arches.app.datatypes.datatypes import DataTypeFactory

logger = logging.getLogger(__name__)


class Resource(models.ResourceInstance):

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(Resource, self).__init__(*args, **kwargs)
        # from models.ResourceInstance
        # self.resourceinstanceid
        # self.graph
        # self.resourceinstancesecurity
        # end from models.ResourceInstance
        self.tiles = []
        self.descriptor_function = None
        self.serialized_graph = None
        self.node_datatypes = None

    def get_serialized_graph(self):
        if not self.serialized_graph:
            try:
                published_graph = self.graph.get_published_graph()
                self.serialized_graph = published_graph.serialized_graph
            except AttributeError:
                self.serialized_graph = None
        return self.serialized_graph

    def set_serialized_graph(self, serialized_graph):
        self.serialized_graph = serialized_graph

    def get_node_datatypes(self):
        if not self.node_datatypes:
            self.node_datatypes = {
                str(nodeid): datatype
                for nodeid, datatype in models.Node.objects.values_list(
                    "nodeid", "datatype"
                )
            }
        return self.node_datatypes

    def set_node_datatypes(self, node_datatypes):
        self.node_datatypes = node_datatypes

    def get_root_ontology(self):
        """
        Finds and returns the ontology class of the instance's root node

        """
        if "root" in self.get_serialized_graph():
            return self.get_serialized_graph()["root"]["ontologyclass"]
        else:
            return SimpleNamespace(
                **next(
                    (
                        x
                        for x in self.get_serialized_graph()["nodes"]
                        if x["istopnode"] is True
                    ),
                    None,
                )
            ).ontologyclass

    def get_descriptor_language(self, context):
        """
        context -- Dictionary which may have:
            language -- Language code in which the descriptor should be returned (e.g. 'en').
                This occurs when handling concept values.
            any key:value pairs needed to control the behavior of a custom descriptor function

        """

        if self.descriptors is None:
            self.descriptors = {}

        if self.name is None:
            self.name = {}

        requested_language = None

        if context and "language" in context:
            requested_language = context["language"]
        language = requested_language or get_language()

        if language not in self.descriptors:
            self.descriptors[language] = {}

        return language

    def get_descriptor(self, descriptor, context):
        """
        descriptor -- string descriptor type: "name", "description", "map_popup"
        context -- Dictionary which may have:
            language -- Language code in which the descriptor should be returned (e.g. 'en').
                This occurs when handling concept values.
            any key:value pairs needed to control the behavior of a custom descriptor function

        """

        language = self.get_descriptor_language(context)

        if self.descriptors:
            try:
                return self.descriptors[language][descriptor]
            except KeyError:
                pass

    def save_descriptors(
        self, descriptors=("name", "description", "map_popup"), context=None
    ):
        """
        descriptors -- iterator with descriptors to be calculated
        context -- Dictionary with any key:value pairs needed to control the behavior of a custom descriptor function

        """

        if self.descriptor_function is None:  # might be empty queryset
            self.descriptor_function = models.FunctionXGraph.objects.filter(
                graph_id=self.graph_id, function__functiontype="primarydescriptors"
            ).select_related("function")

        for lang in settings.LANGUAGES:
            language = self.get_descriptor_language({"language": lang[0]})
            if context:
                context["language"] = language
            else:
                context = {"language": language}

            for descriptor in descriptors:
                if len(self.descriptor_function) == 1:
                    module = self.descriptor_function[0].function.get_class_module()()
                    self.descriptors[language][descriptor] = (
                        module.get_primary_descriptor_from_nodes(
                            self,
                            self.descriptor_function[0].config["descriptor_types"][
                                descriptor
                            ],
                            context,
                            descriptor,
                        )
                    )
                    if (
                        descriptor == "name"
                        and self.descriptors[language][descriptor] is not None
                    ):
                        self.name[language] = self.descriptors[language][descriptor]
                else:
                    self.descriptors[language][descriptor] = None

        super(Resource, self).save()

    def displaydescription(self, context=None):
        return self.get_descriptor("description", context)

    def map_popup(self, context=None):
        return self.get_descriptor("map_popup", context)

    def displayname(self, context=None):
        return self.get_descriptor("name", context)

    def save_edit(
        self,
        user={},
        note="",
        edit_type="",
        oldvalue=None,
        newvalue=None,
        transaction_id=None,
    ):
        timestamp = datetime.datetime.now()
        edit = EditLog()
        edit.resourceclassid = self.graph_id
        edit.resourceinstanceid = self.resourceinstanceid
        edit.userid = getattr(user, "id", "")
        edit.user_email = getattr(user, "email", "")
        edit.user_firstname = getattr(user, "first_name", "")
        edit.user_lastname = getattr(user, "last_name", "")
        edit.user_username = getattr(user, "username", "")
        edit.note = note
        edit.timestamp = timestamp
        edit.oldvalue = oldvalue
        edit.newvalue = newvalue
        if transaction_id is not None:
            edit.transactionid = transaction_id
        edit.edittype = edit_type
        edit.save()

    def save(self, **kwargs):
        """
        Saves and indexes a single resource

        Keyword Arguments:
        request -- the request object
        user -- the user to associate the edit with if the user can't be derived from the request
        index -- True(default) to index the resource, otherwise don't index the resource

        """
        # This initializes serialized graph (for use in superclass?). Setup for the above. NOt sure
        if not self.get_serialized_graph():
            pass

        context = kwargs.pop("context", None)
        index = kwargs.pop("index", True)
        request = kwargs.pop("request", None)
        transaction_id = kwargs.pop("transaction_id", None)
        should_update_resource_instance_lifecycle_state = kwargs.pop(
            "should_update_resource_instance_lifecycle_state", False
        )
        current_resource_instance_lifecycle_state = kwargs.pop(
            "current_resource_instance_lifecycle_state", None
        )
        user = kwargs.pop("user", None)

        if request is None:
            if user is None:
                user = {}
        else:
            user = request.user

        if not self.principaluser_id and user:
            self.principaluser_id = user.id
            add_to_update_fields(kwargs, "principaluser_id")

        super(Resource, self).save(**kwargs)

        if should_update_resource_instance_lifecycle_state:
            self.save_edit(
                user=user,
                edit_type="update_resource_instance_lifecycle_state",
                oldvalue=f"{current_resource_instance_lifecycle_state.name} ({current_resource_instance_lifecycle_state.id})",
                newvalue=f"{self.resource_instance_lifecycle_state.name} ({self.resource_instance_lifecycle_state.id})",
                transaction_id=transaction_id,
            )
            self.index(context)
            return

        self.save_edit(user=user, edit_type="create", transaction_id=transaction_id)

        for tile in self.tiles:
            tile.resourceinstance_id = self.resourceinstanceid
            tile.save(
                request=request,
                index=False,
                resource_creation=True,
                transaction_id=transaction_id,
                context=context,
            )

        if index is True:
            self.index(context)

    def load_tiles(self, user=None, perm="read_nodegroup"):
        """
        Loads the resource's tiles array with all the tiles from the database as a flat list

        """

        self.tiles = list(models.TileModel.objects.filter(resourceinstance=self))
        if user:
            readable_nodegroups = get_nodegroups_by_perm(user, perm, any_perm=True)
            self.tiles = [
                tile
                for tile in self.tiles
                if tile.nodegroup_id is not None
                and tile.nodegroup_id in readable_nodegroups
            ]

    # # flatten out the nested tiles into a single array
    def get_flattened_tiles(self):
        tiles = []
        for tile in self.tiles:
            tiles.extend(tile.get_flattened_tiles())
        return tiles

    @staticmethod
    def bulk_save(resources, transaction_id=None):
        """
        Saves and indexes a list of resources

        Arguments:
        resources -- a list of resource models

        Keyword Arguments:
        transaction_id -- a uuid identifing the save of these instances as belonging to a collective load or process

        """

        datatype_factory = DataTypeFactory()
        node_datatypes = {
            str(nodeid): datatype
            for nodeid, datatype in models.Node.objects.values_list(
                "nodeid", "datatype"
            )
        }
        tiles = []
        documents = []
        term_list = []

        for resource in resources:
            resource.tiles = resource.get_flattened_tiles()
            tiles.extend(resource.tiles)

        # need to save the models first before getting the documents for index
        start = time()
        Resource.objects.bulk_create(resources)
        TileModel.objects.bulk_create(tiles)

        print(
            f"Time to bulk create tiles and resources: {datetime.timedelta(seconds=time() - start)}"
        )

        start = time()
        for resource in resources:
            resource.save_edit(edit_type="create", transaction_id=transaction_id)

        resources[0].tiles[0].save_edit(
            note=f"Bulk created: {len(tiles)} for {len(resources)} resources.",
            edit_type="bulk_create",
            transaction_id=transaction_id,
        )

        print(
            "Time to save resource edits: %s"
            % datetime.timedelta(seconds=time() - start)
        )

        for resource in resources:
            start = time()
            document, terms = resource.get_documents_to_index(
                fetchTiles=False,
                datatype_factory=datatype_factory,
                node_datatypes=node_datatypes,
            )

            documents.append(
                se.create_bulk_item(
                    index=RESOURCES_INDEX,
                    id=document["resourceinstanceid"],
                    data=document,
                )
            )

            for term in terms:
                term_list.append(
                    se.create_bulk_item(
                        index=TERMS_INDEX, id=term["_id"], data=term["_source"]
                    )
                )

        se.bulk_index(documents)
        se.bulk_index(term_list)

    def index(self, context=None):
        """
        Indexes all the necessary items values of a resource to support search

        Keyword Arguments:
        context -- a string such as "copy" to indicate conditions under which a document is indexed
        """

        if str(self.graph_id) != str(settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID):
            datatype_factory = DataTypeFactory()

            node_datatypes = {
                str(nodeid): datatype
                for nodeid, datatype in (
                    (k["nodeid"], k["datatype"])
                    for k in self.get_serialized_graph()["nodes"]
                )
            }
            document, terms = self.get_documents_to_index(
                datatype_factory=datatype_factory,
                node_datatypes=node_datatypes,
                context=context,
            )
            document["root_ontology_class"] = self.get_root_ontology()
            doc = JSONSerializer().serializeToPython(document)

            se.index_data(index=RESOURCES_INDEX, body=doc, id=self.pk)
            for term in terms:
                se.index_data("terms", body=term["_source"], id=term["_id"])

            if len(settings.ELASTICSEARCH_CUSTOM_INDEXES) > 0:
                celery_worker_running = task_management.check_if_celery_available()

                for index in settings.ELASTICSEARCH_CUSTOM_INDEXES:
                    if celery_worker_running and index.get(
                        "should_update_asynchronously"
                    ):
                        index_resource.apply_async(
                            [
                                index["module"],
                                index["name"],
                                self.pk,
                                [tile.pk for tile in document["tiles"]],
                            ]
                        )
                    else:
                        es_index = import_class_from_string(index["module"])(
                            index["name"]
                        )
                        doc, doc_id = es_index.get_documents_to_index(
                            self, document["tiles"]
                        )
                        es_index.index_document(document=doc, id=doc_id)

            resource_indexed = django.dispatch.Signal()
            resource_indexed.send(sender=self.__class__, instance=self)

    def get_documents_to_index(
        self, fetchTiles=True, datatype_factory=None, node_datatypes=None, context=None
    ):
        """
        Gets all the documents nessesary to index a single resource
        returns a tuple of a document and list of terms

        Keyword Arguments:
        fetchTiles -- instead of fetching the tiles from the database get them off the model itself
        datatype_factory -- refernce to the DataTypeFactory instance
        node_datatypes -- a dictionary of datatypes keyed to node ids
        context -- a string such as "copy" to indicate conditions under which a document is indexed

        """

        document = {}
        document["displaydescription"] = None
        document["resourceinstanceid"] = str(self.resourceinstanceid)
        document["graph_id"] = str(self.graph_id)
        document["map_popup"] = None
        document["displayname"] = None
        document["root_ontology_class"] = self.get_root_ontology()
        document["legacyid"] = self.legacyid
        document["resource_instance_lifecycle_state_id"] = str(
            self.resource_instance_lifecycle_state.pk
        )

        document["displayname"] = []
        document["displaydescription"] = []
        document["map_popup"] = []
        for lang in settings.LANGUAGES:
            if context is None:
                context = {}
            context["language"] = lang[0]
            displayname = self.displayname(context)
            if displayname is not None and displayname != "Undefined":
                try:
                    display_name = JSONDeserializer().deserialize(displayname)
                    for key in display_name.keys():
                        document["displayname"].append(
                            {"value": display_name[key]["value"], "language": key}
                        )
                except:
                    display_name = {"value": displayname, "language": lang[0]}
                    document["displayname"].append(display_name)

            displaydescription = self.displaydescription(context)
            if displaydescription is not None and displaydescription != "Undefined":
                try:
                    display_description = JSONDeserializer().deserialize(
                        displaydescription
                    )
                    for key in display_description.keys():
                        document["displaydescription"].append(
                            {
                                "value": display_description[key]["value"],
                                "language": key,
                            }
                        )
                except:
                    display_description = {
                        "value": displaydescription,
                        "language": lang[0],
                    }
                    document["displaydescription"].append(display_description)

            mappopup = self.map_popup(context)
            if mappopup is not None and mappopup != "Undefined":
                try:
                    map_popup = JSONDeserializer().deserialize(mappopup)
                    for key in map_popup.keys():
                        document["map_popup"].append(
                            {"value": map_popup[key]["value"], "language": key}
                        )
                except:
                    map_popup = {"value": mappopup, "language": lang[0]}
                    document["map_popup"].append(map_popup)

        tiles = (
            list(models.TileModel.objects.filter(resourceinstance=self))
            if fetchTiles
            else self.tiles
        )

        document["tiles"] = tiles
        document["permissions"] = {
            "principal_user": (
                [int(self.principaluser_id)] if self.principaluser_id else []
            )
        }
        document["permissions"].update(permission_backend.get_index_values(self))

        document["strings"] = []
        document["dates"] = []
        document["domains"] = []
        document["geometries"] = []
        document["points"] = []
        document["numbers"] = []
        document["date_ranges"] = []
        document["ids"] = []
        tiles_have_authoritative_data = any(
            any(val is not None for val in t.data.values()) for t in tiles
        )
        document["provisional_resource"] = (
            "true" if tiles and not tiles_have_authoritative_data else "false"
        )

        terms = []

        for tile in document["tiles"]:
            for nodeid, nodevalue in tile.data.items():
                if (
                    nodevalue != ""
                    and nodevalue != []
                    and nodevalue != {}
                    and nodevalue is not None
                ):
                    datatype = node_datatypes[nodeid]
                    datatype_instance = datatype_factory.get_instance(datatype)
                    datatype_instance.append_to_document(
                        document, nodevalue, nodeid, tile
                    )
                    node_terms = datatype_instance.get_search_terms(nodevalue, nodeid)

                    for index, term in enumerate(node_terms):
                        terms.append(
                            {
                                "_id": str(nodeid)
                                + str(tile.tileid)
                                + str(index)
                                + term.lang,
                                "_source": {
                                    "value": term.value,
                                    "nodeid": nodeid,
                                    "nodegroupid": tile.nodegroup_id,
                                    "tileid": tile.tileid,
                                    "language": term.lang,
                                    "resourceinstanceid": tile.resourceinstance_id,
                                    "provisional": False,
                                },
                            }
                        )

            if tile.provisionaledits is not None:
                provisionaledits = tile.provisionaledits
                if len(provisionaledits) > 0:
                    if document["provisional_resource"] == "false":
                        document["provisional_resource"] = "partial"
                    for user, edit in provisionaledits.items():
                        if edit["status"] == "review":
                            for nodeid, nodevalue in edit["value"].items():
                                if (
                                    nodevalue != ""
                                    and nodevalue != []
                                    and nodevalue != {}
                                    and nodevalue is not None
                                ):
                                    datatype = node_datatypes[nodeid]
                                    datatype_instance = datatype_factory.get_instance(
                                        datatype
                                    )
                                    datatype_instance.append_to_document(
                                        document, nodevalue, nodeid, tile, True
                                    )
                                    node_terms = datatype_instance.get_search_terms(
                                        nodevalue, nodeid
                                    )

                                    for index, term in enumerate(node_terms):
                                        terms.append(
                                            {
                                                "_id": str(nodeid)
                                                + str(tile.tileid)
                                                + str(index)
                                                + term.lang,
                                                "_source": {
                                                    "value": term.value,
                                                    "nodeid": nodeid,
                                                    "nodegroupid": tile.nodegroup_id,
                                                    "tileid": tile.tileid,
                                                    "language": term.lang,
                                                    "resourceinstanceid": tile.resourceinstance_id,
                                                    "provisional": True,
                                                },
                                            }
                                        )

        for (
            custom_search_class
        ) in EsMappingModifierFactory.get_es_mapping_modifier_classes():
            custom_search_class.add_search_terms(self, document, terms)

        return document, terms

    def delete(self, user={}, index=True, transaction_id=None):
        """
        Deletes a single resource and any related indexed data

        """

        # note that deferring index will require:
        # - that any resources related to the to-be-deleted resource get re-indexed
        # - that the index for the to-be-deleted resource gets deleted

        permit_deletion = False
        if user != {}:
            user_is_reviewer = user_is_resource_reviewer(user)
            if user_is_reviewer is False:
                tiles = list(models.TileModel.objects.filter(resourceinstance=self))
                resource_is_provisional = (
                    True
                    if sum([len(t.data) for t in tiles]) == 0
                    or [any(t.data.values()) for t in tiles][0] == False
                    else False
                )
                if resource_is_provisional is True:
                    creator_id = EditLog.objects.filter(
                        resourceinstanceid=self.pk, edittype="create"
                    ).values_list("userid")[0][0]
                    try:
                        creator_id = int(creator_id)
                    except ValueError:
                        pass
                    if creator_id == user.id:
                        permit_deletion = True
            else:
                permit_deletion = True
        else:
            permit_deletion = True

        if permit_deletion is True:
            for related_resource in models.ResourceXResource.objects.filter(
                Q(resourceinstanceidfrom=self.resourceinstanceid)
                | Q(resourceinstanceidto=self.resourceinstanceid)
            ):
                related_resource.delete(deletedResourceId=self.resourceinstanceid)

            if index:
                self.delete_index()

            try:
                self.save_edit(
                    edit_type="delete",
                    user=user,
                    note=self.displayname(),
                    transaction_id=transaction_id,
                )
            except:
                pass
            super(Resource, self).delete()

        return permit_deletion

    def delete_index(self, resourceinstanceid=None):
        """
        Deletes all references to a resource from all indexes

        Keyword Arguments:
        resourceinstanceid -- the resource instance id to delete from related indexes, if supplied will use this over self.resourceinstanceid
        """

        if resourceinstanceid is None:
            resourceinstanceid = self.resourceinstanceid
            instance = self
        else:
            instance = Resource(pk=resourceinstanceid)
            # ensure PK is UUID
            instance.clean_fields(
                exclude=[
                    "graph",
                    "graph_publication",
                    "resource_instance_lifecycle_state",
                ]
            )
        resourceinstanceid = str(resourceinstanceid)

        # delete any related terms
        query = Query(se)
        bool_query = Bool()
        bool_query.filter(Terms(field="resourceinstanceid", terms=[resourceinstanceid]))
        query.add_query(bool_query)
        query.delete(index=TERMS_INDEX)

        # reindex any related resources
        query = Query(se)
        bool_query = Bool()
        bool_query.filter(
            Nested(path="ids", query=Terms(field="ids.id", terms=[resourceinstanceid]))
        )
        query.add_query(bool_query)
        results = query.search(index=RESOURCES_INDEX)["hits"]["hits"]
        for result in results:
            try:
                res = Resource.objects.get(pk=result["_id"])
                res.load_tiles()
                res.index()
            except ObjectDoesNotExist:
                pass

        # delete resource index
        se.delete(index=RESOURCES_INDEX, id=resourceinstanceid)

        # delete resources from custom indexes
        for index in settings.ELASTICSEARCH_CUSTOM_INDEXES:
            es_index = import_class_from_string(index["module"])(index["name"])
            es_index.delete_resources(resources=instance)

    def validate(self, verbose=False, strict=False):
        """
        Keyword Arguments:
        verbose -- False(default) to only show the first error thrown in any tile, True to show all the errors in all the tiles
        strict -- False(default), True to use a more complete check on the datatype
            (eg: check for the existance of a referenced resoure on the resource-instance datatype)
        """

        from arches.app.models.tile import Tile, TileValidationError

        errors = []
        tiles = self.tiles
        if len(self.tiles) == 0:
            tiles = Tile.objects.filter(resourceinstance=self)

        for tile in tiles:
            try:
                tile.validate(raise_early=(not verbose), strict=strict)
            except TileValidationError as err:
                errors += (
                    err.message if isinstance(err.message, list) else [err.message]
                )
        return errors

    def get_related_resources(
        self,
        lang="en-US",
        limit=settings.RELATED_RESOURCES_EXPORT_LIMIT,
        start=0,
        page=0,
        user=None,
        resourceinstance_graphid=None,
        graphs=None,
        include_rr_count=True,
    ):
        """
        Returns an object that lists the related resources, the relationship types, and a reference to the current resource

        """

        # TODO This function is very similar to code in search results and the resource view. Needs to be centralized.
        def get_localized_descriptor(document, descriptor_type):
            language_codes = (get_language(), settings.LANGUAGE_CODE)
            descriptor = document["_source"][descriptor_type]
            result = descriptor[0] if len(descriptor) > 0 else {"value": _("Undefined")}
            for language_code in language_codes:
                for entry in descriptor:
                    if entry["language"] == language_code and entry["value"] != "":
                        return entry["value"]
            return result["value"]

        if not graphs:
            graphs = list(
                models.GraphModel.objects.all()
                .exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
                .exclude(isresource=False)
                .exclude(is_active=False)
                .exclude(source_identifier__isnull=False)
            )

        graph_lookup = {
            str(graph.graphid): {
                "name": graph.name,
                "iconclass": graph.iconclass,
                "fillColor": graph.color,
            }
            for graph in graphs
        }

        ret = {
            "resource_instance": self,
            "resource_relationships": [],
            "related_resources": [],
            "node_config_lookup": graph_lookup,
        }

        if page > 0:
            number_per_page = settings.RELATED_RESOURCES_PER_PAGE
            start = number_per_page * int(page - 1)
            limit = number_per_page * page

        def get_relations(
            resourceinstanceid,
            start,
            limit,
            resourceinstance_graphid=None,
        ):
            final_query = Q(resourceinstanceidfrom_id=resourceinstanceid) | Q(
                resourceinstanceidto_id=resourceinstanceid
            )

            if resourceinstance_graphid:
                to_graph_id_filter = Q(
                    resourceinstancefrom_graphid_id=str(self.graph_id)
                ) & Q(resourceinstanceto_graphid_id=resourceinstance_graphid)
                from_graph_id_filter = Q(
                    resourceinstancefrom_graphid_id=resourceinstance_graphid
                ) & Q(resourceinstanceto_graphid_id=str(self.graph_id))
                final_query = final_query & (to_graph_id_filter | from_graph_id_filter)

            return (
                {  # resourceinstance_graphid = "00000000-886a-374a-94a5-984f10715e3a"
                    "total": models.ResourceXResource.objects.filter(
                        final_query
                    ).count(),
                    "relations": models.ResourceXResource.objects.filter(final_query)[
                        start:limit
                    ],
                }
            )

        resource_relations = get_relations(
            resourceinstanceid=self.resourceinstanceid,
            start=start,
            limit=limit,
            resourceinstance_graphid=resourceinstance_graphid,
        )

        ret["total"] = {"value": resource_relations["total"]}
        instanceids = set()

        readable_graphids = set(
            permission_backend.get_resource_types_by_perm(
                user, ["models.read_nodegroup"]
            )
        )
        all_resource_ids = set()
        for relation in resource_relations["relations"]:
            all_resource_ids.add(str(relation.resourceinstanceidto_id))
            all_resource_ids.add(str(relation.resourceinstanceidfrom_id))
        exclusive_set, filtered_instances = get_filtered_instances(
            user, se, resources=list(all_resource_ids)
        )
        filtered_instances = filtered_instances if user is not None else []
        permitted_relation_dicts = []

        for relation in resource_relations["relations"]:
            relation = model_to_dict(relation)
            resourceid_to = relation["resourceinstanceidto"]
            resourceid_from = relation["resourceinstanceidfrom"]
            resourceinstanceto_graphid = relation["resourceinstanceto_graphid"]
            resourceinstancefrom_graphid = relation["resourceinstancefrom_graphid"]

            resourceid_to_permission = str(resourceid_to) not in filtered_instances
            resourceid_from_permission = str(resourceid_from) not in filtered_instances

            if exclusive_set:
                resourceid_to_permission = not (resourceid_to_permission)
                resourceid_from_permission = not (resourceid_from_permission)

            if (
                resourceid_to_permission
                and resourceid_from_permission
                and str(resourceinstanceto_graphid) in readable_graphids
                and str(resourceinstancefrom_graphid) in readable_graphids
            ):
                permitted_relation_dicts.append(relation)
            else:
                ret["total"]["value"] -= 1

        # Fetch pref labels for relationship types in bulk.
        relationship_types = {
            relation["relationshiptype"]
            for relation in permitted_relation_dicts
            if relation["relationshiptype"]
        }
        relationship_type_values = (
            models.Value.objects.filter(
                value__in=relationship_types,
            )
            .select_related("concept")
            .prefetch_related(
                Prefetch(
                    "concept__value_set",
                    # Begin with an order, so that if rank_label()
                    # produces ties, we still have a deterministic result.
                    queryset=models.Value.objects.order_by("pk"),
                ),
            )
        )
        preflabel_lookup = {
            str(rel_type.pk): (
                sorted(
                    rel_type.concept.value_set.all(),
                    key=lambda label: rank_label(
                        kind=label.valuetype_id,
                        source_lang=label.language_id,
                        target_lang=lang,
                    ),
                    reverse=True,
                )[0].value
                if rel_type.concept.value_set.all()
                else ""
            )
            for rel_type in relationship_type_values
        }

        for relation in permitted_relation_dicts:
            relation["relationshiptype_label"] = preflabel_lookup.get(
                relation["relationshiptype"], relation["relationshiptype"] or ""
            )

            ret["resource_relationships"].append(relation)
            instanceids.add(str(resourceid_to))
            instanceids.add(str(resourceid_from))

        if str(self.resourceinstanceid) in instanceids:
            instanceids.remove(str(self.resourceinstanceid))

        if len(instanceids) > 0:
            related_resources = se.search(index=RESOURCES_INDEX, id=list(instanceids))
            if related_resources:
                related_resource_ids = [
                    resource["_id"]
                    for resource in related_resources["docs"]
                    if resource["found"]
                ]
                count_query = (
                    models.ResourceInstance.objects.filter(pk__in=related_resource_ids)
                    .annotate(
                        total_relations=(
                            Count("resxres_resource_instance_ids_from", distinct=True)
                            + Count("resxres_resource_instance_ids_to", distinct=True)
                        )
                    )
                    .only("pk")
                )
                total_relations_by_resource_id = {
                    obj.pk: obj.total_relations for obj in count_query.iterator()
                }

                for resource in related_resources["docs"]:
                    if resource["found"]:
                        if include_rr_count:
                            resource["_source"]["total_relations"] = (
                                total_relations_by_resource_id[UUID(resource["_id"])]
                            )
                        for descriptor_type in ("displaydescription", "displayname"):
                            descriptor = get_localized_descriptor(
                                resource, descriptor_type
                            )
                            if descriptor:
                                resource["_source"][descriptor_type] = descriptor
                            else:
                                resource["_source"][descriptor_type] = _("Undefined")

                        ret["related_resources"].append(resource["_source"])

        return ret

    def copy(self):
        """
        Returns a copy of this resource instance including a copy of all tiles associated with this resource instance

        """
        # need this here to prevent a circular import error
        from arches.app.models.tile import Tile

        id_map = {}
        new_resource = Resource()
        new_resource.graph = self.graph

        if len(self.tiles) == 0:
            self.tiles = Tile.objects.filter(resourceinstance=self)

        for tile in self.tiles:
            new_tile = Tile()
            new_tile.data = tile.data
            new_tile.nodegroup = tile.nodegroup
            new_tile.parenttile = tile.parenttile
            new_tile.resourceinstance = new_resource
            new_tile.sortorder = tile.sortorder

            new_resource.tiles.append(new_tile)
            id_map[tile.pk] = new_tile

        for tile in new_resource.tiles:
            if tile.parenttile:
                tile.parenttile = id_map[tile.parenttile_id]

        with transaction.atomic():
            new_resource.save(context="copy")

        return new_resource

    def serialize(self, fields=None, exclude=None, **kwargs):
        """
        Serialize to a different form then used by the internal class structure

        used to append additional values (like parent ontology properties) that
        internal objects (like models.Nodes) don't support

        """

        ret = JSONSerializer().handle_model(self)
        ret["displayname"] = self.displayname()
        ret["tiles"] = self.tiles

        return JSONSerializer().serializeToPython(ret)

    def to_json(
        self,
        compact=True,
        hide_empty_nodes=False,
        user=None,
        perm=None,
        version=None,
        hide_hidden_nodes=False,
    ):
        """
        Returns resource represented as disambiguated JSON graph

        Keyword Arguments:
        compact -- type bool: hide superfluous node data
        hide_empty_nodes -- type bool: hide nodes without data
        """
        if version is None:
            return LabelBasedGraph.from_resource(
                resource=self,
                compact=compact,
                hide_empty_nodes=hide_empty_nodes,
                user=user,
                perm=perm,
                hide_hidden_nodes=hide_hidden_nodes,
            )
        elif version == "beta":
            return LabelBasedGraphV2.from_resource(
                resource=self,
                compact=compact,
                hide_empty_nodes=hide_empty_nodes,
                user=user,
                perm=perm,
                hide_hidden_nodes=hide_hidden_nodes,
            )

    @staticmethod
    def to_json__bulk(resources, compact=True, hide_empty_nodes=False, version=None):
        """
        Returns list of resources represented as disambiguated JSON graphs

        Keyword Arguments:
        resources -- list of Resource
        compact -- type bool: hide superfluous node data
        hide_empty_nodes -- type bool: hide nodes without data
        """

        if version is None:
            return LabelBasedGraph.from_resources(
                resources=resources, compact=compact, hide_empty_nodes=hide_empty_nodes
            )
        elif version == "beta":
            return LabelBasedGraphV2.from_resources(
                resources=resources, compact=compact, hide_empty_nodes=hide_empty_nodes
            )

    def get_node_values(self, node_name):
        """
        Take a node_name (string) as an argument and return a list of values.
        If an invalid node_name is used, or if multiple nodes with the same
        name are found, the method returns False.
        Current supported (tested) node types are: string, date, concept, geometry
        """

        nodes = models.Node.objects.filter(name=node_name, graph_id=self.graph_id)
        if len(nodes) > 1:
            raise MultipleNodesFoundException(node_name, nodes)

        if len(nodes) == 0:
            raise InvalidNodeNameException(node_name)

        tiles = self.tilemodel_set.filter(nodegroup_id=nodes[0].nodegroup_id)

        values = []
        for tile in tiles:
            for node_id, value in tile.data.items():
                if node_id == str(nodes[0].nodeid):
                    if type(value) is list:
                        for v in value:
                            values.append(parse_node_value(v))
                    else:
                        values.append(parse_node_value(value))

        return values

    def remove_resource_instance_permissions(self):
        groups = list(Group.objects.all())
        users = list(User.objects.all())
        for identity in groups + users:
            for perm in [
                "no_access_to_resourceinstance",
                "view_resourceinstance",
                "change_resourceinstance",
                "delete_resourceinstance",
            ]:
                remove_perm(perm, identity, self)
        self.index()

    def add_permission_to_all(self, permission):
        groups = list(Group.objects.all())
        users = [user for user in User.objects.all() if user.is_superuser is False]
        for identity in groups + users:
            assign_perm(permission, identity, self)
        self.index()

    def update_resource_instance_lifecycle_state(
        self, user, resource_instance_lifecycle_state
    ):
        if not user_is_resource_reviewer(user):
            raise PermissionDenied

        if (
            self.graph.resource_instance_lifecycle.pk
            != resource_instance_lifecycle_state.resource_instance_lifecycle.pk
        ):
            raise ValueError(
                _(
                    "The given ResourceInstanceLifecycleState is not part of the model's ResourceInstanceLifecycle."
                )
            )

        if (
            self.resource_instance_lifecycle_state.pk
            != resource_instance_lifecycle_state.pk
        ):
            current_resource_instance_lifecycle_state = (
                self.resource_instance_lifecycle_state
            )
            self.resource_instance_lifecycle_state = resource_instance_lifecycle_state

            self.save(
                user=user,
                current_resource_instance_lifecycle_state=current_resource_instance_lifecycle_state,
                should_update_resource_instance_lifecycle_state=True,
            )

        return self.resource_instance_lifecycle_state


def parse_node_value(value):
    if is_uuid(value):
        try:
            return models.Value.objects.get(pk=value).value
        except ObjectDoesNotExist:
            pass
    return value


def is_uuid(value_to_test):
    try:
        UUID(value_to_test)
        return True
    except Exception:
        return False
