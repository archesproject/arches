from collections import defaultdict
from datetime import datetime

from django.db import transaction
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _


from arches.app.models.models import ControlledList, ControlledListItem, Label
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.decorators import group_required
from arches.app.utils.response import JSONErrorResponse, JSONResponse


@method_decorator(
    group_required("RDM Administrator", raise_exception=True), name="dispatch"
)
class ControlledListsView(View):
    @classmethod
    def serialize(cls, obj, depth_map):
        match obj:
            case ControlledList():
                return {
                    "id": str(obj.id),
                    "name": obj.name,
                    "dynamic": obj.dynamic,
                    "items": [cls.serialize(item, depth_map) for item in obj.items.all()],
                }
            case ControlledListItem():
                if obj.parent_id:
                    depth_map[obj.id] = depth_map[obj.parent_id] + 1
                return {
                    "id": str(obj.id),
                    "uri": obj.uri,
                    "sortorder": obj.sortorder,
                    "labels": [cls.serialize(label, depth_map) for label in obj.labels.all()],
                    "children": sorted(
                        [cls.serialize(child, depth_map) for child in obj.children.all()],
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

    def get(self, request):
        prefetch_depth = request.GET.get("prefetchDepth", 3)
        prefetch_terms = []
        for i in range(prefetch_depth):
            if i == 0:
                prefetch_terms.extend(["items", "items__labels"])
            else:
                prefetch_terms.extend(
                    [f"items{'__children' * i}", f"items{'__children' * i}__labels"]
                )

        data = {
            "controlled_lists": [
                self.serialize(obj, depth_map=defaultdict(int))
                for obj in ControlledList.objects.all().order_by("name").prefetch_related(
                    *prefetch_terms
                )
            ]
        }

        return JSONResponse(data)

    def post(self, request):
        l = ControlledList(name=_("Untitled List: ") + datetime.now().isoformat())
        l.save()
        return self.get(request)


@method_decorator(
    group_required("RDM Administrator", raise_exception=True), name="dispatch"
)
class ControlledListView(View):
    def post(self, request, **kwargs):
        id = kwargs.get("id")
        data = JSONDeserializer().deserialize(request.body)

        list_locked = ControlledList.objects.filter(id=id).select_for_update()

        items_to_save = []
        with transaction.atomic():
            for clist in list_locked:
                clist.items.all().delete()
                clist.dynamic = data["dynamic"]
                clist.name = data["name"]

                for item in data["items"]:
                    labels = item.pop("labels")
                    item_to_save = ControlledListItem(**item)
                    items_to_save.append(item_to_save)

                    labels_to_save = []
                    for label in labels:
                        label["language_id"] = label.pop("language")
                        label["value_type_id"] = label.pop("valuetype")
                        labels_to_save.append(Label(**label))

                    item_to_save.labels.set(labels_to_save, bulk=False)

                clist.items.set(items_to_save, bulk=False)

                clist.save()

        return JSONResponse(status=200)

    def delete(self, request, **kwargs):
        id = kwargs.get("id")
        objs_deleted, _ = ControlledList.objects.filter(pk=id).delete()
        if not objs_deleted:
            return JSONErrorResponse(status=404)
        return JSONResponse(status=204)
