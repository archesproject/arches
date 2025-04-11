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

import json
import logging
import uuid

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.contrib.auth.models import User, Group
from django.forms.models import model_to_dict
from django.http import HttpResponseNotFound
from django.http import Http404
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import View
from django.utils import translation

from arches.app.models import models
from arches.app.models.card import Card
from arches.app.models.graph import Graph
from arches.app.models.tile import Tile
from arches.app.models.resource import Resource, PublishedModelError
from arches.app.models.system_settings import settings
from arches.app.utils.activity_stream_jsonld import ActivityStreamCollection
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.decorators import group_required
from arches.app.utils.decorators import can_edit_resource_instance
from arches.app.utils.decorators import can_read_resource_instance
from arches.app.utils.i18n import LanguageSynchronizer, localize_complex_input
from arches.app.utils.pagination import get_paginator
from arches.app.utils.permission_backend import (
    get_default_settable_permissions,
    user_is_resource_editor,
    user_is_resource_reviewer,
    user_can_delete_resource,
)
from arches.app.utils.response import JSONResponse, JSONErrorResponse
from arches.app.utils.string_utils import str_to_bool
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.views.base import BaseManagerView, MapBaseManagerView
from arches.app.views.concept import Concept
from arches.app.datatypes.datatypes import DataTypeFactory

import arches.app.utils.permission_backend as apb

logger = logging.getLogger(__name__)


@method_decorator(can_edit_resource_instance, name="dispatch")
class ResourceListView(BaseManagerView):
    def get(self, request, graphid=None, resourceid=None):
        context = self.get_context_data(main_script="views/resource")

        context["nav"]["icon"] = "fa fa-bookmark"
        context["nav"]["title"] = _("Resource Manager")
        context["nav"]["login"] = True
        context["nav"]["help"] = {
            "title": _("Creating Resources"),
            "templates": ["resource-editor-landing-help"],
        }

        return render(request, "views/resource.htm", context)


def get_resource_relationship_types():
    resource_relationship_types = Concept().get_child_collections(
        "00000000-0000-0000-0000-000000000005"
    )
    default_relationshiptype_valueid = None
    for relationship_type in resource_relationship_types:
        if relationship_type[0] == "00000000-0000-0000-0000-000000000007":
            default_relationshiptype_valueid = relationship_type[2]
    relationship_type_values = {
        "values": [
            {"id": str(c[2]), "text": str(c[1])} for c in resource_relationship_types
        ],
        "default": str(default_relationshiptype_valueid),
    }
    return relationship_type_values


