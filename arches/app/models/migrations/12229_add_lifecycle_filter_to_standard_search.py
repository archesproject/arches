# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations


def update_standard_search_view_config(apps, schema_editor):
    SearchComponent = apps.get_model("models", "SearchComponent")

    standard_search_component = SearchComponent.objects.get(
        searchcomponentid="69695d63-6f03-4536-8da9-841b07116381"
    )

    standard_search_component.config = {
        "default": True,
        "linkedSearchFilters": [
            {
                "componentname": "paging-filter",
                "searchcomponentid": "7aff5819-651c-4390-9b9a-a61221ba52c6",
                "layoutSortorder": 1,
                "required": True,
                "executionSortorder": 2,
            },
            {
                "componentname": "search-results",
                "searchcomponentid": "00673743-8c1c-4cc0-bd85-c073a52e03ec",
                "layoutSortorder": 2,
            },
            {
                "componentname": "map-filter",
                "searchcomponentid": "09d97fc6-8c83-4319-9cef-3aaa08c3fbec",
                "layoutSortorder": 1,
            },
            {
                "componentname": "advanced-search",
                "searchcomponentid": "f0e56205-acb5-475b-9c98-f5e44f1dbd2c",
                "layoutSortorder": 2,
            },
            {
                "componentname": "related-resources-filter",
                "searchcomponentid": "59f28272-d1f1-4805-af51-227771739aed",
                "layoutSortorder": 3,
            },
            {
                "componentname": "provisional-filter",
                "searchcomponentid": "073406ed-93e5-4b5b-9418-b61c26b3640f",
                "layoutSortorder": 4,
            },
            {
                "componentname": "resource-type-filter",
                "searchcomponentid": "f1c46b7d-0132-421b-b1f3-95d67f9b3980",
                "layoutSortorder": 5,
            },
            {
                "componentname": "lifecycle-state-filter",
                "searchcomponentid": "9e40969b-78c2-40b8-898b-c29265050e2f",
                "layoutSortorder": 6,
            },
            {
                "componentname": "saved-searches",
                "searchcomponentid": "6dc29637-43a1-4fba-adae-8d9956dcd3b9",
                "layoutSortorder": 7,
            },
            {
                "componentname": "search-export",
                "searchcomponentid": "9c6a5a9c-a7ec-48d2-8a25-501b55b8eff6",
                "layoutSortorder": 8,
            },
            {
                "componentname": "search-result-details",
                "searchcomponentid": "f5986dae-8b01-11ea-b65a-77903936669c",
                "layoutSortorder": 9,
            },
            {
                "componentname": "sort-results",
                "searchcomponentid": "6a2fe122-de54-4e44-8e93-b6a0cda7955c",
                "layoutSortorder": 10,
            },
            {
                "componentname": "term-filter",
                "searchcomponentid": "1f42f501-ed70-48c5-bae1-6ff7d0d187da",
                "layoutSortorder": 11,
            },
            {
                "componentname": "time-filter",
                "searchcomponentid": "7497ed4f-2085-40da-bee5-52076a48bcb1",
                "layoutSortorder": 12,
            },
            {
                "componentname": "paging-filter",
                "searchcomponentid": "7aff5819-651c-4390-9b9a-a61221ba52c6",
                "layoutSortorder": 13,
            },
            {
                "componentname": "search-results",
                "searchcomponentid": "00673743-8c1c-4cc0-bd85-c073a52e03ec",
                "layoutSortorder": 14,
                "required": True,
                "executionSortorder": 1,
            },
        ],
    }
    standard_search_component.save()


def revert_standard_search_view_config(apps, schema_editor):
    SearchComponent = apps.get_model("models", "SearchComponent")

    try:
        standard_search_component = SearchComponent.objects.get(
            searchcomponentid="69695d63-6f03-4536-8da9-841b07116381"
        )
    except SearchComponent.DoesNotExist:
        return

    standard_search_component.config = {
        "default": True,
        "linkedSearchFilters": [
            {
                "componentname": "map-filter",
                "searchcomponentid": "09d97fc6-8c83-4319-9cef-3aaa08c3fbec",
                "layoutSortorder": 1,
            },
            {
                "componentname": "advanced-search",
                "searchcomponentid": "f0e56205-acb5-475b-9c98-f5e44f1dbd2c",
                "layoutSortorder": 2,
            },
            {
                "componentname": "related-resources-filter",
                "searchcomponentid": "59f28272-d1f1-4805-af51-227771739aed",
                "layoutSortorder": 3,
            },
            {
                "componentname": "provisional-filter",
                "searchcomponentid": "073406ed-93e5-4b5b-9418-b61c26b3640f",
                "layoutSortorder": 4,
            },
            {
                "componentname": "resource-type-filter",
                "searchcomponentid": "f1c46b7d-0132-421b-b1f3-95d67f9b3980",
                "layoutSortorder": 5,
            },
            {
                "componentname": "saved-searches",
                "searchcomponentid": "6dc29637-43a1-4fba-adae-8d9956dcd3b9",
                "layoutSortorder": 6,
            },
            {
                "componentname": "search-export",
                "searchcomponentid": "9c6a5a9c-a7ec-48d2-8a25-501b55b8eff6",
                "layoutSortorder": 7,
            },
            {
                "componentname": "search-result-details",
                "searchcomponentid": "f5986dae-8b01-11ea-b65a-77903936669c",
                "layoutSortorder": 8,
            },
            {
                "componentname": "sort-results",
                "searchcomponentid": "6a2fe122-de54-4e44-8e93-b6a0cda7955c",
                "layoutSortorder": 9,
            },
            {
                "componentname": "term-filter",
                "searchcomponentid": "1f42f501-ed70-48c5-bae1-6ff7d0d187da",
                "layoutSortorder": 10,
            },
            {
                "componentname": "time-filter",
                "searchcomponentid": "7497ed4f-2085-40da-bee5-52076a48bcb1",
                "layoutSortorder": 11,
            },
            {
                "componentname": "paging-filter",
                "searchcomponentid": "7aff5819-651c-4390-9b9a-a61221ba52c6",
                "required": True,
                "layoutSortorder": 12,
                "executionSortorder": 2,
            },
            {
                "componentname": "search-results",
                "searchcomponentid": "00673743-8c1c-4cc0-bd85-c073a52e03ec",
                "required": True,
                "layoutSortorder": 13,
                "executionSortorder": 1,
            },
        ],
    }
    standard_search_component.save()


class Migration(migrations.Migration):

    dependencies = [
        ("models", "7853_add_timestamp_index"),
    ]

    operations = [
        migrations.RunPython(
            update_standard_search_view_config, revert_standard_search_view_config
        ),
    ]
