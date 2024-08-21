# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("models", "11179_file_and_geom_search"),
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
            'Standard Search View',
            '',
            'standard_search_view.py',
            'StandardSearchView',
            'search-view',
            'views/components/search/standard-search-view',
            'standard-search-view',
            0,
            true,
            '{"default":true,"linkedSearchFilters":[{"componentname":"map-filter","searchcomponentid":"09d97fc6-8c83-4319-9cef-3aaa08c3fbec","layoutSortorder":1},{"componentname":"advanced-search","searchcomponentid":"f0e56205-acb5-475b-9c98-f5e44f1dbd2c","layoutSortorder":2},{"componentname":"related-resources-filter","searchcomponentid":"59f28272-d1f1-4805-af51-227771739aed","layoutSortorder":3},{"componentname":"provisional-filter","searchcomponentid":"073406ed-93e5-4b5b-9418-b61c26b3640f","layoutSortorder":4},{"componentname":"resource-type-filter","searchcomponentid":"f1c46b7d-0132-421b-b1f3-95d67f9b3980","layoutSortorder":5},{"componentname":"saved-searches","searchcomponentid":"6dc29637-43a1-4fba-adae-8d9956dcd3b9","layoutSortorder":6},{"componentname":"search-export","searchcomponentid":"9c6a5a9c-a7ec-48d2-8a25-501b55b8eff6","layoutSortorder":7},{"componentname":"search-result-details","searchcomponentid":"f5986dae-8b01-11ea-b65a-77903936669c","layoutSortorder":8},{"componentname":"sort-results","searchcomponentid":"6a2fe122-de54-4e44-8e93-b6a0cda7955c","layoutSortorder":9},{"componentname":"term-filter","searchcomponentid":"1f42f501-ed70-48c5-bae1-6ff7d0d187da","layoutSortorder":10},{"componentname":"time-filter","searchcomponentid":"7497ed4f-2085-40da-bee5-52076a48bcb1","layoutSortorder":11},{"componentname":"paging-filter","searchcomponentid":"7aff5819-651c-4390-9b9a-a61221ba52c6","required":true,"layoutSortorder":12,"executionSortorder":2},{"componentname":"search-results","searchcomponentid":"00673743-8c1c-4cc0-bd85-c073a52e03ec","required":true,"layoutSortorder":13,"executionSortorder":1}]}'
        );
        UPDATE search_component SET config = '{"layoutType":"tabbed"}' where componentname in ('advanced-search', 'related-resources-filter', 'search-result-details', 'map-filter');
        UPDATE search_component SET config = '{"layoutType":"popup"}' where componentname in ('time-filter', 'saved-searches', 'search-export');
        UPDATE search_component SET componentpath = null where componentpath = '';
        UPDATE search_component SET type = componentname || '-type' 
        WHERE componentname IN (
            'advanced-search',
            'map-filter',
            'paging-filter',
            'provisional-filter',
            'related-resources-filter',
            'resource-type-filter',
            'saved-searches',
            'search-export',
            'search-results',
            'search-result-details',
            'sort-results',
            'term-filter',
            'time-filter'
        );
        
    """
    reverse_sql = """
        delete from search_component where searchcomponentid = '69695d63-6f03-4536-8da9-841b07116381';
        UPDATE search_component SET enabled = true, sortorder = 2 where type != 'search-view';
        UPDATE search_component SET type = 'filter' where type like '%-type';
        UPDATE search_component SET type = 'filter', sortorder = 1 where componentname = 'map-filter';
        UPDATE search_component SET type = 'results-list' where componentname = 'search-results';
        UPDATE search_component SET type = 'text-input' where componentname = 'term-filter';
        UPDATE search_component SET componentpath = '' where componentpath is null;
        UPDATE search_component SET type = 'inline-filter' 
        where componentname in (
            'sort-results',
            'provisional-filter',
            'paging-filter',
            'resource-type-filter'
        );
        UPDATE search_component SET type = 'popup' where componentname in (
            'time-filter',
            'search-export',
            'saved-searches'
        );

    """

    operations = [
        migrations.AlterField(
            model_name="searchcomponent",
            name="componentpath",
            field=models.TextField(null=True, unique=True),
        ),
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
