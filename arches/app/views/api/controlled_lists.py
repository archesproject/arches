import logging
from http import HTTPStatus
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _

from arches.app.models.models import (
    ControlledList,
    ControlledListItem,
    ControlledListItemImage,
    ControlledListItemImageMetadata,
    ControlledListItemValue,
    Language,
    Node,
)
from arches.app.models.utils import field_names
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.decorators import group_required
from arches.app.utils.permission_backend import get_nodegroups_by_perm
from arches.app.utils.response import JSONErrorResponse, JSONResponse
from arches.app.utils.string_utils import str_to_bool

logger = logging.getLogger(__name__)


def _prefetch_terms(request):
    """Children at arbitrary depth will still be returned, but tell
    the ORM to prefetch a certain depth to mitigate N+1 queries after."""
    find_children = not str_to_bool(request.GET.get("flat", "false"))

    # Raising the prefetch depth will only save queries, never cause more.
    # Might add slight python overhead? ~12-14 is enough for Getty AAT.
    prefetch_depth = 14

    terms = []
    for i in range(prefetch_depth):
        if i == 0:
            terms.extend(
                [
                    "controlled_list_items",
                    "controlled_list_items__controlled_list_item_values",
                    "controlled_list_items__controlled_list_item_images",
                    "controlled_list_items__controlled_list_item_images__controlled_list_item_image_metadata",
                ]
            )
        elif find_children:
            terms.extend(
                [
                    f"controlled_list_items{'__children' * i}",
                    f"controlled_list_items{'__children' * i}__controlled_list_item_values",
                    f"controlled_list_items{'__children' * i}__controlled_list_item_images",
                    f"controlled_list_items{'__children' * i}__controlled_list_item_images__controlled_list_item_image_metadata",
                ]
            )
    return terms


@method_decorator(
    group_required("RDM Administrator", raise_exception=True), name="dispatch"
)
class ControlledListsView(View):
    def get(self, request):
        """Returns either a flat representation (?flat=true) or a tree (default)."""
        lists = (
            ControlledList.objects.annotate_node_fields(
                node_ids="pk",
                node_names="name",
                nodegroup_ids="nodegroup_id",
                graph_ids="graph_id",
                graph_names="graph__name",
            )
            .order_by("name")
            .prefetch_related(*_prefetch_terms(request))
        )

        flat = str_to_bool(request.GET.get("flat", "false"))
        permitted = [
            ng.pk for ng in get_nodegroups_by_perm(request.user, "read_nodegroup")
        ]
        serialized = [
            obj.serialize(flat=flat, permitted_nodegroups=permitted) for obj in lists
        ]

        return JSONResponse({"controlled_lists": serialized})


