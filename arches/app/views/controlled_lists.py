import logging
from collections import defaultdict
from datetime import datetime
from typing import TYPE_CHECKING

from django.contrib.postgres.expressions import ArraySubquery
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Max, OuterRef
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.utils.translation import get_language, gettext as _

from arches.app.models.models import (
    ControlledList,
    ControlledListItem,
    ControlledListItemLabel,
    Language,
    Node,
)
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.decorators import group_required
from arches.app.utils.permission_backend import get_nodegroups_by_perm
from arches.app.utils.response import JSONErrorResponse, JSONResponse
from arches.app.utils.string_utils import str_to_bool


if TYPE_CHECKING:
    from uuid import UUID

logger = logging.getLogger(__name__)


def serialize(obj, depth_map=None, flat=False, nodes=False):
    """
    This is a recursive function. The first caller (you) doesn't need
    to provide a `depth_map`, but the recursive calls (see below) do.

    flat=False provides a tree representation.
    flat=True is just that, flat (used in reference datatype widget).

    nodes=True assumes a controlled list model instance has been
    .annotate()'d with various node-related arrays. (The default
    nodes=False is mainly here to facilitate reusing this as a helper
    method when setting up unit tests; the view should set nodes=True.
    """
    if depth_map is None:
        depth_map = defaultdict(int)
    match obj:
        case ControlledList():
            data = {
                "id": str(obj.id),
                "name": obj.name,
                "dynamic": obj.dynamic,
                "search_only": obj.search_only,
                "items": sorted(
                    [
                        serialize(item, depth_map, flat)
                        for item in obj.controlled_list_items.all()
                        if flat or item.parent_id is None
                    ],
                    key=lambda d: d["sortorder"],
                ),
            }
            if nodes:
                data["nodes"] = []
                for node_id, node_name, nodegroup_id, graph_id in zip(
                    obj.node_ids,
                    obj.node_names,
                    obj.nodegroup_ids,
                    obj.graph_ids,
                    strict=True,
                ):
                    data["nodes"].append(
                        {
                            "id": node_id,
                            "name": node_name,
                            "nodegroup_id": nodegroup_id,
                            "graph_id": graph_id,
                        }
                    )
            return data
        case ControlledListItem():
            if obj.parent_id:
                depth_map[obj.id] = depth_map[obj.parent_id] + 1
            data = {
                "id": str(obj.id),
                "uri": obj.uri,
                "sortorder": obj.sortorder,
                "guide": obj.guide,
                "labels": [
                    serialize(label, depth_map)
                    for label in obj.controlled_list_item_labels.all()
                ],
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
                "item_id": obj.controlled_list_item_id,
            }


def prefetch_terms(request):
    """Children at arbitrary depth will still be returned, but tell
    the ORM to prefetch a certain depth to mitigate N+1 queries after."""
    prefetch_depth = request.GET.get("prefetchDepth", 3)
    find_children = not str_to_bool(request.GET.get("flat", "false"))

    terms = []
    for i in range(prefetch_depth):
        if i == 0:
            terms.extend(
                [
                    "controlled_list_items",
                    "controlled_list_items__controlled_list_item_labels",
                ]
            )
        elif find_children:
            terms.extend(
                [
                    f"controlled_list_items{'__children' * i}",
                    f"controlled_list_items{'__children' * i}__controlled_list_item_labels",
                ]
            )
    return terms


