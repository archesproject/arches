from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("models", "9259_performance_fixes"),
    ]

    forward_sql = """
        UPDATE nodes SET config = jsonb_set(config, '{graphs}', (
            SELECT jsonb_agg( element || '{"useOntologyRelationship": true}' ) FROM jsonb_array_elements(config -> 'graphs') element)
        )
        WHERE datatype IN ('resource-instance', 'resource-instance-list')
        AND EXISTS (SELECT * FROM jsonb_array_elements(config -> 'graphs') WHERE value->'ontologyProperty' IS NOT NULL)
        AND EXISTS (SELECT * FROM jsonb_array_elements(config -> 'graphs') WHERE value->'useOntologyRelationship' IS NULL)
        AND jsonb_array_length(config -> 'graphs') > 0;
    """

    """
    Reversing the addition of a property in a nested array means disassembling and reassembling the object. see https://stackoverflow.com/a/58802637
    Because this property would be inert in prior versions of Arches and because of the possible complexity of these configs,
    there is a chance of rebuilding node configs incorrectly in a reverse migration, the reverse migration will leave the property in place.
    """

    reverse_sql = ""

    operations = [
        migrations.RunSQL(forward_sql, reverse_sql),
    ]
