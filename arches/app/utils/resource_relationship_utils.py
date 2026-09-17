import uuid
from collections import defaultdict

from django.apps import apps
from django.db.models import Prefetch, Q

from arches.app.models.models import Value
from arches.app.utils.i18n import rank_label, get_language


def _as_uuid(value):
    """Returns value as a UUID, or None if it isn't one."""
    try:
        return uuid.UUID(str(value))
    except (AttributeError, TypeError, ValueError):
        return None


def _get_concept_labels(relationship_types, lang):
    """Labels for relationship types stored as an RDM concept valueid."""
    valueid_lookup = {
        relationship_type: value_uuid
        for relationship_type in relationship_types
        if (value_uuid := _as_uuid(relationship_type))
    }
    if not valueid_lookup:
        return {}

    relationship_type_values = (
        Value.objects.filter(
            valueid__in=valueid_lookup.values(),
        )
        .select_related("concept")
        .prefetch_related(
            Prefetch(
                "concept__value_set",
                queryset=Value.objects.order_by("pk"),
            ),
        )
    )
    labels_by_valueid = {
        str(rel_type.pk): (
            sorted(
                rel_type.concept.value_set.all(),
                key=lambda label: rank_label(
                    kind=label.valuetype_id,
                    source_lang=label.language_id,
                    target_lang=lang,
                ),
                reverse=True,
            )[0].value
            if rel_type.concept.value_set.all()
            else ""
        )
        for rel_type in relationship_type_values
    }

    return {
        relationship_type: labels_by_valueid[str(value_uuid)]
        for relationship_type, value_uuid in valueid_lookup.items()
        if str(value_uuid) in labels_by_valueid
    }


def _get_list_item_labels(relationship_types, lang):
    """Labels for relationship types stored as a controlled list item, which the
    node config records as the item's uri (see utils/controlled-list.js). A uri is
    generated from PUBLIC_SERVER_ADDRESS or supplied by an import, so one stored in
    a node config can be stale or belong to another environment. Fall back to
    matching the item id, which is the trailing segment of a generated uri.

    Returns nothing when the arches_controlled_lists application isn't installed,
    the same soft dependency the frontend takes (see utils/controlled-list.js).
    """
    if not relationship_types or not apps.is_installed("arches_controlled_lists"):
        return {}

    # imported here because arches_controlled_lists imports from arches.app.models
    from arches_controlled_lists.models import ListItem

    relationship_types_by_item_id = defaultdict(list)
    for relationship_type in relationship_types:
        trailing_segment = str(relationship_type).rstrip("/").rsplit("/", 1)[-1]
        if item_id := _as_uuid(trailing_segment):
            relationship_types_by_item_id[str(item_id)].append(relationship_type)

    items = ListItem.objects.filter(
        Q(uri__in=relationship_types) | Q(pk__in=relationship_types_by_item_id)
    ).with_list_item_labels()

    preflabel_lookup = {}
    for item in items:
        label = item.find_best_label(language=lang)
        if not label:
            continue
        if item.uri in relationship_types:
            preflabel_lookup[item.uri] = label
        # the uri match above is the more precise one, so don't let an id match
        # overwrite it
        for relationship_type in relationship_types_by_item_id[str(item.pk)]:
            preflabel_lookup.setdefault(relationship_type, label)

    return preflabel_lookup


def get_resource_relationship_type_label(relationship_types, lang=None):
    """Maps each relationship type to its preferred label. A relationship type is
    an RDM concept valueid, a controlled list item uri, or an ontology property;
    only the first two have labels to look up, so ontology properties are absent
    from the returned lookup and callers fall back to the raw value.
    """
    if lang is None:
        lang = get_language()

    relationship_types = {
        str(relationship_type)
        for relationship_type in relationship_types
        if relationship_type
    }

    preflabel_lookup = _get_concept_labels(relationship_types, lang)
    preflabel_lookup.update(
        _get_list_item_labels(relationship_types - preflabel_lookup.keys(), lang)
    )

    return preflabel_lookup