@method_decorator(group_required("Resource Editor"), name="dispatch")
class ResourceEditorView(MapBaseManagerView):
    action = None

    @method_decorator(can_edit_resource_instance, name="dispatch")
    def get(
        self,
        request,
        graphid=None,
        resourceid=None,
        view_template="views/resource/editor.htm",
        main_script="views/resource/editor",
        nav_menu=True,
    ):
        if self.action == "copy":
            return self.copy(request, resourceid)

        creator = None
        user_created_instance = None

        languages = models.Language.objects.all()

        def prepare_tiledata(tile, nodes):
            datatype_factory = DataTypeFactory()
            datatype_lookup = {
                str(node.nodeid): datatype_factory.get_instance(node.datatype)
                for node in nodes
            }
            for nodeid in tile.data.keys():
                datatype = datatype_lookup[nodeid]
                datatype.pre_structure_tile_data(tile, nodeid, languages=languages)

        def add_i18n_to_cardwidget_defaults(cardwidgets):
            serialized_cardwidgets = JSONSerializer().serializeToPython(cardwidgets)

            for cardwidget in serialized_cardwidgets:
                if cardwidget["widget_id"] in [
                    "10000000-0000-0000-0000-000000000005",
                    "10000000-0000-0000-0000-000000000001",
                ]:
                    try:
                        default_value = cardwidget["config"]["defaultValue"]
                    except KeyError:
                        default_value = None
                    if default_value is None:
                        existing_languages = []
                        cardwidget["config"]["defaultValue"] = {}
                    elif type(default_value) is str:
                        default_language = languages.get(code=settings.LANGUAGE_CODE)
                        cardwidget["config"]["defaultValue"] = {
                            settings.LANGUAGE_CODE: {
                                "value": default_value,
                                "direction": default_language.default_direction,
                            }
                        }
                        existing_languages = [settings.LANGUAGE_CODE]
                    else:
                        existing_languages = list(default_value.keys())
                    for language in languages:
                        if language.code not in existing_languages:
                            cardwidget["config"]["defaultValue"][language.code] = {
                                "value": "",
                                "direction": language.default_direction,
                            }
            return serialized_cardwidgets

        def add_i18n_to_widget_defaults(widgets):
            for widget in widgets:
                if widget.datatype == "string":
                    existing_languages = []
                    default_value = widget.defaultconfig["defaultValue"]
                    if default_value != "" and default_value is not None:
                        existing_languages = list(default_value.keys())
                        for language in languages:
                            if language.code not in existing_languages:
                                widget.defaultconfig["defaultValue"][language.code] = {
                                    "value": "",
                                    "direction": language.default_direction,
                                }
            return widgets

        if resourceid is None:
            resource_instance = None
            graph = models.GraphModel.objects.get(pk=graphid)
            resourceid = ""
        else:
            resource_instance = Resource.objects.get(pk=resourceid)
            graph = resource_instance.graph
            instance_creator = (
                resource_instance.get_instance_creator_and_edit_permissions(
                    request.user
                )
            )
            creator = instance_creator["creatorid"]
            user_created_instance = instance_creator[
                "user_can_edit_instance_permissions"
            ]

        ontologyclass = None
        nodegroups = []
        editable_nodegroups = []

        nodes = graph.node_set.all().select_related("nodegroup")
        for node in nodes:
            if node.istopnode and not ontologyclass:
                ontologyclass = node.ontologyclass

            if node.is_collector:
                added = False

                if request.user.has_perm("write_nodegroup", node.nodegroup):
                    editable_nodegroups.append(node.nodegroup)
                    nodegroups.append(node.nodegroup)
                    added = True

                if not added and request.user.has_perm(
                    "read_nodegroup", node.nodegroup
                ):
                    nodegroups.append(node.nodegroup)

        primary_descriptor_functions = models.FunctionXGraph.objects.filter(
            graph=graph
        ).filter(function__functiontype="primarydescriptors")
        primary_descriptor_function = JSONSerializer().serialize(
            primary_descriptor_functions[0]
            if len(primary_descriptor_functions) > 0
            else None
        )
        user_is_reviewer = user_is_resource_reviewer(request.user)
        is_system_settings = False
        if resource_instance is None:
            tiles = []
            displayname = _("New Resource")
        else:
            displayname = resource_instance.displayname()
            if displayname == "undefined":
                displayname = _("Unnamed Resource")
            if (
                str(resource_instance.graph_id)
                == settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID
            ):
                is_system_settings = True
                displayname = _("System Settings")

            tiles = resource_instance.tilemodel_set.order_by("sortorder").filter(
                nodegroup__in=nodegroups
            )
            provisionaltiles = []
            for tile in tiles:
                append_tile = True
                isfullyprovisional = False
                if tile.provisionaledits is not None:
                    if len(list(tile.provisionaledits.keys())) > 0:
                        if len(tile.data) == 0:
                            isfullyprovisional = True
                        if user_is_reviewer is False:
                            if str(request.user.id) in tile.provisionaledits:
                                tile.provisionaledits = {
                                    str(request.user.id): tile.provisionaledits[
                                        str(request.user.id)
                                    ]
                                }
                                tile.data = tile.provisionaledits[str(request.user.id)][
                                    "value"
                                ]
                            else:
                                if isfullyprovisional is True:
                                    # if the tile IS fully provisional and the current user is not the owner,
                                    # we don't send that tile back to the client.
                                    append_tile = False
                                else:
                                    # if the tile has authoritaive data and the current user is not the owner,
                                    # we don't send the provisional data of other users back to the client.
                                    tile.provisionaledits = None
                if append_tile is True:
                    provisionaltiles.append(tile)
            tiles = provisionaltiles
            for tile in tiles:
                prepare_tiledata(tile, nodes)

        serialized_graph = None
        if graph.publication:
            try:
                published_graph = graph.get_published_graph()
            except models.PublishedGraph.DoesNotExist:
                LanguageSynchronizer.synchronize_settings_with_db()
                published_graph = graph.get_published_graph()

            serialized_graph = published_graph.serialized_graph

        if serialized_graph:
            serialized_cards = serialized_graph["cards"]
            cardwidgets = [
                models.CardXNodeXWidget(**card_x_node_x_widget_dict)
                for card_x_node_x_widget_dict in serialized_graph["widgets"]
            ]
        else:
            cards = (
                graph.cardmodel_set.order_by("sortorder")
                .filter(nodegroup__in=nodegroups)
                .prefetch_related("cardxnodexwidget_set")
            )
            serialized_cards = JSONSerializer().serializeToPython(cards)
            cardwidgets = []
            for card in cards:
                cardwidgets += list(
                    card.cardxnodexwidget_set.order_by("sortorder").all()
                )

        updated_cardwidgets = add_i18n_to_cardwidget_defaults(cardwidgets)

        widgets = list(models.Widget.objects.all())
        updated_widgets = add_i18n_to_widget_defaults(widgets)

        card_components = models.CardComponent.objects.all()
        templates = models.ReportTemplate.objects.all()

        editable_nodegroup_ids = [
            str(nodegroup.pk) for nodegroup in editable_nodegroups
        ]
        for card in serialized_cards:
            card["is_writable"] = False
            if str(card["nodegroup_id"]) in editable_nodegroup_ids:
                card["is_writable"] = True

        context = self.get_context_data(
            main_script=main_script,
            resourceid=resourceid,
            displayname=displayname,
            graphid=graph.graphid,
            graphiconclass=graph.iconclass,
            graphname=graph.name,
            ontologyclass=ontologyclass,
            resource_graphs=(
                models.GraphModel.objects.exclude(
                    pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID
                )
                .exclude(isresource=False)
                .exclude(publication=None)
            ),
            relationship_types=get_resource_relationship_types(),
            widgets=updated_widgets,
            widgets_json=JSONSerializer().serialize(updated_widgets),
            card_components=card_components,
            card_components_json=JSONSerializer().serialize(card_components),
            tiles=JSONSerializer().serialize(tiles),
            cards=JSONSerializer().serialize(serialized_cards),
            primary_descriptor_function=primary_descriptor_function,
            applied_functions=JSONSerializer().serialize(
                models.FunctionXGraph.objects.filter(graph=graph)
            ),
            nodegroups=JSONSerializer().serialize(nodegroups),
            nodes=JSONSerializer().serialize(nodes.filter(nodegroup__in=nodegroups)),
            cardwidgets=JSONSerializer().serialize(updated_cardwidgets),
            datatypes_json=JSONSerializer().serialize(
                models.DDataType.objects.all(),
                exclude=["iconclass", "modulename", "classname"],
            ),
            map_markers=models.MapMarker.objects.all(),
            geocoding_providers=models.Geocoder.objects.all(),
            user_is_reviewer=json.dumps(user_is_reviewer),
            user_can_delete_resource=user_can_delete_resource(request.user, resourceid),
            creator=json.dumps(creator),
            user_created_instance=json.dumps(user_created_instance),
            report_templates=templates,
            templates_json=JSONSerializer().serialize(
                templates, sort_keys=False, exclude=["name", "description"]
            ),
            graph_json=JSONSerializer().serialize(graph),
            is_system_settings=is_system_settings,
        )

        context["nav"]["title"] = ""
        context["nav"]["menu"] = nav_menu

        if resourceid not in (None, ""):
            context["nav"]["report_view"] = True

        if resourceid == settings.RESOURCE_INSTANCE_ID:
            context["nav"]["help"] = {
                "title": _("Managing System Settings"),
                "templates": ["system-settings-help"],
            }
        else:
            context["nav"]["help"] = {
                "title": _("Using the Resource Editor"),
                "templates": ["resource-editor-help"],
            }

        return render(request, view_template, context)

    def delete(self, request, resourceid=None):
        delete_error = _("Unable to Delete Resource")
        delete_msg = _(
            "User does not have permissions to delete this instance because the instance or its data is restricted"
        )
        try:
            if resourceid is not None:
                if user_can_delete_resource(request.user, resourceid) is False:
                    return JSONErrorResponse(delete_error, delete_msg)
                ret = Resource.objects.get(pk=resourceid)
                try:
                    deleted = ret.delete(user=request.user)
                except PublishedModelError as e:
                    message = _(
                        "Unable to delete. Please verify the model is not currently published."
                    )
                    return JSONResponse(
                        {"status": "false", "message": [_(e.title), _(str(message))]},
                        status=500,
                    )
                except PermissionDenied:
                    return JSONErrorResponse(delete_error, delete_msg)
                if deleted is True:
                    return JSONResponse(ret)
                else:
                    return JSONErrorResponse(delete_error, delete_msg)
            return HttpResponseNotFound()
        except PermissionDenied:
            return JSONErrorResponse(delete_error, delete_msg)

    def copy(self, request, resourceid=None):
        resource_instance = Resource.objects.get(pk=resourceid)
        resource = resource_instance.copy()
        return JSONResponse({"resourceid": resource.resourceinstanceid})


