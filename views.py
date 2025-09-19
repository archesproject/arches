from http import HTTPStatus
from uuid import UUID
import filetype
import json

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max
from django.db.utils import IntegrityError
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _

from arches.app.models.utils import field_names
from arches.app.utils.betterJSONSerializer import JSONDeserializer
from arches.app.utils.decorators import group_required
from arches.app.utils.permission_backend import get_nodegroups_by_perm
from arches.app.utils.response import JSONErrorResponse, JSONResponse
from arches.app.utils.string_utils import str_to_bool
from arches.app.views.api import APIBase
from arches_controlled_lists.models import (
    List,
    ListItem,
    ListItemImage,
    ListItemImageMetadata,
    ListItemValue,
    NodeProxy,
)
from arches_controlled_lists.utils.skos import SKOSReader, SKOSWriter


def _prefetch_terms(request):
    """Children at arbitrary depth will still be returned, but tell
    the ORM to prefetch a certain depth to mitigate N+1 queries after."""
    flat = str_to_bool(request.GET.get("flat", "false"))

    # Raising the prefetch depth will only save queries, never cause more.
    # Might add slight python overhead? ~12-14 is enough for Getty AAT.
    # https://forum.djangoproject.com/t/prefetching-relations-to-arbitrary-depth/39328
    prefetch_depth = 1 if flat else 14

    terms = []
    for i in range(prefetch_depth):
        terms.extend(
            [
                f"list_items{'__children' * i}",
                f"list_items{'__children' * i}__list_item_values",
                f"list_items{'__children' * i}__list_item_images",
                f"list_items{'__children' * i}__list_item_images__list_item_image_metadata",
            ]
        )
    return terms


