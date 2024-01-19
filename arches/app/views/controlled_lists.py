from django.views.generic import View
from django.utils.decorators import method_decorator

from arches.app.models.models import ControlledList, ControlledListItem, Label
from arches.app.utils.decorators import group_required
from arches.app.utils.response import JSONResponse


@method_decorator(
    group_required("RDM Administrator", raise_exception=True), name="dispatch"
)
class ControlledListView(View):
    @classmethod
    def serialize(cls, obj):
        match obj:
            case ControlledList():
                return {
                    "id": str(obj.id),
                    "name": obj.name,
                    "dynamic": obj.dynamic,
                    "items": [cls.serialize(item) for item in obj.items.all()],
                }
            case ControlledListItem():
                return {
                    "id": str(obj.id),
                    "uri": obj.uri,
                    "labels": [cls.serialize(label) for label in obj.labels.all()],
                    "children": [cls.serialize(child) for child in obj.children.all()],
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
                self.serialize(obj)
                for obj in ControlledList.objects.all().prefetch_related(
                    *prefetch_terms
                )
            ]
        }

        return JSONResponse(data)
