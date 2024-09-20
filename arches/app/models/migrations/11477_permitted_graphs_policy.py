from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("models", "11042_update__arches_staging_to_tile"),
    ]
    sql = """
    INSERT INTO search_component
    VALUES (
        '56b3feba-ffd4-445e-bd82-377fca29ff92',
        'Permited Graphs Policy',
        '',
        'permitted_graphs_policy.py',
        'PermittedGraphsPolicy',
        'search-policy',
        NULL,
        'permitted-graphs-policy',
        '{}'
    );
    UPDATE search_component
    SET config = '{"default":true,"linkedSearchFilters":[{"componentname":"map-filter","searchcomponentid":"09d97fc6-8c83-4319-9cef-3aaa08c3fbec","layoutSortorder":1},{"componentname":"advanced-search","searchcomponentid":"f0e56205-acb5-475b-9c98-f5e44f1dbd2c","layoutSortorder":2},{"componentname":"related-resources-filter","searchcomponentid":"59f28272-d1f1-4805-af51-227771739aed","layoutSortorder":3},{"componentname":"provisional-filter","searchcomponentid":"073406ed-93e5-4b5b-9418-b61c26b3640f","layoutSortorder":4},{"componentname":"resource-type-filter","searchcomponentid":"f1c46b7d-0132-421b-b1f3-95d67f9b3980","layoutSortorder":5},{"componentname":"saved-searches","searchcomponentid":"6dc29637-43a1-4fba-adae-8d9956dcd3b9","layoutSortorder":6},{"componentname":"search-export","searchcomponentid":"9c6a5a9c-a7ec-48d2-8a25-501b55b8eff6","layoutSortorder":7},{"componentname":"search-result-details","searchcomponentid":"f5986dae-8b01-11ea-b65a-77903936669c","layoutSortorder":8},{"componentname":"sort-results","searchcomponentid":"6a2fe122-de54-4e44-8e93-b6a0cda7955c","layoutSortorder":9},{"componentname":"term-filter","searchcomponentid":"1f42f501-ed70-48c5-bae1-6ff7d0d187da","layoutSortorder":10},{"componentname":"time-filter","searchcomponentid":"7497ed4f-2085-40da-bee5-52076a48bcb1","layoutSortorder":11},{"componentname":"paging-filter","searchcomponentid":"7aff5819-651c-4390-9b9a-a61221ba52c6","required":true,"layoutSortorder":12,"executionSortorder":2},{"componentname":"search-results","searchcomponentid":"00673743-8c1c-4cc0-bd85-c073a52e03ec","required":true,"layoutSortorder":13,"executionSortorder":1},{"componentname":"permitted-graphs-policy","searchcomponentid":"56b3feba-ffd4-445e-bd82-377fca29ff92","required":true,"layoutSortorder":14,"executionSortorder":3}]}'
    WHERE searchcomponentid = '69695d63-6f03-4536-8da9-841b07116381';
    """
    reverse_sql = """
    UPDATE search_component
    SET config = '{"default":true,"linkedSearchFilters":[{"componentname":"map-filter","searchcomponentid":"09d97fc6-8c83-4319-9cef-3aaa08c3fbec","layoutSortorder":1},{"componentname":"advanced-search","searchcomponentid":"f0e56205-acb5-475b-9c98-f5e44f1dbd2c","layoutSortorder":2},{"componentname":"related-resources-filter","searchcomponentid":"59f28272-d1f1-4805-af51-227771739aed","layoutSortorder":3},{"componentname":"provisional-filter","searchcomponentid":"073406ed-93e5-4b5b-9418-b61c26b3640f","layoutSortorder":4},{"componentname":"resource-type-filter","searchcomponentid":"f1c46b7d-0132-421b-b1f3-95d67f9b3980","layoutSortorder":5},{"componentname":"saved-searches","searchcomponentid":"6dc29637-43a1-4fba-adae-8d9956dcd3b9","layoutSortorder":6},{"componentname":"search-export","searchcomponentid":"9c6a5a9c-a7ec-48d2-8a25-501b55b8eff6","layoutSortorder":7},{"componentname":"search-result-details","searchcomponentid":"f5986dae-8b01-11ea-b65a-77903936669c","layoutSortorder":8},{"componentname":"sort-results","searchcomponentid":"6a2fe122-de54-4e44-8e93-b6a0cda7955c","layoutSortorder":9},{"componentname":"term-filter","searchcomponentid":"1f42f501-ed70-48c5-bae1-6ff7d0d187da","layoutSortorder":10},{"componentname":"time-filter","searchcomponentid":"7497ed4f-2085-40da-bee5-52076a48bcb1","layoutSortorder":11},{"componentname":"paging-filter","searchcomponentid":"7aff5819-651c-4390-9b9a-a61221ba52c6","required":true,"layoutSortorder":12,"executionSortorder":2},{"componentname":"search-results","searchcomponentid":"00673743-8c1c-4cc0-bd85-c073a52e03ec","required":true,"layoutSortorder":13,"executionSortorder":1}]}'
    WHERE searchcomponentid = '69695d63-6f03-4536-8da9-841b07116381';
    DELETE FROM search_component WHERE searchcomponentid = '56b3feba-ffd4-445e-bd82-377fca29ff92';
    """

    operations = [
        migrations.RunSQL(
            sql=sql,
            reverse_sql=reverse_sql,
        ),
    ]