@method_decorator(group_required("Resource Editor"), name="dispatch")
class ResourcePermissionDataView(View):
    perm_cache = {}
    action = None

    def get(self, request):
        resourceid = request.GET.get("instanceid", None)
        resource_instance = models.ResourceInstance.objects.get(pk=resourceid)
        result = self.get_instance_permissions(resource_instance)
        return JSONResponse(result)

    def post(self, request):
        result = None

        data = JSONDeserializer().deserialize(request.body)
        self.apply_permissions(data, request.user)
        if "instanceid" in data:
            resource = models.ResourceInstance.objects.get(pk=data["instanceid"])
            result = self.get_instance_permissions(resource)
        return JSONResponse(result)

    def delete(self, request):
        data = JSONDeserializer().deserialize(request.body)
        self.apply_permissions(data, request.user, revert=True)
        return JSONResponse(data)

    def get_perms(self, identity, type, obj, perms):
        if type == "user":
            identity_perms = apb.get_user_perms(identity, obj)
        else:
            identity_perms = apb.get_group_perms(identity, obj)
        res = []
        for perm in identity_perms:
            res += list(filter(lambda x: (x["codename"] == perm.codename), perms))
        return res

    def get_instance_permissions(self, resource_instance):
        permission_order = get_default_settable_permissions()
        resource_permissions = apb.get_perms_for_model(resource_instance)
        perms = json.loads(
            JSONSerializer().serialize(
                {
                    p.codename: p
                    for p in resource_permissions
                    if p.codename != "add_resourceinstance"
                }
            )
        )
        ordered_perms = []
        for p in permission_order:
            ordered_perms.append(perms[p])
        identities = [
            {
                "name": user.username,
                "id": user.id,
                "type": "user",
                "default_permissions": self.get_perms(
                    user, "user", resource_instance, ordered_perms
                ),
                "system_permissions": apb.get_default_permissions(
                    user, resource_instance
                ),
                "is_editor_or_reviewer": bool(
                    user_is_resource_editor(user) or user_is_resource_reviewer(user)
                ),
            }
            for user in User.objects.all()
        ]
        identities += [
            {
                "name": group.name,
                "id": group.id,
                "type": "group",
                "system_permissions": apb.get_default_permissions(
                    group, resource_instance
                ),
                "default_permissions": self.get_perms(
                    group, "group", resource_instance, ordered_perms
                ),
            }
            for group in Group.objects.all()
        ]
        result = {"identities": identities}
        result["permissions"] = ordered_perms
        result["limitedaccess"] = (
            len(apb.get_users_with_perms(resource_instance))
            + len(apb.get_groups_with_perms(resource_instance))
        ) > 1
        instance_creator = resource_instance.get_instance_creator_and_edit_permissions()
        result["creatorid"] = instance_creator["creatorid"]
        return result

    def apply_permissions(self, data, user, revert=False):
        for instance in data["selectedInstances"]:
            resource_instance = models.ResourceInstance.objects.get(
                pk=instance["resourceinstanceid"]
            )
            for identity in data["selectedIdentities"]:
                if identity["type"] == "group":
                    identityModel = Group.objects.get(pk=identity["id"])
                else:
                    identityModel = User.objects.get(pk=identity["id"])

                instance_creator = (
                    resource_instance.get_instance_creator_and_edit_permissions(user)
                )
                creator = instance_creator["creatorid"]
                user_can_modify_permissions = instance_creator[
                    "user_can_edit_instance_permissions"
                ]

                if user_can_modify_permissions:
                    # first remove all the current permissions
                    for perm in apb.get_perms(identityModel, resource_instance):
                        apb.remove_perm(perm, identityModel, resource_instance)

                    if not revert:
                        # then add the new permissions
                        no_access = any(
                            perm["codename"] == "no_access_to_resourceinstance"
                            for perm in identity["selectedPermissions"]
                        )
                        if no_access:
                            apb.assign_perm(
                                "no_access_to_resourceinstance",
                                identityModel,
                                resource_instance,
                            )
                        else:
                            for perm in identity["selectedPermissions"]:
                                result = apb.assign_perm(
                                    perm["codename"],
                                    identityModel,
                                    resource_instance,
                                )

            resource = Resource.objects.get(
                pk=str(resource_instance.resourceinstanceid)
            )
            resource.graph_id = resource_instance.graph_id
            resource.index()


