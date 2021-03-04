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
import uuid

from distutils.util import strtobool

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.contrib.auth.models import User, Group, Permission
from django.db import transaction
from django.forms.models import model_to_dict
from django.http import HttpResponseNotFound
from django.http import HttpResponse
from django.http import Http404
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic import View
from arches import __version__
from arches.app.models import models
from arches.app.models.card import Card
from arches.app.models.graph import Graph
from arches.app.models.tile import Tile
from arches.app.models.resource import Resource, ModelInactiveError
from arches.app.models.system_settings import settings
from arches.app.utils.activity_stream_jsonld import ActivityStreamCollection
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.decorators import group_required
from arches.app.utils.decorators import can_edit_resource_instance
from arches.app.utils.decorators import can_delete_resource_instance
from arches.app.utils.decorators import can_read_resource_instance
from arches.app.utils.pagination import get_paginator
from arches.app.utils.permission_backend import (
    user_is_resource_editor,
    user_is_resource_reviewer,
    user_can_delete_resource,
    user_can_edit_resource,
    user_can_read_resource,
)
from arches.app.utils.response import JSONResponse, JSONErrorResponse
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Query, Terms
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.views.base import BaseManagerView, MapBaseManagerView
from arches.app.views.concept import Concept
from arches.app.datatypes.datatypes import DataTypeFactory
from elasticsearch import Elasticsearch
from guardian.shortcuts import (
    assign_perm,
    get_perms,
    remove_perm,
    get_group_perms,
    get_user_perms,
    get_groups_with_perms,
    get_users_with_perms,
    get_perms_for_model,
)
import logging

logger = logging.getLogger(__name__)


@method_decorator(can_edit_resource_instance, name="dispatch")
class ResourceListView(BaseManagerView):
    def get(self, request, graphid=None, resourceid=None):
        context = self.get_context_data(main_script="views/resource")

        context["nav"]["icon"] = "fa fa-bookmark"
        context["nav"]["title"] = _("Resource Manager")
        context["nav"]["login"] = True
        context["nav"]["help"] = {"title": _("Creating Resources"), "template": "resource-editor-landing-help"}

        return render(request, "views/resource.htm", context)


def get_resource_relationship_types():
    resource_relationship_types = Concept().get_child_collections("00000000-0000-0000-0000-000000000005")
    default_relationshiptype_valueid = None
    for relationship_type in resource_relationship_types:
        if relationship_type[0] == "00000000-0000-0000-0000-000000000007":
            default_relationshiptype_valueid = relationship_type[2]
    relationship_type_values = {
        "values": [{"id": str(c[2]), "text": str(c[1])} for c in resource_relationship_types],
        "default": str(default_relationshiptype_valueid),
    }
    return relationship_type_values


