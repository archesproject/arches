from collections import defaultdict
from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Max
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.utils.translation import get_language, gettext as _

from arches.app.models.models import (
    ControlledList,
    ControlledListItem,
    ControlledListItemLabel,
    Language,
)
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.decorators import group_required
from arches.app.utils.response import JSONErrorResponse, JSONResponse
from arches.app.utils.string_utils import str_to_bool


def serialize(obj, depth_map=None, flat=False):
    if depth_map is None:
        depth_map = defaultdict(int)
    match obj:
        case ControlledList():
            return {
                "id": str(obj.id),
                "name": obj.name,
                "dynamic": obj.dynamic,
                "items": sorted(
                    [
                        serialize(item, depth_map, flat)
                        for item in obj.items.all()
                        if flat or item.parent_id is None
                    ],
                    key=lambda d: d["sortorder"],
                ),
            }
        case ControlledListItem():
            if obj.parent_id:
                depth_map[obj.id] = depth_map[obj.parent_id] + 1
            data = {
                "id": str(obj.id),
                "uri": obj.uri,
                "sortorder": obj.sortorder,
                "labels": [serialize(label, depth_map) for label in obj.labels.all()],
                "parent_id": str(obj.parent_id) if obj.parent_id else None,
                "depth": depth_map[obj.id],
            }
            if not flat:
                data["children"] = sorted(
                    [serialize(child, depth_map, flat) for child in obj.children.all()],
                    key=lambda d: d["sortorder"],
                )
            return data
        case ControlledListItemLabel():
            return {
                "id": str(obj.id),
                "valuetype": obj.value_type_id,
                "language": obj.language_id,
                "value": obj.value,
                "item_id": obj.item_id,
            }


def prefetch_terms(request):
    """Children at arbitrary depth will still be returned, but tell
    the ORM to prefetch a certain depth to mitigate N+1 queries after."""
    prefetch_depth = request.GET.get("prefetchDepth", 3)
    find_children = not str_to_bool(request.GET.get("flat", "false"))

    prefetch_terms = []
    for i in range(prefetch_depth):
        if i == 0:
            prefetch_terms.extend(["items", "items__labels"])
        elif find_children:
            prefetch_terms.extend(
                [f"items{'__children' * i}", f"items{'__children' * i}__labels"]
            )
    return prefetch_terms


def handle_items(itemDicts):
    items_to_save = []
    labels_to_save = []

    def handle_item(itemDict):
        nonlocal items_to_save
        nonlocal labels_to_save

        # Deletion/insertion of list items not yet implemented.
        labels = itemDict.pop("labels")
        # Altering hierarchy is done by altering parents.
        children = itemDict.pop("children", None)
        itemDict.pop("depth", None)

        item_to_save = ControlledListItem(**itemDict)
        item_to_save._state.adding = False  # allows checking uniqueness
        items_to_save.append(item_to_save)

        for label in labels:
            label["language_id"] = label.pop("language")
            label["value_type_id"] = label.pop("valuetype")
            label.pop("item_id")  # trust the item, not the label
            labels_to_save.append(
                ControlledListItemLabel(item_id=item_to_save.id, **label)
            )

        # Recurse
        for child in children:
            handle_item(child)

    for itemDict in itemDicts:
        handle_item(itemDict)

    # Consider skipping uniqueness checks and just letting IntegrityError
    # bubble up. But doing Django validation provides a localized error.
    for item_to_save in items_to_save:
        item_to_save.full_clean(exclude=["parent", "list", "id"])

    ControlledListItem.objects.bulk_update(
        items_to_save, fields=["uri", "sortorder", "parent"]
    )
    ControlledListItemLabel.objects.bulk_update(
        labels_to_save, fields=["value", "value_type", "language"]
    )


@method_decorator(
    group_required("RDM Administrator", raise_exception=True), name="dispatch"
)
class ControlledListsView(View):
    def get(self, request):
        """Returns either a flat representation (?flat=true) or a tree (default)."""
        data = {
            "controlled_lists": [
                serialize(obj, flat=str_to_bool(request.GET.get("flat", "false")))
                for obj in ControlledList.objects.all()
                .order_by("name")
                .prefetch_related(*prefetch_terms(request))
            ],
        }

        return JSONResponse(data)