@method_decorator(can_edit_resource_instance, name="dispatch")
class ResourceEditLogView(BaseManagerView):
    def getEditConceptValue(self, values):
        if values is not None:
            for k, v in values.items():
                try:
                    uuid.UUID(v)
                    v = models.Value.objects.get(pk=v).value
                    values[k] = v
                except Exception as e:
                    pass
                try:
                    display_values = []
                    for val in v:
                        uuid.UUID(val)
                        display_value = models.Value.objects.get(pk=val).value
                        display_values.append(display_value)
                    values[k] = display_values
                except Exception as e:
                    pass

    def get(
        self, request, resourceid=None, view_template="views/resource/edit-log.htm"
    ):
        transaction_id = request.GET.get("transactionid", None)
        if resourceid is None:
            if transaction_id:
                recent_edits = models.EditLog.objects.filter(
                    transactionid=transaction_id
                ).order_by("-timestamp")
            else:
                recent_edits = (
                    models.EditLog.objects.all()
                    .exclude(resourceclassid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
                    .order_by("-timestamp")[:100]
                )
            edited_ids = list({edit.resourceinstanceid for edit in recent_edits})
            resources = Resource.objects.filter(
                resourceinstanceid__in=edited_ids
            ).select_related("graph")
            edit_type_lookup = {
                "create": _("Resource Created"),
                "delete": _("Resource Deleted"),
                "tile delete": _("Tile Deleted"),
                "tile create": _("Tile Created"),
                "tile edit": _("Tile Updated"),
                "delete edit": _("Edit Deleted"),
                "bulk_create": _("Resource Created"),
            }
            deleted_instances = [
                e.resourceinstanceid for e in recent_edits if e.edittype == "delete"
            ]
            graph_name_lookup = {
                str(r.resourceinstanceid): r.graph.name for r in resources
            }
            for edit in recent_edits:
                edit.friendly_edittype = edit_type_lookup[edit.edittype]
                edit.resource_model_name = None
                edit.deleted = edit.resourceinstanceid in deleted_instances
                if edit.resourceinstanceid in graph_name_lookup:
                    edit.resource_model_name = graph_name_lookup[
                        edit.resourceinstanceid
                    ]
                edit.displayname = edit.note
                if edit.resource_model_name is None:
                    try:
                        edit.resource_model_name = models.GraphModel.objects.get(
                            pk=edit.resourceclassid
                        ).name
                    except Exception:
                        pass

            context = self.get_context_data(
                main_script="views/edit-history", recent_edits=recent_edits
            )

            context["nav"]["title"] = _("Recent Edits")

            return render(request, "views/edit-history.htm", context)
        else:
            resource_instance = models.ResourceInstance.objects.get(pk=resourceid)
            edits = models.EditLog.objects.filter(resourceinstanceid=resourceid)
            permitted_edits = []
            nodegroup_ids_from_edits = [
                uuid.UUID(nodegroupid) if nodegroupid else nodegroupid
                for nodegroupid in edits.values_list("nodegroupid", flat=True)
            ]
            nodegroups_for_edits = models.NodeGroup.objects.filter(
                pk__in=nodegroup_ids_from_edits
            ).in_bulk()
            for edit in edits:
                if edit.nodegroupid is not None:
                    edit_nodegroup = nodegroups_for_edits.get(
                        uuid.UUID(edit.nodegroupid)
                    )
                    if request.user.has_perm("read_nodegroup", edit_nodegroup):
                        if edit.newvalue is not None:
                            self.getEditConceptValue(edit.newvalue)
                        if edit.oldvalue is not None:
                            self.getEditConceptValue(edit.oldvalue)
                        permitted_edits.append(edit)
                else:
                    permitted_edits.append(edit)
            resource = Resource.objects.get(pk=resourceid)
            displayname = resource.displayname()
            cards = Card.objects.filter(
                nodegroup__parentnodegroup=None, graph=resource_instance.graph
            )
            graph_name = resource_instance.graph.name

            context = self.get_context_data(
                main_script="views/resource/edit-log",
                cards=JSONSerializer().serialize(cards),
                resource_type=graph_name,
                resource_description=resource.displaydescription(),
                iconclass=resource_instance.graph.iconclass,
                edits=JSONSerializer().serialize(
                    localize_complex_input(permitted_edits)
                ),
                resourceid=resourceid,
                displayname=(
                    _("Unnamed Resource") if displayname == "undefined" else displayname
                ),
            )

            context["nav"]["res_edit"] = True
            context["nav"]["icon"] = resource_instance.graph.iconclass
            context["nav"]["title"] = graph_name

            return render(request, view_template, context)


@method_decorator(can_edit_resource_instance, name="dispatch")
class ResourceActivityStreamPageView(BaseManagerView):
    def get(self, request, page=None):
        current_page = 1
        page_size = 100
        if hasattr(settings, "ACTIVITY_STREAM_PAGE_SIZE"):
            page_size = int(settings.ACTIVITY_STREAM_PAGE_SIZE)
        st = 0
        end = 100
        if page is not None:
            try:
                current_page = int(page)
                if current_page <= 0:
                    current_page = 1
                st = (current_page - 1) * page_size
                end = current_page * page_size
            except (ValueError, TypeError) as e:
                return HttpResponseBadRequest()

        totalItems = (
            models.EditLog.objects.all()
            .exclude(resourceclassid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
            .exclude(note="resource creation")
            .count()
        )
        edits = (
            models.EditLog.objects.all()
            .exclude(resourceclassid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
            .exclude(note="resource creation")
            .order_by("timestamp")[st:end]
        )

        # setting last to be same as first, changing later if there are more pages
        uris = {
            "root": request.build_absolute_uri(reverse("as_stream_collection")),
            "this": request.build_absolute_uri(
                reverse("as_stream_page", kwargs={"page": current_page})
            ),
            "first": request.build_absolute_uri(
                reverse("as_stream_page", kwargs={"page": 1})
            ),
            "last": request.build_absolute_uri(
                reverse("as_stream_page", kwargs={"page": 1})
            ),
        }

        if current_page > 1:
            uris["prev"] = request.build_absolute_uri(
                reverse("as_stream_page", kwargs={"page": current_page - 1})
            )
        if end < totalItems:
            uris["next"] = request.build_absolute_uri(
                reverse("as_stream_page", kwargs={"page": current_page + 1})
            )
        if totalItems > page_size:
            uris["last"] = (
                request.build_absolute_uri(
                    reverse(
                        "as_stream_page",
                        kwargs={"page": int(totalItems / page_size) + 1},
                    )
                ),
            )

        collection = ActivityStreamCollection(
            uris,
            totalItems,
            base_uri_for_arches=request.build_absolute_uri("/").rsplit("/", 1)[0],
        )

        collection_page = collection.generate_page(uris, edits)
        collection_page.startIndex((current_page - 1) * page_size)

        return JsonResponse(collection_page.to_obj())


@method_decorator(can_edit_resource_instance, name="dispatch")
class ResourceActivityStreamCollectionView(BaseManagerView):
    def get(self, request):
        page_size = 100
        if hasattr(settings, "ACTIVITY_STREAM_PAGE_SIZE"):
            page_size = int(settings.ACTIVITY_STREAM_PAGE_SIZE)

        totalItems = (
            models.EditLog.objects.all()
            .exclude(resourceclassid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
            .exclude(note="resource creation")
            .count()
        )

        uris = {
            "root": request.build_absolute_uri(reverse("as_stream_collection")),
            "first": request.build_absolute_uri(
                reverse("as_stream_page", kwargs={"page": 1})
            ),
            "last": request.build_absolute_uri(
                reverse("as_stream_page", kwargs={"page": 1})
            ),
        }

        if totalItems > page_size:
            uris["last"] = request.build_absolute_uri(
                reverse(
                    "as_stream_page", kwargs={"page": int(totalItems / page_size) + 1}
                )
            )

        collection = ActivityStreamCollection(
            uris,
            totalItems,
            base_uri_for_arches=request.build_absolute_uri("/").rsplit("/", 1),
        )

        return JsonResponse(collection.to_obj())


@method_decorator(can_edit_resource_instance, name="dispatch")
class ResourceData(View):
    def get(self, request, resourceid=None, formid=None):
        if formid is not None:
            form = Form(resourceid=resourceid, formid=formid, user=request.user)
            return JSONResponse(form)

        return HttpResponseNotFound()


@method_decorator(can_read_resource_instance, name="dispatch")
class ResourceTiles(View):
    def get(self, request, resourceid=None, include_display_values=True):
        datatype_factory = DataTypeFactory()
        nodeid = request.GET.get("nodeid", None)
        search_term = request.GET.get("term", None)
        permitted_tiles = []
        perm = "read_nodegroup"
        tiles = models.TileModel.objects.filter(resourceinstance_id=resourceid)
        if nodeid is not None:
            node = models.Node.objects.get(pk=nodeid)
            tiles = tiles.filter(nodegroup=node.nodegroup)

        for tile in tiles:
            if request.user.has_perm(perm, tile.nodegroup):
                tile = Tile.objects.get(pk=tile.tileid)
                tile.filter_by_perm(request.user, perm)
                tile_dict = model_to_dict(tile)
                if include_display_values:
                    tile_dict["display_values"] = []
                    for node in models.Node.objects.filter(nodegroup=tile.nodegroup):
                        if str(node.nodeid) in tile.data:
                            datatype = datatype_factory.get_instance(node.datatype)
                            display_value = datatype.get_display_value(tile, node)
                            if display_value is not None:
                                if (
                                    search_term is not None
                                    and search_term in display_value
                                ):
                                    tile_dict["display_values"].append(
                                        {
                                            "value": display_value,
                                            "label": node.name,
                                            "nodeid": node.nodeid,
                                        }
                                    )
                                elif search_term is None:
                                    tile_dict["display_values"].append(
                                        {
                                            "value": display_value,
                                            "label": node.name,
                                            "nodeid": node.nodeid,
                                        }
                                    )

                if search_term is None:
                    permitted_tiles.append(tile_dict)
                elif len(tile_dict["display_values"]) > 0:
                    permitted_tiles.append(tile_dict)
        return JSONResponse({"tiles": permitted_tiles})


@method_decorator(can_read_resource_instance, name="dispatch")
class ResourceCards(View):
    def get(self, request, resourceid=None):
        cards = []
        if resourceid is not None:
            graph = models.GraphModel.objects.get(graphid=resourceid)
            cards = [
                Card.objects.get(pk=card.cardid)
                for card in models.CardModel.objects.filter(graph=graph)
            ]
        return JSONResponse({"success": True, "cards": cards})


class ResourceDescriptors(View):
    def get_localized_descriptor(self, document, descriptor_type):
        language_codes = (translation.get_language(), settings.LANGUAGE_CODE)
        descriptor = document["_source"][descriptor_type]
        result = descriptor[0] if len(descriptor) > 0 else {"value": _("Undefined")}
        for language_code in language_codes:
            for entry in descriptor:
                if entry["language"] == language_code and entry["value"] != "":
                    return entry["value"]
        return result["value"]

    def get(self, request, resourceid=None):
        if (
            Resource.objects.filter(pk=resourceid)
            .exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_ID)
            .exists()
        ):
            try:
                resource = Resource.objects.get(pk=resourceid)
                se = SearchEngineFactory().create()
                document = se.search(index=RESOURCES_INDEX, id=resourceid)
                return JSONResponse(
                    {
                        "graphid": document["_source"]["graph_id"],
                        "graph_name": resource.graph.name,
                        "displaydescription": self.get_localized_descriptor(
                            document, "displaydescription"
                        ),
                        "map_popup": self.get_localized_descriptor(
                            document, "map_popup"
                        ),
                        "displayname": self.get_localized_descriptor(
                            document, "displayname"
                        ),
                        "geometries": document["_source"]["geometries"],
                        "permissions": document["_source"]["permissions"],
                        "userid": request.user.id,
                    }
                )
            except Exception as e:
                logger.exception(_("Failed to fetch resource instance descriptors"))

        return HttpResponseNotFound()


@method_decorator(can_read_resource_instance, name="dispatch")
class ResourceReportView(MapBaseManagerView):
    def get(self, request, resourceid=None):
        try:
            resource = Resource.objects.only("graph_id").get(pk=resourceid)
        except Resource.DoesNotExist:
            raise Http404(_("Resource does not exist"))
        graph = Graph.objects.get(graphid=resource.graph_id)

        try:
            map_markers = models.MapMarker.objects.all()
            geocoding_providers = models.Geocoder.objects.all()
        except AttributeError:
            raise Http404(
                _("No active report template is available for this resource.")
            )

        context = self.get_context_data(
            main_script="views/resource/report",
            resourceid=resourceid,
            report_templates=models.ReportTemplate.objects.all(),
            card_components=models.CardComponent.objects.all(),
            widgets=models.Widget.objects.all(),
            map_markers=map_markers,
            geocoding_providers=geocoding_providers,
        )

        if graph.iconclass:
            context["nav"]["icon"] = graph.iconclass
        context["nav"]["title"] = graph.name
        context["nav"]["res_edit"] = True
        context["nav"]["print"] = True

        return render(request, "views/resource/report.htm", context)


@method_decorator(can_read_resource_instance, name="dispatch")
class RelatedResourcesView(BaseManagerView):
    action = None
    graphs = (
        models.GraphModel.objects.all()
        .exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
        .exclude(isresource=False)
        .exclude(publication=None)
    )

    def paginate_related_resources(self, related_resources, page, request):
        total = related_resources["total"]["value"]
        paginator, pages = get_paginator(
            request, related_resources, total, page, settings.RELATED_RESOURCES_PER_PAGE
        )
        page = paginator.page(page)

        def parse_relationshiptype_label(relationship):
            if relationship["relationshiptype_label"].startswith("http"):
                relationship["relationshiptype_label"] = relationship[
                    "relationshiptype_label"
                ].rsplit("/")[-1]
            return relationship

        related_resources["resource_relationships"] = [
            parse_relationshiptype_label(r)
            for r in related_resources["resource_relationships"]
        ]

        ret = {}
        ret["related_resources"] = related_resources
        ret["paginator"] = {}
        ret["paginator"]["current_page"] = page.number
        ret["paginator"]["has_next"] = page.has_next()
        ret["paginator"]["has_previous"] = page.has_previous()
        ret["paginator"]["has_other_pages"] = page.has_other_pages()
        ret["paginator"]["next_page_number"] = (
            page.next_page_number() if page.has_next() else None
        )
        ret["paginator"]["previous_page_number"] = (
            page.previous_page_number() if page.has_previous() else None
        )
        ret["paginator"]["start_index"] = page.start_index()
        ret["paginator"]["end_index"] = page.end_index()
        ret["paginator"]["pages"] = pages

        return ret

    def get(self, request, resourceid=None, include_rr_count=True):
        ret = {}

        if self.action == "get_candidates":
            resourceid = request.GET.get("resourceids", "")
            resources = Resource.objects.filter(
                resourceinstanceid=resourceid
            ).prefetch_related("graph__functions")
            ret = []

            for resource in resources:
                res = JSONSerializer().serializeToPython(resource)
                res["ontologyclass"] = resource.get_root_ontology()
                ret.append(res)

        elif self.action == "get_relatable_resources":
            graphid = request.GET.get("graphid", None)
            nodes = (
                models.Node.objects.filter(graph=graphid)
                .exclude(istopnode=False)[0]
                .get_relatable_resources()
            )
            ret = {str(node.graph_id) for node in nodes}

        else:
            lang = request.GET.get("lang", request.LANGUAGE_CODE)
            resourceinstance_graphid = request.GET.get("resourceinstance_graphid")
            paginate = str_to_bool(
                request.GET.get("paginate", "true")
            )  # default to true
            resource = Resource.objects.get(pk=resourceid)

            if paginate:
                page = (
                    1
                    if request.GET.get("page") == ""
                    else int(request.GET.get("page", 1))
                )
                start = int(request.GET.get("start", 0))

                related_resources = resource.get_related_resources(
                    lang=lang,
                    start=start,
                    page=page,
                    user=request.user,
                    resourceinstance_graphid=resourceinstance_graphid,
                    graphs=self.graphs,
                    include_rr_count=include_rr_count,
                )

                ret = self.paginate_related_resources(
                    related_resources=related_resources, page=page, request=request
                )
            else:
                ret = resource.get_related_resources(
                    lang=lang,
                    user=request.user,
                    resourceinstance_graphid=resourceinstance_graphid,
                    graphs=self.graphs,
                    include_rr_count=include_rr_count,
                )

        return JSONResponse(ret)

    def delete(self, request, resourceid=None):
        lang = request.GET.get("lang", request.LANGUAGE_CODE)
        se = SearchEngineFactory().create()
        req = dict(request.GET)
        ids_to_delete = req["resourcexids[]"]
        root_resourceinstanceid = req["root_resourceinstanceid"]
        for resourcexid in ids_to_delete:
            try:
                ret = models.ResourceXResource.objects.get(pk=resourcexid).delete()
            except ObjectDoesNotExist:
                logger.exception(_("Unable to delete. Relationship does not exist"))
        start = request.GET.get("start", 0)
        resource = Resource.objects.get(pk=root_resourceinstanceid[0])
        page = 1 if request.GET.get("page") == "" else int(request.GET.get("page", 1))
        related_resources = resource.get_related_resources(
            lang=lang, start=start, limit=1000, page=page, user=request.user
        )
        ret = []

        if related_resources is not None:
            ret = self.paginate_related_resources(related_resources, page, request)

        return JSONResponse(ret, indent=4)

    def post(self, request, resourceid=None):
        lang = request.GET.get("lang", request.LANGUAGE_CODE)
        se = SearchEngineFactory().create()
        res = dict(request.POST)
        relationshiptype = res["relationship_properties[relationshiptype]"][0]
        datefrom = res["relationship_properties[datestarted]"][0]
        dateto = res["relationship_properties[dateended]"][0]
        dateto = None if dateto == "" else dateto
        datefrom = None if datefrom == "" else datefrom
        notes = res["relationship_properties[notes]"][0]
        root_resourceinstanceid = res["root_resourceinstanceid"]
        instances_to_relate = []
        relationships_to_update = []
        if "instances_to_relate[]" in res:
            instances_to_relate = res["instances_to_relate[]"]
        if "relationship_ids[]" in res:
            relationships_to_update = res["relationship_ids[]"]

        def get_relatable_resources(graphid):
            """
            Takes the graphid of a resource, finds the graphs root node, and returns the relatable graphids
            """
            nodes = models.Node.objects.filter(graph_id=graphid)
            top_node = [node for node in nodes if node.istopnode == True][0]
            relatable_resources = [
                str(node.graph_id) for node in top_node.get_relatable_resources()
            ]
            return relatable_resources

        def confirm_relationship_permitted(to_id, from_id):
            resource_instance_to = models.ResourceInstance.objects.filter(
                resourceinstanceid=to_id
            )[0]
            resource_instance_from = models.ResourceInstance.objects.filter(
                resourceinstanceid=from_id
            )[0]
            relatable_to = get_relatable_resources(resource_instance_to.graph_id)
            relatable_from = get_relatable_resources(resource_instance_from.graph_id)
            relatable_to_is_valid = str(resource_instance_to.graph_id) in relatable_from
            relatable_from_is_valid = (
                str(resource_instance_from.graph_id) in relatable_to
            )
            return relatable_to_is_valid is True and relatable_from_is_valid is True

        for instanceid in instances_to_relate:
            permitted = confirm_relationship_permitted(
                instanceid, root_resourceinstanceid[0]
            )
            if permitted is True:
                rr = models.ResourceXResource(
                    resourceinstanceidfrom=Resource(root_resourceinstanceid[0]),
                    resourceinstanceidto=Resource(instanceid),
                    notes=notes,
                    relationshiptype=relationshiptype,
                    datestarted=datefrom,
                    dateended=dateto,
                )
                try:
                    rr.save()
                except PublishedModelError as e:
                    message = _(
                        "Unable to save. Please verify the model is not currently published."
                    )
                    return JSONResponse(
                        {"status": "false", "message": [_(e.title), _(str(message))]},
                        status=500,
                    )
            else:
                print("relationship not permitted")

        for relationshipid in relationships_to_update:
            rr = models.ResourceXResource.objects.get(pk=relationshipid)
            rr.notes = notes
            rr.relationshiptype = relationshiptype
            rr.datestarted = datefrom
            rr.dateended = dateto
            try:
                rr.save()
            except PublishedModelError as e:
                message = _(
                    "Unable to save. Please verify the model is not currently published."
                )
                return JSONResponse(
                    {"status": "false", "message": [_(e.title), _(str(message))]},
                    status=500,
                )

        start = request.GET.get("start", 0)
        resource = Resource.objects.get(pk=root_resourceinstanceid[0])
        page = 1 if request.GET.get("page") == "" else int(request.GET.get("page", 1))
        related_resources = resource.get_related_resources(
            lang=lang, start=start, limit=1000, page=page, user=request.user
        )
        ret = []

        if related_resources is not None:
            ret = self.paginate_related_resources(related_resources, page, request)

        return JSONResponse(ret, indent=4)