class ListsView(APIBase):
    def get(self, request):
        """Returns either a flat representation (?flat=true) or a tree (default)."""
        lists = (
            List.objects.annotate_node_fields(
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
        permitted = get_nodegroups_by_perm(request.user, "read_nodegroup")
        serialized = [
            obj.serialize(flat=flat, permitted_nodegroups=permitted) for obj in lists
        ]

        return JSONResponse({"controlled_lists": serialized})


class ListView(APIBase):
    def get(self, request, list_id):
        """Returns either a flat representation (?flat=true) or a tree (default)."""
        try:
            lst = List.objects.prefetch_related(*_prefetch_terms(request)).get(
                pk=list_id
            )
        except List.DoesNotExist:
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)

        flat = str_to_bool(request.GET.get("flat", "false"))
        permitted = get_nodegroups_by_perm(request.user, "read_nodegroup")
        serialized = lst.serialize(flat=flat, permitted_nodegroups=permitted)

        return JSONResponse(serialized)

    @method_decorator(
        group_required("RDM Administrator", raise_exception=True), name="dispatch"
    )
    def post(self, request):
        skosfile = request.FILES.get("skosfile", None)
        overwrite_option = request.POST.get("overwrite_option", None)
        if skosfile and overwrite_option:
            try:
                # Do minimal file validation to mock file checking in FileValidator
                extension = skosfile.name.split(".")[-1]
                guessed_file_type = filetype.guess(skosfile)

                # guessed_file_type will be None if the file is xml
                if extension != "xml" or guessed_file_type is not None:
                    return JSONErrorResponse(
                        message=(
                            f"File extension {extension}/{guessed_file_type.extension} not allowed"
                        ),
                        status=HTTPStatus.BAD_REQUEST,
                    )

                skos = SKOSReader()
                rdf = skos.read_file(skosfile)
                concepts = skos.save_controlled_lists_from_skos(
                    rdf, overwrite_options=overwrite_option
                )
            # Wide catch is because Arches SKOSReader raises generic Exceptions
            except Exception as error:
                return JSONErrorResponse(
                    message=(str(error)), status=HTTPStatus.BAD_REQUEST
                )
            return JSONResponse(concepts, status=HTTPStatus.OK)

        else:
            data = JSONDeserializer().deserialize(request.body)
            lst = List(name=data.get("name", None))
            try:
                lst.full_clean()  # applies default name
            except ValidationError as ve:
                return JSONErrorResponse(
                    message="\n".join(ve.messages), status=HTTPStatus.BAD_REQUEST
                )
            lst.save()
            return JSONResponse(lst.serialize(), status=HTTPStatus.CREATED)

    @method_decorator(
        group_required("RDM Administrator", raise_exception=True), name="dispatch"
    )
    def patch(self, request, list_id):
        data = JSONDeserializer().deserialize(request.body)
        data.pop("items", None)
        sortorder_map = data.pop("sortorder_map", {})
        parent_map = data.pop("parent_map", {})

        update_fields = set(data)
        if not update_fields and not sortorder_map:
            return JSONResponse(status=HTTPStatus.BAD_REQUEST)

        try:
            clist = List.objects.get(pk=list_id)
        except List.DoesNotExist:
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)
        for key, value in data.items():
            setattr(clist, key, value)

        exclude_fields = field_names(clist) - update_fields
        try:
            clist.full_clean(exclude=exclude_fields)
        except ValidationError as ve:
            return JSONErrorResponse(
                message="\n".join(ve.messages), status=HTTPStatus.BAD_REQUEST
            )

        clist.save(update_fields=update_fields)

        if sortorder_map:
            clist.bulk_update_item_parentage_and_order(parent_map, sortorder_map)

        return JSONResponse(status=HTTPStatus.NO_CONTENT)

    @method_decorator(
        group_required("RDM Administrator", raise_exception=True), name="dispatch"
    )
    def delete(self, request, list_id):
        try:
            list_to_delete = List.objects.get(pk=list_id)
        except List.DoesNotExist:
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)

        nodes_using_list = NodeProxy.objects.with_controlled_lists().filter(
            controlled_list_id=list_to_delete.pk
        )
        errors = [
            _(
                "{controlled_list} could not be deleted: still in use by {graph} - {node}"
            ).format(
                controlled_list=list_to_delete.name,
                graph=node.graph.name,
                node=node.name,
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
class ListExportView(APIBase):
    def post(self, request):
        list_ids = json.loads(request.body).get("list_ids", [])
        try:
            export_lists = List.objects.filter(pk__in=list_ids)
            export_list_items = ListItem.objects.filter(
                list__in=export_lists
            ).prefetch_related("list_item_values", "parent", "children")
        except List.DoesNotExist:
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)

        if len(export_lists) != 0:
            skos = SKOSWriter()
            rdf = skos.write_controlled_lists(
                export_lists, export_list_items, format="pretty-xml"
            )

            response = JSONResponse(rdf, status=HTTPStatus.OK)
            response["Content-Type"] = "application/xml"
            response["Content-Disposition"] = (
                f'attachment; filename="{export_lists[0].name}.xml"'
            )
            return response
        else:
            return JSONErrorResponse(
                message=_("No lists found to export."), status=HTTPStatus.BAD_REQUEST
            )


@method_decorator(
    group_required("RDM Administrator", raise_exception=True), name="dispatch"
)
class ListItemView(APIBase):
    def post(self, request):
        data = JSONDeserializer().deserialize(request.body)
        try:
            parent_id = data["parent_id"]
            list_id = data["list_id"]
        except KeyError:
            return JSONErrorResponse(status=HTTPStatus.BAD_REQUEST)

        try:
            controlled_list = List.objects.get(pk=list_id)
        except List.DoesNotExist:
            return JSONErrorResponse(status=HTTPStatus.BAD_REQUEST)

        try:
            if parent_id:
                max_existing_sort = ListItem.objects.filter(pk=parent_id).aggregate(
                    max=Max("children__sortorder", default=-1)
                )["max"]
            else:
                max_existing_sort = controlled_list.list_items.filter(
                    parent=None
                ).aggregate(max=Max("sortorder", default=-1))["max"]
            item = ListItem(
                list=controlled_list,
                parent_id=parent_id,
                sortorder=max_existing_sort + 1,
            )
            item.full_clean()
            item.save()
        except ValidationError as ve:
            return JSONErrorResponse(
                message="\n".join(ve.messages), status=HTTPStatus.BAD_REQUEST
            )

        return JSONResponse(item.serialize(), status=HTTPStatus.CREATED)

    def patch(self, request, item_id):
        data = JSONDeserializer().deserialize(request.body)
        try:
            item = ListItem.objects.get(pk=item_id)
        except ListItem.DoesNotExist:
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)
        for key, value in data.items():
            setattr(item, key, value)

        update_fields = set(data)
        if not update_fields:
            return JSONErrorResponse(status=HTTPStatus.BAD_REQUEST)
        exclude_fields = field_names(item) - update_fields
        try:
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

    def delete(self, request, item_id):
        objs_deleted, unused = ListItem.objects.filter(pk=item_id).delete()
        if not objs_deleted:
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)
        return JSONResponse(status=HTTPStatus.NO_CONTENT)