@method_decorator(
    group_required("RDM Administrator", raise_exception=True), name="dispatch"
)
class ControlledListView(View):
    def get(self, request, **kwargs):
        """Returns either a flat representation (?flat=true) or a tree (default)."""
        list_id = kwargs.get("id")
        try:
            lst = ControlledList.objects.prefetch_related(
                *_prefetch_terms(request)
            ).get(pk=list_id)
        except ControlledList.DoesNotExist:
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)

        flat = str_to_bool(request.GET.get("flat", "false"))
        permitted = [
            ng.pk for ng in get_nodegroups_by_perm(request.user, "read_nodegroup")
        ]
        serialized = lst.serialize(flat=flat, permitted_nodegroups=permitted)

        return JSONResponse(serialized)

    def add_new_list(self, name):
        lst = ControlledList(name=name)
        try:
            lst.full_clean()  # applies default name
        except ValidationError as ve:
            return JSONErrorResponse(
                message="\n".join(ve.messages), status=HTTPStatus.BAD_REQUEST
            )
        lst.save()
        return JSONResponse(lst.serialize(), status=HTTPStatus.CREATED)

    def post(self, request, **kwargs):
        data = JSONDeserializer().deserialize(request.body)
        name = data.get("name", None)
        if "id" not in kwargs:
            return self.add_new_list(name)

        raise NotImplementedError

    def patch(self, request, **kwargs):
        list_id: UUID = kwargs.get("id")
        data = JSONDeserializer().deserialize(request.body)
        data.pop("items", None)
        sortorder_map = data.pop("sortorder_map", {})
        parent_map = data.pop("parent_map", {})

        update_fields = list(data)
        if not update_fields and not sortorder_map:
            return JSONResponse(status=HTTPStatus.BAD_REQUEST)

        clist = ControlledList(id=list_id, **data)

        exclude_fields = {f for f in field_names(clist) if f not in update_fields}
        try:
            clist._state.adding = False
            clist.full_clean(exclude=exclude_fields)
        except ValidationError as ve:
            return JSONErrorResponse(
                message="\n".join(ve.messages), status=HTTPStatus.BAD_REQUEST
            )

        clist.save(update_fields=update_fields)

        if sortorder_map:
            clist.bulk_update_item_parentage_and_order(parent_map, sortorder_map)

        return JSONResponse(status=HTTPStatus.NO_CONTENT)

    def delete(self, request, **kwargs):
        try:
            list_to_delete = ControlledList.objects.get(pk=kwargs.get("id"))
        except ControlledList.DoesNotExist:
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)

        nodes_using_list = Node.objects.with_controlled_lists().filter(
            controlled_list_id=list_to_delete.pk
        )
        errors = [
            _(
                "{controlled_list} could not be deleted: still in use by {graph} - {node}".format(
                    controlled_list=list_to_delete.name,
                    graph=node.graph.name,
                    node=node.name,
                )
            )
            for node in nodes_using_list
        ]
        if errors:
            return JSONErrorResponse(
                message="\n".join(errors), status=HTTPStatus.BAD_REQUEST
            )
        list_to_delete.delete()
        return JSONResponse(status=HTTPStatus.NO_CONTENT)


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
        except ControlledList.DoesNotExist:
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)

        return JSONResponse(item.serialize(), status=HTTPStatus.CREATED)

    def post(self, request, **kwargs):
        if "id" not in kwargs:
            return self.add_new_item(request)

        raise NotImplementedError

    def patch(self, request, **kwargs):
        item_id: UUID = kwargs.get("id")
        data = JSONDeserializer().deserialize(request.body)
        item = ControlledListItem(id=item_id, **data)

        update_fields = list(data)
        if not update_fields:
            return JSONErrorResponse(status=HTTPStatus.BAD_REQUEST)
        exclude_fields = {f for f in field_names(item) if f not in update_fields}
        try:
            item._state.adding = False
            item.full_clean(exclude=exclude_fields)
            with transaction.atomic():
                item.save(update_fields=update_fields)
                if "parent_id" in update_fields:
                    # Check for recursive structure
                    unused = item.parent.serialize()
        except RecursionError:
            return JSONErrorResponse(
                message=_("Recursive structure detected."),
                status=HTTPStatus.BAD_REQUEST,
            )
        except ValidationError as ve:
            return JSONErrorResponse(
                message="\n".join(ve.messages), status=HTTPStatus.BAD_REQUEST
            )

        return JSONResponse(status=HTTPStatus.NO_CONTENT)

    def delete(self, request, **kwargs):
        item_id: UUID = kwargs.get("id")
        objs_deleted, unused = ControlledListItem.objects.filter(pk=item_id).delete()
        if not objs_deleted:
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)
        return JSONResponse(status=HTTPStatus.NO_CONTENT)