def get_instance_creator(resource_instance, user=None):
    creatorid = None
    can_edit = None
    if models.EditLog.objects.filter(resourceinstanceid=resource_instance.resourceinstanceid).filter(edittype="create").exists():
        creatorid = (
            models.EditLog.objects.filter(resourceinstanceid=resource_instance.resourceinstanceid).filter(edittype="create")[0].userid
        )
    if creatorid is None or creatorid == "":
        creatorid = settings.DEFAULT_RESOURCE_IMPORT_USER["userid"]
    if user:
        can_edit = user.id == int(creatorid) or user.is_superuser
    return {"creatorid": creatorid, "user_can_edit_instance_permissions": can_edit}


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
        if resourceid is None:
            resource_instance = None
            graph = models.GraphModel.objects.get(pk=graphid)
            resourceid = ""
        else:
            resource_instance = Resource.objects.get(pk=resourceid)
            graph = resource_instance.graph
            instance_creator = get_instance_creator(resource_instance, request.user)
            creator = instance_creator["creatorid"]
            user_created_instance = instance_creator["user_can_edit_instance_permissions"]
        nodes = graph.node_set.all()
        resource_graphs = (
            models.GraphModel.objects.exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
            .exclude(isresource=False)
            .exclude(isactive=False)
        )
        ontologyclass = [node for node in nodes if node.istopnode is True][0].ontologyclass or ""
        relationship_type_values = get_resource_relationship_types()
        nodegroups = []
        editable_nodegroups = []
        for node in nodes:
            if node.is_collector:
                added = False
                if request.user.has_perm("write_nodegroup", node.nodegroup):
                    editable_nodegroups.append(node.nodegroup)
                    nodegroups.append(node.nodegroup)
                    added = True
                if not added and request.user.has_perm("read_nodegroup", node.nodegroup):
                    nodegroups.append(node.nodegroup)

        nodes = nodes.filter(nodegroup__in=nodegroups)
        cards = graph.cardmodel_set.order_by("sortorder").filter(nodegroup__in=nodegroups).prefetch_related("cardxnodexwidget_set")
        cardwidgets = [
            widget for widgets in [card.cardxnodexwidget_set.order_by("sortorder").all() for card in cards] for widget in widgets
        ]
        widgets = models.Widget.objects.all()
        card_components = models.CardComponent.objects.all()
        applied_functions = JSONSerializer().serialize(models.FunctionXGraph.objects.filter(graph=graph))
        datatypes = models.DDataType.objects.all()
        user_is_reviewer = user_is_resource_reviewer(request.user)
        is_system_settings = False

        if resource_instance is None:
            tiles = []
            displayname = _("New Resource")
        else:
            displayname = resource_instance.displayname
            if displayname == "undefined":
                displayname = _("Unnamed Resource")
            if str(resource_instance.graph_id) == settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID:
                is_system_settings = True
                displayname = _("System Settings")

            tiles = resource_instance.tilemodel_set.order_by("sortorder").filter(nodegroup__in=nodegroups)
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
                                tile.provisionaledits = {str(request.user.id): tile.provisionaledits[str(request.user.id)]}
                                tile.data = tile.provisionaledits[str(request.user.id)]["value"]
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
        map_layers = models.MapLayer.objects.all()
        map_markers = models.MapMarker.objects.all()
        map_sources = models.MapSource.objects.all()
        geocoding_providers = models.Geocoder.objects.all()
        templates = models.ReportTemplate.objects.all()

        cards = JSONSerializer().serializeToPython(cards)
        editable_nodegroup_ids = [str(nodegroup.pk) for nodegroup in editable_nodegroups]
        for card in cards:
            card["is_writable"] = False
            if str(card["nodegroup_id"]) in editable_nodegroup_ids:
                card["is_writable"] = True
        can_delete = user_can_delete_resource(request.user, resourceid)
        context = self.get_context_data(
            main_script=main_script,
            resourceid=resourceid,
            displayname=displayname,
            graphid=graph.graphid,
            graphiconclass=graph.iconclass,
            graphname=graph.name,
            ontologyclass=ontologyclass,
            resource_graphs=resource_graphs,
            relationship_types=relationship_type_values,
            widgets=widgets,
            widgets_json=JSONSerializer().serialize(widgets),
            card_components=card_components,
            card_components_json=JSONSerializer().serialize(card_components),
            tiles=JSONSerializer().serialize(tiles),
            cards=JSONSerializer().serialize(cards),
            applied_functions=applied_functions,
            nodegroups=JSONSerializer().serialize(nodegroups),
            nodes=JSONSerializer().serialize(nodes),
            cardwidgets=JSONSerializer().serialize(cardwidgets),
            datatypes_json=JSONSerializer().serialize(datatypes, exclude=["iconclass", "modulename", "classname"]),
            map_layers=map_layers,
            map_markers=map_markers,
            map_sources=map_sources,
            geocoding_providers=geocoding_providers,
            user_is_reviewer=json.dumps(user_is_reviewer),
            user_can_delete_resource=can_delete,
            creator=json.dumps(creator),
            user_created_instance=json.dumps(user_created_instance),
            report_templates=templates,
            templates_json=JSONSerializer().serialize(templates, sort_keys=False, exclude=["name", "description"]),
            graph_json=JSONSerializer().serialize(graph),
            is_system_settings=is_system_settings,
        )

        context["nav"]["title"] = ""
        context["nav"]["menu"] = nav_menu
        if resourceid == settings.RESOURCE_INSTANCE_ID:
            context["nav"]["help"] = {"title": _("Managing System Settings"), "template": "system-settings-help"}
        else:
            context["nav"]["help"] = {"title": _("Using the Resource Editor"), "template": "resource-editor-help"}

        return render(request, view_template, context)

    def delete(self, request, resourceid=None):
        delete_error = _("Unable to Delete Resource")
        delete_msg = _("User does not have permissions to delete this instance because the instance or its data is restricted")
        try:
            if resourceid is not None:
                if user_can_delete_resource(request.user, resourceid) is False:
                    return JSONErrorResponse(delete_error, delete_msg)
                ret = Resource.objects.get(pk=resourceid)
                try:
                    deleted = ret.delete(user=request.user)
                except ModelInactiveError as e:
                    message = _("Unable to delete. Please verify the model status is active")
                    return JSONResponse({"status": "false", "message": [_(e.title), _(str(message))]}, status=500)
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
        return JSONResponse(resource_instance.copy())


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
        resourceid = request.POST.get("instanceid", None)
        action = request.POST.get("action", None)
        graphid = request.POST.get("graphid", None)
        result = None
        if action == "restrict":
            result = self.make_instance_private(resourceid, graphid)
        elif action == "open":
            result = self.make_instance_public(resourceid, graphid)
        else:
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
            identity_perms = get_user_perms(identity, obj)
        else:
            identity_perms = get_group_perms(identity, obj)
        res = []
        for perm in identity_perms:
            res += list(filter(lambda x: (x["codename"] == perm), perms))
        return res

    def get_instance_permissions(self, resource_instance):
        permission_order = ["view_resourceinstance", "change_resourceinstance", "delete_resourceinstance", "no_access_to_resourceinstance"]
        perms = json.loads(
            JSONSerializer().serialize(
                {p.codename: p for p in get_perms_for_model(resource_instance) if p.codename != "add_resourceinstance"}
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
                "default_permissions": self.get_perms(user, "user", resource_instance, ordered_perms),
                "is_editor_or_reviewer": bool(user_is_resource_editor(user) or user_is_resource_reviewer(user)),
            }
            for user in User.objects.all()
        ]
        identities += [
            {
                "name": group.name,
                "id": group.id,
                "type": "group",
                "default_permissions": self.get_perms(group, "group", resource_instance, ordered_perms),
            }
            for group in Group.objects.all()
        ]
        result = {"identities": identities}
        result["permissions"] = ordered_perms
        result["limitedaccess"] = (len(get_users_with_perms(resource_instance)) + len(get_groups_with_perms(resource_instance))) > 1
        instance_creator = get_instance_creator(resource_instance)
        result["creatorid"] = instance_creator["creatorid"]
        return result

    def make_instance_private(self, resourceinstanceid, graphid=None):
        resource = Resource(resourceinstanceid)
        resource.graph_id = graphid if graphid else str(models.ResourceInstance.objects.get(pk=resourceinstanceid).graph_id)
        resource.add_permission_to_all("no_access_to_resourceinstance")
        instance_creator = get_instance_creator(resource)
        user = User.objects.get(pk=instance_creator["creatorid"])
        assign_perm("view_resourceinstance", user, resource)
        assign_perm("change_resourceinstance", user, resource)
        assign_perm("delete_resourceinstance", user, resource)
        remove_perm("no_access_to_resourceinstance", user, resource)
        return self.get_instance_permissions(resource)

    def make_instance_public(self, resourceinstanceid, graphid=None):
        resource = Resource(resourceinstanceid)
        resource.graph_id = graphid if graphid else str(models.ResourceInstance.objects.get(pk=resourceinstanceid).graph_id)
        resource.remove_resource_instance_permissions()
        return self.get_instance_permissions(resource)

    def apply_permissions(self, data, user, revert=False):
        with transaction.atomic():
            for instance in data["selectedInstances"]:
                resource_instance = models.ResourceInstance.objects.get(pk=instance["resourceinstanceid"])
                for identity in data["selectedIdentities"]:
                    if identity["type"] == "group":
                        identityModel = Group.objects.get(pk=identity["id"])
                    else:
                        identityModel = User.objects.get(pk=identity["id"])

                    instance_creator = get_instance_creator(resource_instance, user)
                    creator = instance_creator["creatorid"]
                    user_can_modify_permissions = instance_creator["user_can_edit_instance_permissions"]

                    if user_can_modify_permissions:
                        # first remove all the current permissions
                        for perm in get_perms(identityModel, resource_instance):
                            remove_perm(perm, identityModel, resource_instance)

                        if not revert:
                            # then add the new permissions
                            no_access = any(perm["codename"] == "no_access_to_resourceinstance" for perm in identity["selectedPermissions"])
                            if no_access:
                                assign_perm("no_access_to_resourceinstance", identityModel, resource_instance)
                            else:
                                for perm in identity["selectedPermissions"]:
                                    assign_perm(perm["codename"], identityModel, resource_instance)

                resource = Resource(str(resource_instance.resourceinstanceid))
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

    def get(self, request, resourceid=None, view_template="views/resource/edit-log.htm"):
        if resourceid is None:
            recent_edits = (
                models.EditLog.objects.all()
                .exclude(resourceclassid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
                .order_by("-timestamp")[:100]
            )
            edited_ids = list({edit.resourceinstanceid for edit in recent_edits})
            resources = Resource.objects.filter(resourceinstanceid__in=edited_ids)
            edit_type_lookup = {
                "create": _("Resource Created"),
                "delete": _("Resource Deleted"),
                "tile delete": _("Tile Deleted"),
                "tile create": _("Tile Created"),
                "tile edit": _("Tile Updated"),
                "delete edit": _("Edit Deleted"),
                "bulk_create": _("Resource Created"),
            }
            deleted_instances = [e.resourceinstanceid for e in recent_edits if e.edittype == "delete"]
            graph_name_lookup = {str(r.resourceinstanceid): r.graph.name for r in resources}
            for edit in recent_edits:
                edit.friendly_edittype = edit_type_lookup[edit.edittype]
                edit.resource_model_name = None
                edit.deleted = edit.resourceinstanceid in deleted_instances
                if edit.resourceinstanceid in graph_name_lookup:
                    edit.resource_model_name = graph_name_lookup[edit.resourceinstanceid]
                edit.displayname = edit.note
                if edit.resource_model_name is None:
                    try:
                        edit.resource_model_name = models.GraphModel.objects.get(pk=edit.resourceclassid).name
                    except Exception:
                        pass

            context = self.get_context_data(main_script="views/edit-history", recent_edits=recent_edits)

            context["nav"]["title"] = _("Recent Edits")

            return render(request, "views/edit-history.htm", context)
        else:
            resource_instance = models.ResourceInstance.objects.get(pk=resourceid)
            edits = models.EditLog.objects.filter(resourceinstanceid=resourceid)
            permitted_edits = []
            for edit in edits:
                if edit.nodegroupid is not None:
                    nodegroup = models.NodeGroup.objects.get(pk=edit.nodegroupid)
                    if request.user.has_perm("read_nodegroup", edit.nodegroupid):
                        if edit.newvalue is not None:
                            self.getEditConceptValue(edit.newvalue)
                        if edit.oldvalue is not None:
                            self.getEditConceptValue(edit.oldvalue)
                        permitted_edits.append(edit)
                else:
                    permitted_edits.append(edit)

            resource = Resource.objects.get(pk=resourceid)
            displayname = resource.displayname
            displaydescription = resource.displaydescription
            cards = Card.objects.filter(nodegroup__parentnodegroup=None, graph=resource_instance.graph)
            graph_name = resource_instance.graph.name
            if displayname == "undefined":
                displayname = _("Unnamed Resource")

            context = self.get_context_data(
                main_script="views/resource/edit-log",
                cards=JSONSerializer().serialize(cards),
                resource_type=graph_name,
                resource_description=displaydescription,
                iconclass=resource_instance.graph.iconclass,
                edits=JSONSerializer().serialize(permitted_edits),
                resourceid=resourceid,
                displayname=displayname,
            )

            context["nav"]["res_edit"] = True
            context["nav"]["icon"] = resource_instance.graph.iconclass
            context["nav"]["title"] = graph_name

            return render(request, view_template, context)

        return HttpResponseNotFound()


@method_decorator(can_edit_resource_instance, name="dispatch")
class ResourceActivityStreamPageView(BaseManagerView):
    def get(self, request, page=None):
        current_page = 1
        page_size = 100
        if hasattr(settings, "ACTIVITY_STREAM_PAGE_SIZE"):
            page_size = int(setting.ACTIVITY_STREAM_PAGE_SIZE)
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

        totalItems = models.EditLog.objects.all().exclude(resourceclassid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID).count()

        edits = (
            models.EditLog.objects.all().exclude(resourceclassid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID).order_by("timestamp")[st:end]
        )

        # setting last to be same as first, changing later if there are more pages
        uris = {
            "root": request.build_absolute_uri(reverse("as_stream_collection")),
            "this": request.build_absolute_uri(reverse("as_stream_page", kwargs={"page": current_page})),
            "first": request.build_absolute_uri(reverse("as_stream_page", kwargs={"page": 1})),
            "last": request.build_absolute_uri(reverse("as_stream_page", kwargs={"page": 1})),
        }

        if current_page > 1:
            uris["prev"] = request.build_absolute_uri(reverse("as_stream_page", kwargs={"page": current_page - 1}))
        if end < totalItems:
            uris["next"] = request.build_absolute_uri(reverse("as_stream_page", kwargs={"page": current_page + 1}))
        if totalItems > page_size:
            uris["last"] = (request.build_absolute_uri(reverse("as_stream_page", kwargs={"page": int(totalItems / page_size) + 1})),)

        collection = ActivityStreamCollection(uris, totalItems, base_uri_for_arches=request.build_absolute_uri("/").rsplit("/", 1)[0])

        collection_page = collection.generate_page(uris, edits)
        collection_page.startIndex((current_page - 1) * page_size)

        return JsonResponse(collection_page.to_obj())


@method_decorator(can_edit_resource_instance, name="dispatch")
class ResourceActivityStreamCollectionView(BaseManagerView):
    def get(self, request):
        page_size = 100
        if hasattr(settings, "ACTIVITY_STREAM_PAGE_SIZE"):
            page_size = int(setting.ACTIVITY_STREAM_PAGE_SIZE)

        totalItems = models.EditLog.objects.all().exclude(resourceclassid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID).count()

        uris = {
            "root": request.build_absolute_uri(reverse("as_stream_collection")),
            "first": request.build_absolute_uri(reverse("as_stream_page", kwargs={"page": 1})),
            "last": request.build_absolute_uri(reverse("as_stream_page", kwargs={"page": 1})),
        }

        if totalItems > page_size:
            uris["last"] = request.build_absolute_uri(reverse("as_stream_page", kwargs={"page": int(totalItems / page_size) + 1}))

        collection = ActivityStreamCollection(uris, totalItems, base_uri_for_arches=request.build_absolute_uri("/").rsplit("/", 1))

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
                                if search_term is not None and search_term in display_value:
                                    tile_dict["display_values"].append({"value": display_value, "label": node.name, "nodeid": node.nodeid})
                                elif search_term is None:
                                    tile_dict["display_values"].append({"value": display_value, "label": node.name, "nodeid": node.nodeid})

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
            cards = [Card.objects.get(pk=card.cardid) for card in models.CardModel.objects.filter(graph=graph)]
        return JSONResponse({"success": True, "cards": cards})


class ResourceDescriptors(View):
    def get(self, request, resourceid=None):
        if Resource.objects.filter(pk=resourceid).exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_ID).exists():
            try:
                resource = Resource.objects.get(pk=resourceid)
                se = SearchEngineFactory().create()
                document = se.search(index=RESOURCES_INDEX, id=resourceid)
                return JSONResponse(
                    {
                        "graphid": document["_source"]["graph_id"],
                        "graph_name": resource.graph.name,
                        "displaydescription": document["_source"]["displaydescription"],
                        "map_popup": document["_source"]["map_popup"],
                        "displayname": document["_source"]["displayname"],
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
    def _generate_related_resources_summary(self, related_resources, resource_relationships, resource_models):
        related_resource_summary = [
            {"graphid": str(resource_model.graphid), "name": resource_model.name, "resources": []} for resource_model in resource_models
        ]

        resource_relationship_types = {
            resource_relationship_type["id"]: resource_relationship_type["text"]
            for resource_relationship_type in get_resource_relationship_types()["values"]
        }

        for related_resource in related_resources:
            for summary in related_resource_summary:
                if related_resource["graph_id"] == summary["graphid"]:
                    relationship_summary = []
                    for resource_relationship in resource_relationships:
                        if related_resource["resourceinstanceid"] == resource_relationship["resourceinstanceidto"]:
                            rr_type = (
                                resource_relationship_types[resource_relationship["relationshiptype"]]
                                if resource_relationship["relationshiptype"] in resource_relationship_types
                                else resource_relationship["relationshiptype"]
                            )
                            relationship_summary.append(rr_type)
                        elif related_resource["resourceinstanceid"] == resource_relationship["resourceinstanceidfrom"]:
                            rr_type = (
                                resource_relationship_types[resource_relationship["inverserelationshiptype"]]
                                if resource_relationship["inverserelationshiptype"] in resource_relationship_types
                                else resource_relationship["inverserelationshiptype"]
                            )
                            relationship_summary.append(rr_type)

                    summary["resources"].append(
                        {
                            "instance_id": related_resource["resourceinstanceid"],
                            "displayname": related_resource["displayname"],
                            "relationships": relationship_summary,
                        }
                    )

        return related_resource_summary

    def get(self, request, resourceid=None):
        resource = Resource.objects.get(pk=resourceid)

        resource_models = (
            models.GraphModel.objects.filter(isresource=True).exclude(isactive=False).exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
        )

        if strtobool(request.GET.get("json", "false")):
            get_params = request.GET.copy()
            get_params.update({"paginate": "false"})
            request.GET = get_params

            related_resources_response = RelatedResourcesView().get(request, resourceid)
            related_resources = json.loads(related_resources_response.content)

            related_resources_summary = self._generate_related_resources_summary(
                related_resources=related_resources["related_resources"],
                resource_relationships=related_resources["resource_relationships"],
                resource_models=resource_models,
            )
        else:
            related_resources_summary = {}

            for resource_model in resource_models:
                get_params = request.GET.copy()
                get_params.update({"resourceinstance_graphid": str(resource_model.graphid)})
                request.GET = get_params

                related_resources_response = RelatedResourcesView().get(request, resourceid).content
                related_resources_summary[str(resource_model.pk)] = json.loads(related_resources_response)

        permitted_tiles = []
        perm = "read_nodegroup"

        for tile in Tile.objects.filter(resourceinstance=resource).order_by("sortorder"):
            if request.user.has_perm(perm, tile.nodegroup):
                tile.filter_by_perm(request.user, perm)
                permitted_tiles.append(tile)

        if strtobool(request.GET.get("json", "false")) and strtobool(request.GET.get("exclude_graph", "false")):
            return JSONResponse(
                {
                    "tiles": permitted_tiles,
                    "related_resources": related_resources_summary,
                    "displayname": resource.displayname,
                    "resourceid": resourceid,
                }
            )

        datatypes = models.DDataType.objects.all()
        graph = Graph.objects.get(graphid=resource.graph_id)

        permitted_cards = []

        for card in Card.objects.filter(graph_id=resource.graph_id).order_by("sortorder"):
            if request.user.has_perm(perm, card.nodegroup):
                card.filter_by_perm(request.user, perm)
                permitted_cards.append(card)

        cardwidgets = [
            widget for widgets in [card.cardxnodexwidget_set.order_by("sortorder").all() for card in permitted_cards] for widget in widgets
        ]

        if strtobool(request.GET.get("json", "false")) and not strtobool(request.GET.get("exclude_graph", "false")):
            return JSONResponse(
                {
                    "datatypes": datatypes,
                    "cards": permitted_cards,
                    "tiles": permitted_tiles,
                    "graph": graph,
                    "related_resources": related_resources_summary,
                    "displayname": resource.displayname,
                    "resourceid": resourceid,
                    "cardwidgets": cardwidgets,
                }
            )

        widgets = models.Widget.objects.all()
        templates = models.ReportTemplate.objects.all()
        card_components = models.CardComponent.objects.all()

        try:
            map_layers = models.MapLayer.objects.all()
            map_markers = models.MapMarker.objects.all()
            map_sources = models.MapSource.objects.all()
            geocoding_providers = models.Geocoder.objects.all()
        except AttributeError:
            raise Http404(_("No active report template is available for this resource."))

        context = self.get_context_data(
            main_script="views/resource/report",
            report_templates=templates,
            templates_json=JSONSerializer().serialize(templates, sort_keys=False, exclude=["name", "description"]),
            card_components=card_components,
            card_components_json=JSONSerializer().serialize(card_components),
            cardwidgets=JSONSerializer().serialize(cardwidgets),
            tiles=JSONSerializer().serialize(permitted_tiles, sort_keys=False),
            cards=JSONSerializer().serialize(
                permitted_cards,
                sort_keys=False,
                exclude=["is_editable", "description", "instructions", "helpenabled", "helptext", "helptitle", "ontologyproperty"],
            ),
            datatypes_json=JSONSerializer().serialize(
                datatypes, exclude=["modulename", "issearchable", "configcomponent", "configname", "iconclass"]
            ),
            geocoding_providers=geocoding_providers,
            related_resources=JSONSerializer().serialize(related_resources_summary, sort_keys=False),
            widgets=widgets,
            map_layers=map_layers,
            map_markers=map_markers,
            map_sources=map_sources,
            graph_id=graph.graphid,
            graph_name=graph.name,
            graph_json=JSONSerializer().serialize(
                graph,
                sort_keys=False,
                exclude=[
                    "functions",
                    "relatable_resource_model_ids",
                    "domain_connections",
                    "edges",
                    "is_editable",
                    "description",
                    "iconclass",
                    "subtitle",
                    "author",
                ],
            ),
            resourceid=resourceid,
            displayname=resource.displayname,
            version=__version__,
            hide_empty_nodes=settings.HIDE_EMPTY_NODES_IN_REPORT,
        )

        if graph.iconclass:
            context["nav"]["icon"] = graph.iconclass
        context["nav"]["title"] = graph.name
        context["nav"]["res_edit"] = True
        context["nav"]["print"] = True
        context["nav"]["print"] = True

        return render(request, "views/resource/report.htm", context)


@method_decorator(can_read_resource_instance, name="dispatch")
class RelatedResourcesView(BaseManagerView):
    action = None

    def paginate_related_resources(self, related_resources, page, request):
        total = related_resources["total"]["value"]
        paginator, pages = get_paginator(request, related_resources, total, page, settings.RELATED_RESOURCES_PER_PAGE)
        page = paginator.page(page)

        def parse_relationshiptype_label(relationship):
            if relationship["relationshiptype_label"].startswith("http"):
                relationship["relationshiptype_label"] = relationship["relationshiptype_label"].rsplit("/")[-1]
            return relationship

        related_resources["resource_relationships"] = [parse_relationshiptype_label(r) for r in related_resources["resource_relationships"]]

        ret = {}
        ret["related_resources"] = related_resources
        ret["paginator"] = {}
        ret["paginator"]["current_page"] = page.number
        ret["paginator"]["has_next"] = page.has_next()
        ret["paginator"]["has_previous"] = page.has_previous()
        ret["paginator"]["has_other_pages"] = page.has_other_pages()
        ret["paginator"]["next_page_number"] = page.next_page_number() if page.has_next() else None
        ret["paginator"]["previous_page_number"] = page.previous_page_number() if page.has_previous() else None
        ret["paginator"]["start_index"] = page.start_index()
        ret["paginator"]["end_index"] = page.end_index()
        ret["paginator"]["pages"] = pages

        return ret

    def get(self, request, resourceid=None):
        ret = {}

        if self.action == "get_candidates":
            resourceid = request.GET.get("resourceids", "")
            resources = Resource.objects.filter(resourceinstanceid=resourceid)
            ret = []

            for resource in resources:
                res = JSONSerializer().serializeToPython(resource)
                res["ontologyclass"] = resource.get_root_ontology()
                ret.append(res)

        elif self.action == "get_relatable_resources":
            graphid = request.GET.get("graphid", None)
            nodes = models.Node.objects.filter(graph=graphid).exclude(istopnode=False)[0].get_relatable_resources()
            ret = {str(node.graph_id) for node in nodes}

        else:
            lang = request.GET.get("lang", settings.LANGUAGE_CODE)
            resourceinstance_graphid = request.GET.get("resourceinstance_graphid")
            paginate = strtobool(request.GET.get("paginate", "true"))  # default to true

            resource = Resource.objects.get(pk=resourceid)

            if paginate:
                page = 1 if request.GET.get("page") == "" else int(request.GET.get("page", 1))
                start = int(request.GET.get("start", 0))

                related_resources = resource.get_related_resources(
                    lang=lang, start=start, page=page, user=request.user, resourceinstance_graphid=resourceinstance_graphid,
                )

                ret = self.paginate_related_resources(related_resources=related_resources, page=page, request=request)
            else:
                ret = resource.get_related_resources(lang=lang, user=request.user, resourceinstance_graphid=resourceinstance_graphid)

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
        se.es.indices.refresh(index=se._add_prefix("resource_relations"))
        resource = Resource.objects.get(pk=root_resourceinstanceid[0])
        page = 1 if request.GET.get("page") == "" else int(request.GET.get("page", 1))
        related_resources = resource.get_related_resources(lang=lang, start=start, limit=1000, page=page, user=request.user)
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
            relatable_resources = [str(node.graph_id) for node in top_node.get_relatable_resources()]
            return relatable_resources

        def confirm_relationship_permitted(to_id, from_id):
            resource_instance_to = models.ResourceInstance.objects.filter(resourceinstanceid=to_id)[0]
            resource_instance_from = models.ResourceInstance.objects.filter(resourceinstanceid=from_id)[0]
            relatable_to = get_relatable_resources(resource_instance_to.graph_id)
            relatable_from = get_relatable_resources(resource_instance_from.graph_id)
            relatable_to_is_valid = str(resource_instance_to.graph_id) in relatable_from
            relatable_from_is_valid = str(resource_instance_from.graph_id) in relatable_to
            return relatable_to_is_valid is True and relatable_from_is_valid is True

        for instanceid in instances_to_relate:
            permitted = confirm_relationship_permitted(instanceid, root_resourceinstanceid[0])
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
                except ModelInactiveError as e:
                    message = _("Unable to save. Please verify the model status is active")
                    return JSONResponse({"status": "false", "message": [_(e.title), _(str(message))]}, status=500)
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
            except ModelInactiveError as e:
                message = _("Unable to save. Please verify the model status is active")
                return JSONResponse({"status": "false", "message": [_(e.title), _(str(message))]}, status=500)

        start = request.GET.get("start", 0)
        se.es.indices.refresh(index=se._add_prefix("resource_relations"))
        resource = Resource.objects.get(pk=root_resourceinstanceid[0])
        page = 1 if request.GET.get("page") == "" else int(request.GET.get("page", 1))
        related_resources = resource.get_related_resources(lang=lang, start=start, limit=1000, page=page, user=request.user)
        ret = []

        if related_resources is not None:
            ret = self.paginate_related_resources(related_resources, page, request)

        return JSONResponse(ret, indent=4)
