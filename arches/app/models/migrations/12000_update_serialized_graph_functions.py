from django.db import migrations


# Renames "functions" to "functions_x_graphs" in the serialized_graph field of published_graphs
# to allow for serialization of functions in draft graphs without affecting published graphs.
# This migration is necessary to maintain compatibility with existing 7.6.x published graphs.
class Migration(migrations.Migration):

    dependencies = [("models", "10887_loadstaging_nodegroup_nullable")]

    forward = r"""
        UPDATE published_graphs
        SET serialized_graph = (
            serialized_graph - 'functions' || jsonb_build_object('functions_x_graphs', serialized_graph->'functions')
        )
        WHERE serialized_graph ? 'functions';
    """

    reverse = r"""
        UPDATE published_graphs
        SET serialized_graph = (
            serialized_graph - 'functions_x_graphs' || jsonb_build_object('functions', serialized_graph->'functions_x_graphs')
        )
        WHERE serialized_graph ? 'functions_x_graphs';
    """

    operations = [
        migrations.RunSQL(forward, reverse),
    ]
