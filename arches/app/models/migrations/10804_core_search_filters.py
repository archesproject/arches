# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "10999_update_principaluser"),
    ]

    sql = """
        INSERT INTO search_component (
            searchcomponentid,
            name,
            icon,
            modulename,
            classname,
            type,
            componentpath,
            componentname,
            sortorder,
            enabled,
            config
        ) VALUES (
            '69695d63-6f03-4536-8da9-841b07116381',
            'Arches Core Search',
            '',
            'arches_core_search.py',
            'ArchesCoreSearch',
            'core',
            'views/components/search/arches-core-search',
            'arches-core-search',
            0,
            true,
            '{"default":true,"requiredComponents":[{"componentname":"map-filter","searchcomponentid":"09d97fc6-8c83-4319-9cef-3aaa08c3fbec","sortorder":1},{"componentname":"advanced-search","searchcomponentid":"f0e56205-acb5-475b-9c98-f5e44f1dbd2c","sortorder":2},{"componentname":"related-resources-filter","searchcomponentid":"59f28272-d1f1-4805-af51-227771739aed","sortorder":3},{"componentname":"provisional-filter","searchcomponentid":"073406ed-93e5-4b5b-9418-b61c26b3640f","sortorder":4},{"componentname":"resource-type-filter","searchcomponentid":"f1c46b7d-0132-421b-b1f3-95d67f9b3980","sortorder":5},{"componentname":"saved-searches","searchcomponentid":"6dc29637-43a1-4fba-adae-8d9956dcd3b9","sortorder":6},{"componentname":"search-export","searchcomponentid":"9c6a5a9c-a7ec-48d2-8a25-501b55b8eff6","sortorder":7},{"componentname":"search-result-details","searchcomponentid":"f5986dae-8b01-11ea-b65a-77903936669c","sortorder":8},{"componentname":"sort-results","searchcomponentid":"6a2fe122-de54-4e44-8e93-b6a0cda7955c","sortorder":9},{"componentname":"term-filter","searchcomponentid":"1f42f501-ed70-48c5-bae1-6ff7d0d187da","sortorder":10},{"componentname":"time-filter","searchcomponentid":"7497ed4f-2085-40da-bee5-52076a48bcb1","sortorder":11},{"componentname":"paging-filter","searchcomponentid":"7aff5819-651c-4390-9b9a-a61221ba52c6","sortorder":12},{"componentname":"search-results","searchcomponentid":"00673743-8c1c-4cc0-bd85-c073a52e03ec","sortorder":13}]}'
        );
        UPDATE search_component SET config = '{"requiredComponents":[{"componentname":"term-filter","searchcomponentid":"1f42f501-ed70-48c5-bae1-6ff7d0d187da","sortorder":1}]}' WHERE componentname = 'provisional-filter';
        UPDATE search_component SET config = '{"requiredComponents":[{"componentname":"search-results","searchcomponentid":"00673743-8c1c-4cc0-bd85-c073a52e03ec","sortorder":1}]}' WHERE componentname = 'related-resources-filter';
        UPDATE search_component SET config = '{"requiredComponents":[{"componentname":"term-filter","searchcomponentid":"1f42f501-ed70-48c5-bae1-6ff7d0d187da","sortorder":1}]}' WHERE componentname = 'resource-type-filter';
        UPDATE search_component SET config = '{"requiredComponents":[{"componentname":"search-results","searchcomponentid":"00673743-8c1c-4cc0-bd85-c073a52e03ec","sortorder":1}]}' WHERE componentname = 'search-result-details';
        UPDATE search_component SET config = '{"requiredComponents":[{"componentname":"map-filter","searchcomponentid":"09d97fc6-8c83-4319-9cef-3aaa08c3fbec","sortorder":1}]}' WHERE componentname = 'search-results';
    """
    reverse_sql = """
        delete from search_component where searchcomponentid = '69695d63-6f03-4536-8da9-841b07116381';
    """

    operations = [
        migrations.AddField(
            model_name="searchcomponent",
            name="config",
            field=models.JSONField(default=dict),
        ),
        migrations.RunSQL(
            sql,
            reverse_sql,
        ),
        migrations.RemoveField(
            model_name="searchcomponent",
            name="enabled",
        ),
        migrations.RemoveField(
            model_name="searchcomponent",
            name="sortorder",
        ),
    ]