def handle_items(item_dicts):
    items_to_save = []
    labels_to_save = []

    def handle_item(item_dict):
        nonlocal items_to_save
        nonlocal labels_to_save

        # Deletion/insertion of list items not yet implemented.
        labels = item_dict.pop("labels")
        # Altering hierarchy is done by altering parents.
        children = item_dict.pop("children", None)
        item_dict.pop("depth", None)

        item_to_save = ControlledListItem(**item_dict)
        item_to_save._state.adding = False  # allows checking uniqueness
        items_to_save.append(item_to_save)

        for label in labels:
            label["language_id"] = label.pop("language")
            label["value_type_id"] = label.pop("valuetype")
            label.pop("item_id")  # trust the item, not the label
            labels_to_save.append(
                ControlledListItemLabel(
                    controlled_list_item_id=item_to_save.id, **label
                )
            )

        # Recurse
        for child in children:
            handle_item(child)

    for item_dict in item_dicts:
        handle_item(item_dict)

    # Consider skipping uniqueness checks and just letting IntegrityError
    # bubble up. But doing Django validation provides a localized error.
    for item_to_save in items_to_save:
        item_to_save.full_clean(exclude=["parent", "controlled_list", "id"])

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
        lists = (
            ControlledList.objects.all()
            .annotate(node_ids=self.node_subquery())
            .annotate(node_names=self.node_subquery("name"))
            .annotate(nodegroup_ids=self.node_subquery("nodegroup_id"))
            .annotate(graph_ids=self.node_subquery("graph_id"))
            .order_by("name")
            .prefetch_related(*prefetch_terms(request))
        )
        serialized_lists = [
            serialize(
                obj, nodes=True, flat=str_to_bool(request.GET.get("flat", "false"))
            )
            for obj in lists
        ]
        filtered = self.filter_permitted_nodegroups(serialized_lists, request)
        data = {"controlled_lists": filtered}

        return JSONResponse(data)

    @staticmethod
    def node_subquery(node_field: str = "pk"):
        return ArraySubquery(
            Node.with_controlled_list.filter(controlled_list=OuterRef("id"))
            .order_by("pk")
            .values(node_field)
        )

    def filter_permitted_nodegroups(self, serialized_lists, request):
        permitted_nodegroups = [
            ng.pk for ng in get_nodegroups_by_perm(request.user, "read_nodegroup")
        ]

        for lst in serialized_lists:
            lst["nodes"] = [
                node_dict
                for node_dict in lst["nodes"]
                if node_dict["nodegroup_id"] in permitted_nodegroups
            ]
        return serialized_lists


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
            ControlledListItem.objects.filter(controlled_list_id=list_id)
            .select_related("controlled_list")
            .select_for_update()
        )
        # Does not currently bother to lock labels.

        try:
            with transaction.atomic():
                try:
                    clist = qs[0].controlled_list
                except (IndexError, ControlledListItem.DoesNotExist):
                    clist = ControlledList.objects.get(pk=list_id)
                except ControlledList.DoesNotExist:
                    return JSONErrorResponse(status=404)

                clist.dynamic = data["dynamic"]
                clist.search_only = data["search_only"]
                clist.name = data["name"]

                for item in data["items"]:
                    item["controlled_list_id"] = list_id
                handle_items(data["items"])

                clist.save()
        except ValidationError as e:
            return JSONErrorResponse(message=" ".join(e.messages), status=400)
        except:
            return JSONErrorResponse()

        return JSONResponse(serialize(clist))

    def delete(self, request, **kwargs):
        list_id: UUID = kwargs.get("id")
        for node in Node.with_controlled_list.filter(controlled_list=list_id):
            try:
                lst = ControlledList.objects.get(id=list_id)
            except ControlledList.DoesNotExist:
                return JSONErrorResponse(status=404)
            return JSONErrorResponse(
                message=_(
                    "{controlled_list} could not be deleted: still in use by {graph} - {node}".format(
                        controlled_list=lst.name,
                        graph=node.graph.name,
                        node=node.name,
                    )
                ),
                status=400,
            )
        objs_deleted, unused = ControlledList.objects.filter(pk=list_id).delete()
        if not objs_deleted:
            return JSONErrorResponse(status=404)
        return JSONResponse(status=204)


@method_decorator(
    group_required("RDM Administrator", raise_exception=True), name="dispatch"
)
class ControlledListItemView(View):
    def add_new_item(self, request):
        data = JSONDeserializer().deserialize(request.body)
        parent_id = data["parent_id"]

        # The front end shows lists and items in the same tree, and when
        # sending the parent id to the endpoint, it doesn't really know
        # if the parent is a list or an item. The backend does care whether
        # the parent is a list or an item, so we figure it out here.
        try:
            controlled_list_id = ControlledListItem.objects.get(
                pk=parent_id
            ).controlled_list_id
        except ControlledListItem.DoesNotExist:
            controlled_list_id = parent_id

        try:
            with transaction.atomic():
                controlled_list = (
                    ControlledList.objects.filter(pk=controlled_list_id)
                    .annotate(
                        max_sortorder=Max(
                            "controlled_list_items__sortorder", default=-1
                        )
                    )
                    .get()
                )
                item = ControlledListItem.objects.create(
                    controlled_list=controlled_list,
                    sortorder=controlled_list.max_sortorder + 1,
                    parent_id=None if controlled_list_id == parent_id else parent_id,
                )
                ControlledListItemLabel.objects.create(
                    controlled_list_item=item,
                    value=_("New Item: ") + datetime.now().isoformat(),
                    value_type_id="prefLabel",
                    language_id=get_language(),
                )
        except ControlledList.DoesNotExist:
            return JSONErrorResponse(status=404)
        except Exception as e:
            logger.error(e)
            return JSONErrorResponse()

        return JSONResponse(serialize(item))

    def post(self, request, **kwargs):
        if not (item_id := kwargs.get("id", None)):
            return self.add_new_item(request)

        # Update list item
        data = JSONDeserializer().deserialize(request.body)

        try:
            with transaction.atomic():
                for item in ControlledListItem.objects.filter(
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

        return JSONResponse(serialize(item))

    def delete(self, request, **kwargs):
        item_id = kwargs.get("id")
        objs_deleted, unused = ControlledListItem.objects.filter(pk=item_id).delete()
        if not objs_deleted:
            return JSONErrorResponse(status=404)
        return JSONResponse(status=204)


@method_decorator(
    group_required("RDM Administrator", raise_exception=True), name="dispatch"
)
class ControlledListItemLabelView(View):
    def add_new_label(self, request):
        data = JSONDeserializer().deserialize(request.body)

        label = ControlledListItemLabel(
            controlled_list_item_id=data["item_id"],
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
        try:
            label = ControlledListItemLabel.objects.get(pk=label_id)
        except:
            return JSONErrorResponse(status=404)
        if (
            label.value_type_id == "prefLabel"
            and len(
                label.controlled_list_item.controlled_list_item_labels.filter(
                    value_type="prefLabel"
                )
            )
            < 2
        ):
            return JSONErrorResponse(
                message=_(
                    "Deleting the item's only remaining preferred label is not permitted."
                ),
                status=400,
            )
        label.delete()
        return JSONResponse(status=204)
