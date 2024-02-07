from collections import defaultdict
from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.utils.translation import get_language, gettext as _


from arches.app.models.models import ControlledList, ControlledListItem, Label, Language
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.decorators import group_required
from arches.app.utils.response import JSONErrorResponse, JSONResponse


def serialize(obj, depth_map=None):
    if depth_map is None:
        depth_map = defaultdict(int)
    match obj:
        case ControlledList():
            return {
                "id": str(obj.id),
                "name": obj.name,
                "dynamic": obj.dynamic,
                "items": sorted(
                    [serialize(item, depth_map) for item in obj.items.all()],
                    key=lambda d: d["sortorder"],
                ),
            }
        case ControlledListItem():
            if obj.parent_id:
                depth_map[obj.id] = depth_map[obj.parent_id] + 1
            return {
                "id": str(obj.id),
                "uri": obj.uri,
                "sortorder": obj.sortorder,
                "labels": [serialize(label, depth_map) for label in obj.labels.all()],
                "children": sorted(
                    [serialize(child, depth_map) for child in obj.children.all()],
                    key=lambda d: d["sortorder"],
                ),
                "parent_id": str(obj.parent_id) if obj.parent_id else None,
                "depth": depth_map[obj.id],
            }
        case Label():
            return {
                "id": str(obj.id),
                "valuetype": obj.value_type_id,
                "language": obj.language_id,
                "value": obj.value,
            }


def prefetch_terms(request):
    """Children at arbitrary depth will still be returned, but tell
    the ORM to expect a certain number to mitigate N+1 queries."""
    prefetch_depth = request.GET.get("prefetchDepth", 3)
    prefetch_terms = []
    for i in range(prefetch_depth):
        if i == 0:
            prefetch_terms.extend(["items", "items__labels"])
        else:
            prefetch_terms.extend(
                [f"items{'__children' * i}", f"items{'__children' * i}__labels"]
            )
    return prefetch_terms


def handle_items(itemDicts):
    items_to_save = []
    labels_to_save = []

    for itemDict in itemDicts:
        # Deletion/insertion of list items not yet implemented.
        labels = itemDict.pop("labels")
        # Altering hierarchy is done by altering parents.
        itemDict.pop("children", None)
        itemDict.pop("depth", None)

        item_to_save = ControlledListItem(list_id=id, **itemDict)
        item_to_save._state.adding = False  # allows checking uniqueness
        items_to_save.append(item_to_save)

        for label in labels:
            label["language_id"] = label.pop("language")
            label["value_type_id"] = label.pop("valuetype")
            labels_to_save.append(Label(item_id=item_to_save.id, **label))

    # Consider skipping uniqueness checks and just letting IntegrityError
    # bubble up. But doing Django validation provides a localized error.
    for itemDict in items_to_save:
        item_to_save.full_clean(exclude=["parent", "list", "id"])

    ControlledListItem.objects.bulk_update(
        items_to_save, fields=["uri", "sortorder", "parent"]
    )
    Label.objects.bulk_update(
        labels_to_save, fields=["value", "value_type", "language"]
    )


@method_decorator(
    group_required("RDM Administrator", raise_exception=True), name="dispatch"
)
class ControlledListsView(View):
    def get(self, request):
        data = {
            "controlled_lists": [
                serialize(obj)
                for obj in ControlledList.objects.all()
                .order_by("name")
                .prefetch_related(*prefetch_terms(request))
            ],
            "languages": {lang.code: lang.name for lang in Language.objects.all()},
        }

        return JSONResponse(data)


@method_decorator(
    group_required("RDM Administrator", raise_exception=True), name="dispatch"
)
class ControlledListView(View):
    def get(self, request, **kwargs):
        id = kwargs.get("id")
        try:
            lst = ControlledList.objects.prefetch_related(*prefetch_terms(request)).get(
                pk=id
            )
        except ControlledList.DoesNotExist:
            return JSONErrorResponse(status=404)
        return JSONResponse(serialize(lst))

    def post(self, request, **kwargs):
        if not (id := kwargs.get("id", None)):
            # Add a new list.
            lst = ControlledList(name=_("Untitled List: ") + datetime.now().isoformat())
            lst.save()
            return JSONResponse(serialize(lst))

        data = JSONDeserializer().deserialize(request.body)

        qs = (
            ControlledListItem.objects.filter(list_id=id)
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
                except ControlledListItem.DoesNotExist:
                    clist = ControlledList.objects.get(pk=id)
                except (IndexError, ControlledList.DoesNotExist):
                    return JSONErrorResponse(status=404)

                clist.dynamic = data["dynamic"]
                clist.name = data["name"]

                handle_items(data["items"])

                clist.save()
        except ValidationError as e:
            return JSONErrorResponse(message=" ".join(e.messages), status=400)
        except:
            return JSONErrorResponse()

        return JSONResponse(status=200)

    def delete(self, request, **kwargs):
        id = kwargs.get("id")
        objs_deleted, _ = ControlledList.objects.filter(pk=id).delete()
        if not objs_deleted:
            return JSONErrorResponse(status=404)
        return JSONResponse(status=204)


@method_decorator(
    group_required("RDM Administrator", raise_exception=True), name="dispatch"
)
class ControlledListItemView(View):
    def add_new_item(self, request, parent_id):
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
                    parent_id=parent_id,
                )
                item.save()
                label = Label(
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
        if not (id := kwargs.get("id", None)):
            return self.add_new_item(request, parent_id=kwargs.get("parent_id", None))

        # Update list item
        data = JSONDeserializer().deserialize(request.body)

        try:
            with transaction.atomic():
                for _item in (
                    ControlledListItem.objects.filter(pk=id)
                    .select_for_update()
                ):
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
        id = kwargs.get("id")
        objs_deleted, _ = ControlledListItem.objects.filter(pk=id).delete()
        if not objs_deleted:
            return JSONErrorResponse(status=404)
        return JSONResponse(status=204)


@method_decorator(
    group_required("RDM Administrator", raise_exception=True), name="dispatch"
)
class LabelView(View):
    def delete(self, request, **kwargs):
        id = kwargs.get("id")
        objs_deleted, _ = Label.objects.filter(pk=id).delete()
        if not objs_deleted:
            return JSONErrorResponse(status=404)
        return JSONResponse(status=204)
