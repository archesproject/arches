from django.db.models import Prefetch

from arches.app.utils.string_utils import str_to_bool
from arches_controlled_lists.models import ListItem


def _prefetch_terms(request):
    """Children at arbitrary depth will still be returned, but tell
    the ORM to prefetch a certain depth to mitigate N+1 queries after.

    When ``?shallow=true`` is set, we only prefetch values/images for the
    root items (depth 1) and skip the deep ``children`` walk entirely. The
    ``list_items`` queryset itself is supplied separately via a ``Prefetch``
    object so we can attach ``annotate_has_children``.
    """
    flat = str_to_bool(request.GET.get("flat", "false"))
    shallow = str_to_bool(request.GET.get("shallow", "false"))

    if shallow:
        return [
            "list_items__list_item_values",
            "list_items__list_item_images",
            "list_items__list_item_images__list_item_image_metadata",
        ]

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


def _shallow_list_items_prefetch():
    """Returns a ``Prefetch`` that scopes the ``list_items`` relation to
    root items only and annotates each with ``has_children_annotated``. Used
    by the shallow path so the serializer never has to walk descendants."""
    return Prefetch(
        "list_items",
        queryset=ListItem.objects.filter(parent_id=None).annotate_has_children(),
    )
