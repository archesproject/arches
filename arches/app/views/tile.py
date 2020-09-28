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

import importlib
import json as jsonparser
import logging
import traceback
import uuid
import arches.app.utils.zip as arches_zip
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models import models
from arches.app.models.resource import Resource, ModelInactiveError
from arches.app.models.tile import Tile, TileValidationError
from arches.app.models.system_settings import settings
from arches.app.utils.response import JSONResponse, JSONErrorResponse
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.decorators import can_edit_resource_instance
from arches.app.utils.permission_backend import user_is_resource_reviewer
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.views.generic import View
from django.db import transaction
from arches.app.models.resource import EditLog

logger = logging.getLogger(__name__)


@method_decorator(can_edit_resource_instance, name="dispatch")
class TileData(View):
    action = "update_tile"

    def delete_provisional_edit(self, tile, user, request):
        provisionaledits = None
        if tile.provisionaledits is not None:
            provisionaledits = tile.provisionaledits
            if user in provisionaledits:
                provisional_editor = User.objects.get(pk=user)
                edit = provisionaledits[user]
                provisionaledits.pop(user)
                if len(provisionaledits) == 0:
                    tile.provisionaledits = None
                else:
                    tile.provisionaledits = provisionaledits
                tile.save(
                    request=request,
                    provisional_edit_log_details={
                        "user": request.user,
                        "action": "delete edit",
                        "edit": edit,
                        "provisional_editor": provisional_editor,
                    },
                )

    def handle_save_error(self, e, tile_id="", title=_("Saving tile failed"), message=None):
        if message is None:
            message = type(e).__name__
            if hasattr(e, "message") and e.message:
                message += ": {0}".format(e.message)
        else:
            message = str(e)
        logger.error(
            title
            + """ [Tile id: {tile_id}] \
                     [Exception message: {message}] \
                     [Exception trace: {trace}]""".format(
                tile_id=tile_id, message=message, trace=traceback.format_exc()
            )
        )

        return JSONErrorResponse(_(title), _(str(message)), {"message": message, "title": title})

    def post(self, request):
        if self.action == "update_tile":
            json = request.POST.get("data", None)
            accepted_provisional = request.POST.get("accepted_provisional", None)
            if accepted_provisional is not None:
                accepted_provisional_edit = JSONDeserializer().deserialize(accepted_provisional)
            if json is not None:
                data = JSONDeserializer().deserialize(json)
                data["resourceinstance_id"] = "" if "resourceinstance_id" not in data else data["resourceinstance_id"]
                if data["resourceinstance_id"] == "":
                    data["resourceinstance_id"] = uuid.uuid4()
                try:
                    models.ResourceInstance.objects.get(pk=data["resourceinstance_id"])
                except ObjectDoesNotExist:
                    try:
                        resource = Resource(uuid.UUID(str(data["resourceinstance_id"])))
                    except ValueError:
                        resource = Resource()
                    graphid = models.Node.objects.filter(nodegroup=data["nodegroup_id"])[0].graph_id
                    resource.graph_id = graphid
                    try:
                        resource.save(user=request.user)
                        data["resourceinstance_id"] = resource.pk
                        resource.index()
                    except ModelInactiveError as e:
                        message = _("Unable to save. Please verify the model status is active")
                        return JSONResponse({"status": "false", "message": [_(e.title), _(str(message))]}, status=500)
                tile_id = data["tileid"]
                resource_instance = models.ResourceInstance.objects.get(pk=data["resourceinstance_id"])
                is_active = resource_instance.graph.isactive
                if tile_id is not None and tile_id != "":
                    try:
                        old_tile = Tile.objects.get(pk=tile_id)
                    except ObjectDoesNotExist as e:
                        return self.handle_save_error(e, _("This tile is no longer available"), _("It was likely deleted by another user"))

                tile = Tile(data)

                if tile.filter_by_perm(request.user, "write_nodegroup") and is_active is True:
                    try:
                        with transaction.atomic():
                            try:
                                if accepted_provisional is None:
                                    try:
                                        tile.save(request=request)
                                    except TileValidationError as e:
                                        resource_tiles = models.TileModel.objects.filter(resourceinstance=tile.resourceinstance)
                                        if resource_tiles.count() == 0:
                                            Resource.objects.get(pk=tile.resourceinstance_id).delete(request.user)
                                        title = _("Unable to save. Please verify your input is valid")
                                        return self.handle_save_error(e, tile_id, title=title)
                                    except ModelInactiveError as e:
                                        message = _("Unable to save. Please verify the model status is active")
                                        return JSONResponse({"status": "false", "message": [_(e.title), _(str(message))]}, status=500)
                                else:
                                    if accepted_provisional is not None:
                                        provisional_editor = User.objects.get(pk=accepted_provisional_edit["user"])
                                        prov_edit_log_details = {
                                            "user": request.user,
                                            "action": "accept edit",
                                            "edit": accepted_provisional_edit,
                                            "provisional_editor": provisional_editor,
                                        }
                                    tile.save(request=request, provisional_edit_log_details=prov_edit_log_details)

                                if tile.provisionaledits is not None and str(request.user.id) in tile.provisionaledits:
                                    tile.data = tile.provisionaledits[str(request.user.id)]["value"]

                            except Exception as e:
                                return self.handle_save_error(e, tile_id)

                            tile.after_update_all()
                            update_system_settings_cache(tile)

                    except Exception as e:
                        return self.handle_save_error(e, tile_id)

                    return JSONResponse(tile)
                elif is_active is False:
                    response = {"status": "false", "message": [_("Request Failed"), _("Unable to Save. Verify model status is active")]}
                    return JSONResponse(response, status=500)
                else:
                    return JSONErrorResponse(_("Request Failed"), _("Permission Denied"))

        if self.action == "reorder_tiles":
            json = request.body
            if json is not None:
                data = JSONDeserializer().deserialize(json)

                if "tiles" in data and len(data["tiles"]) > 0:
                    sortorder = 0
                    with transaction.atomic():
                        for tile in data["tiles"]:
                            t = Tile(tile)
                            if t.filter_by_perm(request.user, "write_nodegroup"):
                                t.sortorder = sortorder
                                t.save(update_fields=["sortorder"], request=request)
                                sortorder = sortorder + 1

                    return JSONResponse(data)

        if self.action == "delete_provisional_tile":
            user = request.POST.get("user", None)
            tileid = request.POST.get("tileid", None)
            users = request.POST.get("users", None)
            tile = Tile.objects.get(tileid=tileid)
            is_provisional = tile.is_provisional()

            if tileid is not None and user is not None:
                provisionaledits = self.delete_provisional_edit(tile, user, request)

            elif tileid is not None and users is not None:
                users = jsonparser.loads(users)
                for user in users:
                    self.delete_provisional_edit(tile, user, request)

            if is_provisional == True:
                return JSONResponse({"result": "delete"})
            else:
                return JSONResponse({"result": "success"})

        return HttpResponseNotFound()

    def delete(self, request):
        json = request.body
        if json is not None:
            ret = []
            data = JSONDeserializer().deserialize(json)
            with transaction.atomic():
                try:
                    tile = Tile.objects.get(tileid=data["tileid"])
                    resource_instance = tile.resourceinstance
                    is_active = resource_instance.graph.isactive
                except ObjectDoesNotExist:
                    return JSONErrorResponse(_("This tile is no longer available"), _("It was likely already deleted by another user"))
                user_is_reviewer = user_is_resource_reviewer(request.user)
                if (user_is_reviewer or tile.is_provisional() is True) and is_active is True:
                    if tile.filter_by_perm(request.user, "delete_nodegroup"):
                        nodegroup = models.NodeGroup.objects.get(pk=tile.nodegroup_id)
                        if tile.is_provisional() is True and len(list(tile.provisionaledits.keys())) == 1:
                            provisional_editor_id = list(tile.provisionaledits.keys())[0]
                            edit = tile.provisionaledits[provisional_editor_id]
                            provisional_editor = User.objects.get(pk=provisional_editor_id)
                            reviewer = request.user
                            tile.delete(
                                request=request,
                                provisional_edit_log_details={
                                    "user": reviewer,
                                    "action": "delete edit",
                                    "edit": edit,
                                    "provisional_editor": provisional_editor,
                                },
                            )
                        else:
                            tile.delete(request=request)
                        tile.after_update_all()
                        update_system_settings_cache(tile)
                        return JSONResponse(tile)
                    else:
                        return JSONErrorResponse(_("Request Failed"), _("Permission Denied"))
                elif is_active is False:
                    response = {"status": "false", "message": [_("Request Failed"), _("Unable to delete. Verify model status is active")]}
                    return JSONResponse(response, status=500)
                else:
                    return JSONErrorResponse(
                        _("Request Failed"), _("You do not have permissions to delete a tile with authoritative data.")
                    )

        return HttpResponseNotFound()

    def download_files(self, request):
        try:
            tileids = jsonparser.loads(request.GET.get("tiles", None))
            nodeid = request.GET.get("node", None)
            tiles = Tile.objects.filter(pk__in=tileids)
            files = sum(
                [
                    [{"name": file["name"], "outputfile": models.File.objects.get(pk=file["file_id"]).path} for file in tile.data[nodeid]]
                    for tile in tiles
                ],
                [],
            )
            response = arches_zip.zip_response(files, "file-viewer-download.zip")
            return response
        except TypeError as e:
            logger.error("Tile id array required to download files.")
            return JSONErrorResponse(_("Request Failed"), _(e))

    def get(self, request):
        if self.action == "tile_history":
            start = request.GET.get("start")
            end = request.GET.get("end")
            edits = (
                EditLog.objects.filter(provisional_userid=request.user.id)
                .filter(timestamp__range=[start, end])
                .order_by("tileinstanceid", "timestamp")
            )
            resourceinstanceids = [e["resourceinstanceid"] for e in edits.values("resourceinstanceid")]
            deleted_resource_edits = EditLog.objects.filter(resourceinstanceid__in=resourceinstanceids).filter(edittype="delete")
            deleted_resource_instances = [e["resourceinstanceid"] for e in deleted_resource_edits.values("resourceinstanceid")]
            summary = {}
            for edit in edits:
                if edit.tileinstanceid not in summary:
                    summary[edit.tileinstanceid] = {"pending": False, "tileid": edit.tileinstanceid}
                summary[edit.tileinstanceid]["lasttimestamp"] = edit.timestamp
                summary[edit.tileinstanceid]["lastedittype"] = edit.provisional_edittype
                summary[edit.tileinstanceid]["reviewer"] = ""
                summary[edit.tileinstanceid]["resourceinstanceid"] = edit.resourceinstanceid
                summary[edit.tileinstanceid]["resourcedisplayname"] = edit.resourcedisplayname
                summary[edit.tileinstanceid]["resourcemodelid"] = edit.resourceclassid
                summary[edit.tileinstanceid]["nodegroupid"] = edit.nodegroupid
                summary[edit.tileinstanceid]["resource_deleted"] = True if edit.resourceinstanceid in deleted_resource_instances else False
                if edit.provisional_edittype in ["accept edit", "delete edit"]:
                    summary[edit.tileinstanceid]["reviewer"] = edit.user_username

            chronological_summary = []
            resource_models = (
                models.GraphModel.objects.filter(isresource=True)
                .exclude(graphid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
                .values("iconclass", "color", "graphid", "name")
            )
            cards = models.CardModel.objects.all().values("name", "nodegroup_id")
            card_lookup = {str(card["nodegroup_id"]): card for card in cards}
            resource_model_lookup = {str(graph["graphid"]): graph for graph in resource_models}
            for k, v in summary.items():
                if v["lastedittype"] not in ["accept edit", "delete edit"]:
                    if models.TileModel.objects.filter(pk=k).exists():
                        tile = models.TileModel.objects.get(pk=k)
                        if tile.provisionaledits is not None and str(request.user.id) in tile.provisionaledits:
                            v["pending"] = True

                v["resourcemodel"] = resource_model_lookup[v["resourcemodelid"]]
                v["card"] = card_lookup[v["nodegroupid"]]
                if "graphid" in v["resourcemodel"]:
                    v["resourcemodel"].pop("graphid")
                if "nodegroup_id" in v["card"]:
                    v["card"].pop("nodegroup_id")
                chronological_summary.append(v)

            return JSONResponse(JSONSerializer().serialize(sorted(chronological_summary, key=lambda k: k["lasttimestamp"], reverse=True)))

        if self.action == "download_files":
            response = self.download_files(request)
            return response

# Move to util function
def get(id):
    try:
        uuid.UUID(id)
        return uuid.UUID(id), False
    except (ValueError, TypeError):
        return uuid.uuid4(), True


uuid.get_or_create = get


def update_system_settings_cache(tile):
    if str(tile.resourceinstance_id) == settings.RESOURCE_INSTANCE_ID:
        settings.update_from_db()
