# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "10710_fix_whatisthis"),
    ]

    sql = """
        UPDATE search_component SET sortorder = sortorder + 1;
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
            'Core Search',
            '',
            'core_search.py.py',
            'CoreSearchFilter',
            'backend',
            'views/components/search/core-search',
            'core-search',
            0,
            true,
            '{"requiredComponents":[{"componentname":"localize-descriptors","searchcomponentid":"ada062d9-092d-400c-bcf7-94a931d1f271"}]}'
        ),
        (
            'ada062d9-092d-400c-bcf7-94a931d1f271',
            'Localize Result Descriptors',
            '',
            'localize_result_descriptors.py',
            'LocalizeResultDescriptors',
            'backend',
            'views/components/search/localize-descriptors',
            'localize-descriptors',
            99,
            true,
            '{"requiredComponents":[{"componentname":"core-search","searchcomponentid":"69695d63-6f03-4536-8da9-841b07116381"}]}'
        );
        UPDATE search_component SET config = '{"requiredComponents":[{"componentname":"core-search","searchcomponentid":"69695d63-6f03-4536-8da9-841b07116381"},{"componentname":"term-filter","searchcomponentid":"1f42f501-ed70-48c5-bae1-6ff7d0d187da"}]}' WHERE componentname = 'provisional-filter';
        UPDATE search_component SET config = '{"requiredComponents":[{"componentname":"core-search","searchcomponentid":"69695d63-6f03-4536-8da9-841b07116381"},{"componentname":"search-results","searchcomponentid":"00673743-8c1c-4cc0-bd85-c073a52e03ec"}]}' WHERE componentname = 'related-resources-filter';
        UPDATE search_component SET config = '{"requiredComponents":[{"componentname":"core-search","searchcomponentid":"69695d63-6f03-4536-8da9-841b07116381"},{"componentname":"term-filter","searchcomponentid":"1f42f501-ed70-48c5-bae1-6ff7d0d187da"}]}' WHERE componentname = 'resource-type-filter';
        UPDATE search_component SET config = '{"requiredComponents":[{"componentname":"core-search","searchcomponentid":"69695d63-6f03-4536-8da9-841b07116381"},{"componentname":"search-results","searchcomponentid":"00673743-8c1c-4cc0-bd85-c073a52e03ec"}]}' WHERE componentname = 'search-result-details';
        UPDATE search_component SET config = '{"requiredComponents":[{"componentname":"core-search","searchcomponentid":"69695d63-6f03-4536-8da9-841b07116381"},{"componentname":"map-filter","searchcomponentid":"09d97fc6-8c83-4319-9cef-3aaa08c3fbec"}]}' WHERE componentname = 'search-results';
    """
    reverse_sql = """
        delete from search_component where searchcomponentid in (
            '69695d63-6f03-4536-8da9-841b07116381',
            'ada062d9-092d-400c-bcf7-94a931d1f271'
        );
        update search_component set sortorder = sortorder - 1 where sortorder > 0;
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
    ]