@method_decorator(
    group_required("RDM Administrator", raise_exception=True), name="dispatch"
)
class ListItemValueView(APIBase):
    def post(self, request):
        data = JSONDeserializer().deserialize(request.body)
        value = ListItemValue(**data)
        try:
            value.full_clean()
        except ValidationError as ve:
            return JSONErrorResponse(
                message="\n".join(ve.messages), status=HTTPStatus.BAD_REQUEST
            )
        value.save()

        return JSONResponse(value.serialize(), status=HTTPStatus.CREATED)

    def put(self, request, value_id):
        data = JSONDeserializer().deserialize(request.body)
        try:
            value = ListItemValue.objects.values_without_images().get(pk=value_id)
        except ListItemValue.DoesNotExist:
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)

        try:
            value.value = data["value"]
            value.valuetype_id = data["valuetype_id"]
            value.language_id = data["language_id"]
            value.full_clean()
        except ValidationError as ve:
            return JSONErrorResponse(
                message="\n".join(ve.messages), status=HTTPStatus.BAD_REQUEST
            )
        except KeyError:
            return JSONErrorResponse(status=HTTPStatus.BAD_REQUEST)
        value.save()

        return JSONResponse(value.serialize())

    def delete(self, request, value_id):
        try:
            value = ListItemValue.objects.values_without_images().get(pk=value_id)
        except ListItemValue.DoesNotExist:
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
class ListItemImageView(APIBase):
    def post(self, request):
        uploaded_file = request.FILES["item_image"]
        img = ListItemImage(
            list_item_id=UUID(request.POST["list_item_id"]),
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

    def delete(self, request, image_id):
        count, unused = ListItemImage.objects.filter(pk=image_id).delete()
        if not count:
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)
        return JSONResponse(status=HTTPStatus.NO_CONTENT)


@method_decorator(
    group_required("RDM Administrator", raise_exception=True), name="dispatch"
)
class ListItemImageMetadataView(APIBase):
    def post(self, request):
        data = JSONDeserializer().deserialize(request.body)
        data.pop("metadata_label", None)
        metadata = ListItemImageMetadata(**data)
        try:
            metadata.full_clean()
        except ValidationError as ve:
            return JSONErrorResponse(
                message="\n".join(ve.messages), status=HTTPStatus.BAD_REQUEST
            )
        metadata.save()
        return JSONResponse(metadata.serialize(), status=HTTPStatus.CREATED)

    def put(self, request, metadata_id):
        data = JSONDeserializer().deserialize(request.body)
        try:
            metadata = ListItemImageMetadata.objects.get(pk=metadata_id)
        except ListItemImageMetadata.DoesNotExist:
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)

        try:
            metadata.value = data["value"]
            metadata.language_id = data["language_id"]
            metadata.metadata_type = data["metadata_type"]
            metadata.full_clean()
        except ValidationError as ve:
            return JSONErrorResponse(
                message="\n".join(ve.messages), status=HTTPStatus.BAD_REQUEST
            )
        except KeyError:
            return JSONErrorResponse(status=HTTPStatus.BAD_REQUEST)
        metadata.save()

        return JSONResponse(metadata.serialize())

    def delete(self, request, metadata_id):
        count, unused = ListItemImageMetadata.objects.filter(pk=metadata_id).delete()
        if not count:
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)
        return JSONResponse(status=HTTPStatus.NO_CONTENT)


class ListOptionsView(APIBase):
    def get(self, request):
        node_alias = request.GET.get("node_alias")
        graph_slug = request.GET.get("graph_slug")

        controlled_list_id = (
            NodeProxy.objects.filter(
                alias=node_alias, graph__slug=graph_slug, source_identifier=None
            )
            .with_controlled_lists()
            .values("controlled_list_id")[:1]
        )

        list_items = ListItem.objects.filter(
            list_id=controlled_list_id
        ).with_list_item_labels()
        serialized = [
            item.build_select_option() for item in list_items if item.parent_id is None
        ]
        return JSONResponse(serialized)


class ListItemCopyView(APIBase):
    @method_decorator(
        group_required("RDM Administrator", raise_exception=True), name="dispatch"
    )
    def post(self, request, item_id):
        data = JSONDeserializer().deserialize(request.body)
        try:
            target_list_id = data["target_list_id"]
            target_item_id = data.get("target_item_id", None)
            copy_children = data.get("copy_children", False)
        except KeyError:
            return JSONErrorResponse(status=HTTPStatus.BAD_REQUEST)

        try:
            item_to_copy = ListItem.objects.get(pk=item_id)
            if target_item_id:
                parent = ListItem.objects.get(id=target_item_id)
            else:
                parent = List.objects.get(id=target_list_id)
        except (ListItem.DoesNotExist, List.DoesNotExist):
            return JSONErrorResponse(status=HTTPStatus.NOT_FOUND)

        new_children, new_children_values = item_to_copy.duplicate_under_new_parent(
            [parent], include_children=copy_children, force_sortorder=True
        )
        try:
            with transaction.atomic():
                ListItem.objects.bulk_create(new_children)
                ListItemValue.objects.bulk_create(new_children_values)
        except IntegrityError:
            return JSONErrorResponse(
                message=(
                    f"Copy disallowed: duplicates URI ({item_to_copy.uri}) in list."
                ),
                status=HTTPStatus.BAD_REQUEST,
            )

        return JSONResponse(
            {"copied_list_item": new_children[0]}, status=HTTPStatus.CREATED
        )
