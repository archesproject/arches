from django.core.exceptions import ValidationError
from django.db.models import Prefetch

from arches.app.models.models import Value
from arches.app.utils.i18n import rank_label, get_language


def get_resource_relationship_type_label(relationship_types, lang=None):
    preflabel_lookup = {}
    if lang is None:
        lang = get_language()
    try:
        relationship_type_values = (
            Value.objects.filter(
                valueid__in=relationship_types,
            )
            .select_related("concept")
            .prefetch_related(
                Prefetch(
                    "concept__value_set",
                    queryset=Value.objects.order_by("pk"),
                ),
            )
        )
        preflabel_lookup = {
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
    except ValidationError:
        # If relationship_type is not a uuid, ie. ontology property
        pass

    return preflabel_lookup
