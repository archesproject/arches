from __future__ import unicode_literals

from arches.app.search.search_engine_factory import SearchEngineFactory
from django.db import migrations


def forwards_func(apps, schema_editor):
    se = SearchEngineFactory().create()
    body = {
        '_doc': {
            'properties': {
                'ids': {
                    'type': 'nested',
                    'properties': {
                        'id': {'type': 'keyword'},
                        'nodegroup_id': {'type': 'keyword'},
                        'provisional': {'type': 'boolean'}
                    }
                }
            }
        }
    }
    se.create_mapping(index='resources', body=body)


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('models', '5076_adds_map_card_sourcelayer_config'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
