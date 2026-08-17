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

from django.utils.feedgenerator import rfc3339_date
from django.urls import reverse
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from django.core.exceptions import ObjectDoesNotExist
import json


class ActivityStreamCollection(object):
    # uris MUST contain keys to URIs: first, last, root (Collection URI)
    def __init__(
        self,
        uris,
        totalItems,
        summary=None,
        base_uri_for_arches="https://example.org",
        context="https://www.w3.org/ns/activitystreams",
        perm_level="full",
    ):
        self.representation = {
            "@context": context,
            "type": "OrderedCollection",
            "id": uris["root"],
            "totalItems": totalItems,
            "first": {"id": uris["first"], "type": "OrderedCollectionPage"},
            "last": {"id": uris["last"], "type": "OrderedCollectionPage"},
        }
        self.uris = uris
        self.id = uris["root"]
        self.perm_level = perm_level
        self.base_uri_for_arches = base_uri_for_arches

    def to_jsonld(self):
        return json.dumps(self.representation)

    def to_obj(self):
        return self.representation.copy()

    def generate_page(self, page_uris, editlog_object_generator):
        page_uris["root"] = self.id
        page_uris["base_uri_for_arches"] = self.base_uri_for_arches
        colpage = ActivityStreamCollectionPage(
            page_uris,
            totalItems=self.representation["totalItems"],
            perm_level=self.perm_level,
        )
        for op in editlog_object_generator:
            colpage.add_item(op)
        return colpage


class ActivityStreamCollectionPage(object):

    type_mapping = {
        "create": "Create",
        "delete": "Delete",
        "tile delete": "Update",  # pass all tile events as Resource updates.
        "tile create": "Update",
        "tile edit": "Update",
        "delete edit": "Edit Deleted",
    }

    def __init__(
        self,
        uris,  # MUST contain keys to URIs: this, root (Collection URI)
        # SHOULD contain keys to URIs: next, prev
        context="https://www.w3.org/ns/activitystreams",
        totalItems=0,
        perm_level="full",
    ):  # "full"|"idsonly"
        self._boilerplate = {
            "@context": context,
            "type": "OrderedCollectionPage",
            "id": uris["this"],
        }

        self._boilerplate["partOf"] = {
            "id": uris["root"],
            "type": "OrderedCollection",
            "totalItems": totalItems,
        }

        for k, v in [(x, y) for x, y in list(uris.items()) if x in ["next", "prev"]]:
            self._boilerplate[k] = {"id": v, "type": "OrderedCollectionPage"}

        self._items = []
        self.base_uri_for_arches = uris.get("base_uri_for_arches", "")
        self.perm_level = perm_level

    def summary(self, summary=None):
        if summary is not None:
            self._boilerplate["summary":summary]
        return self._boilerplate["summary":summary]

    def startIndex(self, startIndex=None):
        if startIndex is not None:
            self._boilerplate["startIndex"] = startIndex
        return self._boilerplate["startIndex"]

    def add_item(self, editlog_object, perm_level="full"):
        # add a JSON-LD obj to a list of the Activities
        self._items.append(
            self.editlog_to_collection_item(editlog_object, self.perm_level)
        )

    def editlog_to_collection_item(self, editlog_object, perm_level="full"):
        def add_actor(editlog_object, perm_level=perm_level):
            actor = {
                "type": "Person",
                "id": "{0}/{1}".format(
                    self.base_uri_for_arches + reverse("user_profile_manager"),
                    editlog_object.userid,
                ),
            }
            if perm_level == "full":
                actor["name"] = "{0}, {1}".format(
                    editlog_object.user_lastname, editlog_object.user_firstname
                )
                if actor["name"] == ", ":
                    del actor["name"]
                actor["tag"] = editlog_object.user_username
                if actor["tag"] == "null":
                    del actor["tag"]
            return actor

        def add_resource(editlog_object, perm_level=perm_level):
            obj = {"type": "Object"}
            try:
                r = Resource.objects.get(pk=editlog_object.resourceinstanceid)
                rclass = r.get_root_ontology()
                if rclass:
                    obj = {"type": rclass}
            except ObjectDoesNotExist:
                pass

            if editlog_object.edittype == "delete":
                # Tombstone instead.
                obj["formerType"] = obj["type"]
                obj["type"] = "Tombstone"

            obj["id"] = self.base_uri_for_arches + reverse(
                "resources", args=(editlog_object.resourceinstanceid,)
            )

            return obj

        def add_tile(editlog_object, perm_level=perm_level):
            obj = {"type": "Object"}  # Tile?
            obj["url"] = "{0}node/{1}/tile/{2}".format(
                settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT,
                editlog_object.nodegroupid,
                editlog_object.tileinstanceid,
            )
            return obj

        item = {"type": self.type_mapping.get(editlog_object.edittype, "Activity")}

        # what's the correct attr here?
        item["endTime"] = rfc3339_date(editlog_object.timestamp)

        if item["type"] in ("Create", "Delete"):
            # activity affects main resource
            item["actor"] = add_actor(editlog_object)
            item["object"] = add_resource(editlog_object)

        if item["type"] in ("Update"):
            # activity affects a Tile associated with a resource
            # If a Tile associated with a resource is altered, bubble that
            # change up to be about the Resource, and mark it as an 'Update'
            item["actor"] = add_actor(editlog_object)
            # item["object"] = add_tile(editlog_object)
            item["object"] = add_resource(editlog_object)

        return item

    def to_obj(self):
        export = self._boilerplate.copy()
        export["orderedItems"] = self._items
        return export

    def to_jsonld(self, pagination=False):
        export = self.to_obj()
        return json.dumps(export)