@method_decorator(
    group_required("RDM Administrator", raise_exception=True), name="dispatch"
)
class ControlledListView(View):
    def get(self, request, **kwargs):
        """Returns either a flat representation (?flat=true) or a tree (default)."""
        list_id = kwargs.get("id")
        try:
            lst = ControlledList.objects.prefetch_related(*prefetch_terms(request)).get(
                pk=list_id
            )
        except ControlledList.DoesNotExist:
            return JSONErrorResponse(status=404)
        return JSONResponse(
            serialize(lst, flat=str_to_bool(request.GET.get("flat", "false")))
        )

    def post(self, request, **kwargs):
        if not (list_id := kwargs.get("id", None)):
            # Add a new list.
            lst = ControlledList(name=_("Untitled List: ") + datetime.now().isoformat())
            lst.save()
            return JSONResponse(serialize(lst))

        data = JSONDeserializer().deserialize(request.body)

        qs = (
            ControlledListItem.objects.filter(list_id=list_id)
            .select_related("list")
            .select_for_update()
        )
        # TODO: lock labels?

        items_to_save = []
        labels_to_save = []
        try:
            with transaction.atomic():
                try:
                    clist = qs[0].list
                except (IndexError, ControlledListItem.DoesNotExist):
                    clist = ControlledList.objects.get(pk=list_id)
                except ControlledList.DoesNotExist:
                    return JSONErrorResponse(status=404)

                clist.dynamic = data["dynamic"]
                clist.name = data["name"]

                for item in data["items"]:
                    item["list_id"] = list_id
                handle_items(data["items"])

                clist.save()
        except ValidationError as e:
            return JSONErrorResponse(message=" ".join(e.messages), status=400)
        except:
            return JSONErrorResponse()

        return JSONResponse(status=200)

    def delete(self, request, **kwargs):
        list_id = kwargs.get("id")
        objs_deleted, _ = ControlledList.objects.filter(pk=list_id).delete()
        if not objs_deleted:
            return JSONErrorResponse(status=404)
        return JSONResponse(status=204)


@method_decorator(
    group_required("RDM Administrator", raise_exception=True), name="dispatch"
)
class ControlledListItemView(View):
    def add_new_item(self, request):
        data = JSONDeserializer().deserialize(request.body)

        try:
            lst = (
                ControlledList.objects.filter(pk=data["list_id"])
                .annotate(max_sortorder=Max("items__sortorder"))
                .get()
            )
        except ControlledList.DoesNotExist:
            return JSONErrorResponse(status=404)

        if lst.max_sortorder is None:
            sortorder = 0
        else:
            sortorder = lst.max_sortorder + 1

        try:
            with transaction.atomic():
                item = ControlledListItem(
                    list=lst,
                    sortorder=sortorder,
                    parent_id=data.get("parent_id", None),
                )
                item.save()
                label = ControlledListItemLabel(
                    item=item,
                    value=_("New Label: ") + datetime.now().isoformat(),
                    value_type_id="prefLabel",
                    language_id=get_language(),
                )
                label.save()
        except:
            return JSONErrorResponse()

        return JSONResponse(serialize(item))

    def post(self, request, **kwargs):
        if not (item_id := kwargs.get("id", None)):
            return self.add_new_item(request)

        # Update list item
        data = JSONDeserializer().deserialize(request.body)

        try:
            with transaction.atomic():
                for _item in ControlledListItem.objects.filter(
                    pk=item_id
                ).select_for_update():
                    handle_items([data])
                    break
                else:
                    JSONErrorResponse(status=404)

        except ValidationError as e:
            return JSONErrorResponse(message=" ".join(e.messages), status=400)
        except:
            return JSONErrorResponse()

        return JSONResponse(status=200)

    def delete(self, request, **kwargs):
        item_id = kwargs.get("id")
        objs_deleted, _ = ControlledListItem.objects.filter(pk=item_id).delete()
        if not objs_deleted:
            return JSONErrorResponse(status=404)
        return JSONResponse(status=204)


@method_decorator(
    group_required("RDM Administrator", raise_exception=True), name="dispatch"
)
class LabelView(View):
    def add_new_label(self, request):
        data = JSONDeserializer().deserialize(request.body)

        label = ControlledListItemLabel(
            item_id=data["item_id"],
            value_type_id=data["valuetype"],
            language=Language.objects.get(code=data["language"]),
            value=data["value"],
        )
        try:
            label.save()
        except (ControlledListItem.DoesNotExist, Language.DoesNotExist):
            return JSONErrorResponse(status=404)
        except IntegrityError as e:
            return JSONErrorResponse(message=" ".join(e.args), status=400)
        except:
            return JSONErrorResponse()

        return JSONResponse(serialize(label))

    def post(self, request, **kwargs):
        if not (label_id := kwargs.get("id", None)):
            return self.add_new_label(request)

        # Update label
        data = JSONDeserializer().deserialize(request.body)

        try:
            ControlledListItemLabel.objects.filter(pk=label_id).update(
                value=data["value"], language_id=data["language"]
            )
        except ControlledListItemLabel.DoesNotExist:
            return JSONErrorResponse(status=404)
        except IntegrityError as e:
            return JSONErrorResponse(message=" ".join(e.args), status=400)
        except:
            return JSONErrorResponse()

        return JSONResponse(serialize(ControlledListItemLabel.objects.get(pk=label_id)))

    def delete(self, request, **kwargs):
        label_id = kwargs.get("id")
        objs_deleted, _ = ControlledListItemLabel.objects.filter(pk=label_id).delete()
        if not objs_deleted:
            return JSONErrorResponse(status=404)
        return JSONResponse(status=204)