@method_decorator(
    group_required("RDM Administrator", raise_exception=True), name="dispatch"
)
class ControlledListItemValueView(View):
    def add_new_value(self, request):
        data = JSONDeserializer().deserialize(request.body)

        value = ControlledListItemValue(
            controlled_list_item_id=UUID(data["item_id"]),
            valuetype_id=data["valuetype_id"],
            language_id=data["language_id"],
            value=data["value"],
        )
        try:
            value.full_clean()
        except ValidationError as ve:
            return JSONErrorResponse(
                message="\n".join(ve.messages), status=HTTPStatus.BAD_REQUEST
            )
        value.save()

        return JSONResponse(value.serialize(), status=HTTPStatus.CREATED)

    def post(self, request, **kwargs):
        if not (value_id := kwargs.get("id", None)):
            return self.add_new_value(request)

        data = JSONDeserializer().deserialize(request.body)

        try:
            value = ControlledListItemValue.objects.values_without_images().get(
                pk=value_id
            )
        except ControlledListItemValue.DoesNotExist:
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)

        value.value = data["value"]
        value.valuetype_id = data["valuetype_id"]
        try:
            value.language = Language.objects.get(code=data["language_id"])
        except Language.DoesNotExist:
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)

        try:
            value.full_clean()
        except ValidationError as ve:
            return JSONErrorResponse(
                message="\n".join(ve.messages), status=HTTPStatus.BAD_REQUEST
            )
        value.save()

        return JSONResponse(value.serialize())

    def delete(self, request, **kwargs):
        value_id = kwargs.get("id")
        try:
            value = ControlledListItemValue.objects.values_without_images().get(
                pk=value_id
            )
        except:
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)

        try:
            value.delete()
        except ValidationError as ve:
            return JSONErrorResponse(
                message="\n".join(ve.messages), status=HTTPStatus.BAD_REQUEST
            )
        return JSONResponse(status=HTTPStatus.NO_CONTENT)


@method_decorator(
    group_required("RDM Administrator", raise_exception=True), name="dispatch"
)
class ControlledListItemImageView(View):
    def add_new_image(self, request):
        uploaded_file = request.FILES["item_image"]
        img = ControlledListItemImage(
            controlled_list_item_id=UUID(request.POST["item_id"]),
            valuetype_id="image",
            value=uploaded_file,
        )
        try:
            img.full_clean()
        except ValidationError as ve:
            return JSONErrorResponse(
                message="\n".join(ve.messages), status=HTTPStatus.BAD_REQUEST
            )
        img.save()
        return JSONResponse(img.serialize(), status=HTTPStatus.CREATED)

    def post(self, request, **kwargs):
        if not (image_id := kwargs.get("id", None)):
            return self.add_new_image(request)
        raise NotImplementedError

    def delete(self, request, **kwargs):
        image_id = kwargs.get("id")
        count, unused = ControlledListItemImage.objects.filter(pk=image_id).delete()
        if not count:
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)
        return JSONResponse(status=HTTPStatus.NO_CONTENT)


@method_decorator(
    group_required("RDM Administrator", raise_exception=True), name="dispatch"
)
class ControlledListItemImageMetadataView(View):
    def add_new_metadata(self, request):
        data = JSONDeserializer().deserialize(request.body)
        data.pop("metadata_label", None)
        metadata = ControlledListItemImageMetadata(**data)
        try:
            metadata.full_clean()
        except ValidationError as ve:
            return JSONErrorResponse(
                message="\n".join(ve.messages), status=HTTPStatus.BAD_REQUEST
            )
        metadata.save()

        return JSONResponse(metadata.serialize(), status=HTTPStatus.CREATED)

    def post(self, request, **kwargs):
        if not (metadata_id := kwargs.get("id", None)):
            return self.add_new_metadata(request)

        data = JSONDeserializer().deserialize(request.body)

        try:
            metadata = ControlledListItemImageMetadata.objects.get(pk=metadata_id)
        except ControlledListItemImageMetadata.DoesNotExist:
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)

        metadata.value = data["value"]
        try:
            metadata.language = Language.objects.get(code=data["language_id"])
        except Language.DoesNotExist:
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)
        metadata.metadata_type = data["metadata_type"]

        try:
            metadata.full_clean()
        except ValidationError as ve:
            return JSONErrorResponse(
                message="\n".join(ve.messages), status=HTTPStatus.BAD_REQUEST
            )
        metadata.save()

        return JSONResponse(metadata.serialize())

    def delete(self, request, **kwargs):
        metadata_id = kwargs.get("id")
        count, unused = ControlledListItemImageMetadata.objects.filter(
            pk=metadata_id
        ).delete()
        if not count:
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)
        return JSONResponse(status=HTTPStatus.NO_CONTENT)
