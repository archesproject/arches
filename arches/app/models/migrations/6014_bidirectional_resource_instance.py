from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("models", "6125_details_search_component"),
    ]

    operations = [
        migrations.AlterField(
            model_name="resourcexresource",
            name="resourceinstanceidfrom",
            field=models.ForeignKey(
                blank=True,
                db_column="resourceinstanceidfrom",
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="resxres_resource_instance_ids_from",
                to="models.ResourceInstance",
            ),
        ),
        migrations.AlterField(
            model_name="resourcexresource",
            name="resourceinstanceidto",
            field=models.ForeignKey(
                blank=True,
                db_column="resourceinstanceidto",
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="resxres_resource_instance_ids_to",
                to="models.ResourceInstance",
            ),
        ),
        migrations.AddField(model_name="resourcexresource", name="inverserelationshiptype", field=models.TextField(blank=True, null=True),),
        migrations.AddField(
            model_name="resourcexresource",
            name="tileid",
            field=models.ForeignKey(
                blank=True,
                db_column="tileid",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="resxres_tile_id",
                to="models.TileModel",
            ),
        ),
        migrations.AddField(
            model_name="resourcexresource",
            name="nodeid",
            field=models.ForeignKey(
                blank=True,
                db_column="nodeid",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="resxres_node_id",
                to="models.Node",
            ),
        ),
    ]
