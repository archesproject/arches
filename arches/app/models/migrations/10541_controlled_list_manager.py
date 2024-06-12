# Generated by Django 4.2.13 on 2024-05-23 11:06

import django.core.validators
from django.db import migrations, models
import django.db.models.constraints
import django.db.models.deletion
import django.db.models.fields.json
import django.db.models.functions.comparison
import textwrap
import uuid

from arches.app.models.fields.i18n import I18n_String


class Migration(migrations.Migration):
    dependencies = [
        ("models", "9525_add_published_graph_edits"),
    ]

    def add_plugin(apps, schema_editor):
        Plugin = apps.get_model("models", "Plugin")

        Plugin(
            pluginid=uuid.UUID("60aa3e80-4aea-4042-a76e-5a872b1c36a0"),
            name=I18n_String("Controlled List Manager"),
            icon="fa fa-list",
            component="views/components/plugins/controlled-list-manager",
            componentname="controlled-list-manager",
            config={"show": True},
            slug="controlled-list-manager",
            sortorder=0,
        ).save()

    def remove_plugin(apps, schema_editor):
        Plugin = apps.get_model("models", "Plugin")
        Plugin.objects.filter(slug="controlled-list-manager").delete()

    add_reference_datatype = textwrap.dedent(
        """
        INSERT INTO d_data_types(
            datatype,
            iconclass,
            modulename,
            classname,
            defaultconfig,
            configcomponent,
            configname,
            isgeometric,
            defaultwidget,
            issearchable
        ) VALUES (
            'reference',
            'fa fa-list',
            'datatypes.py',
            'ReferenceDataType',
            '{"controlledList": null, "multiValue": false}',
            'views/components/datatypes/reference',
            'reference-datatype-config',
            FALSE,
            '19e56148-82b8-47eb-b66e-f6243639a1a8',
            TRUE
        )
        ON CONFLICT DO NOTHING;

        INSERT INTO widgets(
            widgetid,
            name,
            component,
            datatype,
            defaultconfig
        ) VALUES (
            '19e56148-82b8-47eb-b66e-f6243639a1a8',
            'reference-select-widget',
            'views/components/widgets/reference-select',
            'reference',
            '{"placeholder": "Select an option", "i18n_properties": ["placeholder"]}'
        )
        ON CONFLICT DO NOTHING;
        """
    )

    operations = [
        migrations.RunPython(add_plugin, remove_plugin),
        migrations.RunSQL(add_reference_datatype, migrations.RunSQL.noop),
        migrations.CreateModel(
            name="ControlledListItemImage",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("value", models.FileField(upload_to="controlled_list_item_images")),
            ],
            options={
                "db_table": "controlled_list_item_values",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="ControlledList",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=127, blank=True)),
                ("dynamic", models.BooleanField(default=False)),
                ("search_only", models.BooleanField(default=False)),
            ],
            options={
                "db_table": "controlled_lists",
            },
        ),
        migrations.CreateModel(
            name="ControlledListItem",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("uri", models.URLField(blank=True, max_length=2048, null=True)),
                (
                    "sortorder",
                    models.IntegerField(
                        validators=[django.core.validators.MinValueValidator(0)]
                    ),
                ),
                ("guide", models.BooleanField(default=False)),
            ],
            options={
                "db_table": "controlled_list_items",
            },
        ),
        migrations.CreateModel(
            name="ControlledListItemImageMetadata",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "metadata_type",
                    models.CharField(
                        choices=[
                            ("title", "Title"),
                            ("desc", "Description"),
                            ("attr", "Attribution"),
                            ("alt", "Alternative text"),
                        ],
                        max_length=5,
                    ),
                ),
                ("value", models.CharField(max_length=2048)),
            ],
            options={
                "db_table": "controlled_list_item_image_metadata",
            },
        ),
        migrations.CreateModel(
            name="ControlledListItemValue",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("value", models.CharField(max_length=1024, blank=True)),
            ],
            options={
                "db_table": "controlled_list_item_values",
            },
        ),
        migrations.AddIndex(
            model_name="node",
            index=models.Index(
                django.db.models.functions.comparison.Cast(
                    django.db.models.fields.json.KeyTextTransform(
                        "controlledList", "config"
                    ),
                    output_field=models.UUIDField(),
                ),
                name="lists_reffed_by_node_idx",
            ),
        ),
        migrations.AddField(
            model_name="controlledlistitemvalue",
            name="controlled_list_item",
            field=models.ForeignKey(
                db_column="itemid",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="controlled_list_item_values",
                to="models.controlledlistitem",
            ),
        ),
        migrations.AddField(
            model_name="controlledlistitemvalue",
            name="language",
            field=models.ForeignKey(
                blank=True,
                db_column="languageid",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="models.language",
                to_field="code",
            ),
        ),
        migrations.AddField(
            model_name="controlledlistitemvalue",
            name="valuetype",
            field=models.ForeignKey(
                limit_choices_to=models.Q(("category__in", ("label", "image", "note"))),
                on_delete=django.db.models.deletion.PROTECT,
                to="models.dvaluetype",
            ),
        ),
        migrations.AddField(
            model_name="controlledlistitemimagemetadata",
            name="controlled_list_item_image",
            field=models.ForeignKey(
                db_column="labelid",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="controlled_list_item_image_metadata",
                to="models.controlledlistitemimage",
            ),
        ),
        migrations.AddField(
            model_name="controlledlistitemimagemetadata",
            name="language",
            field=models.ForeignKey(
                db_column="languageid",
                on_delete=django.db.models.deletion.PROTECT,
                to="models.language",
                to_field="code",
            ),
        ),
        migrations.AddField(
            model_name="controlledlistitem",
            name="controlled_list",
            field=models.ForeignKey(
                db_column="listid",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="controlled_list_items",
                to="models.controlledlist",
            ),
        ),
        migrations.AddField(
            model_name="controlledlistitem",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="models.controlledlistitem",
            ),
        ),
        migrations.AddConstraint(
            model_name="controlledlistitemvalue",
            constraint=models.UniqueConstraint(
                fields=("controlled_list_item", "value", "valuetype", "language"),
                name="unique_item_value_valuetype_language",
                violation_error_message="The same item value cannot be stored twice in the same language.",
            ),
        ),
        migrations.AddConstraint(
            model_name="controlledlistitemvalue",
            constraint=models.UniqueConstraint(
                condition=models.Q(("valuetype", "prefLabel")),
                fields=("controlled_list_item", "language"),
                name="unique_item_preflabel_language",
                violation_error_message="Only one preferred label per language is permitted.",
            ),
        ),
        migrations.AddConstraint(
            model_name="controlledlistitemvalue",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("language_id__isnull", False),
                    ("valuetype", "image"),
                    _connector="OR",
                ),
                name="only_images_nullable_language",
                violation_error_message="Item values must be associated with a language.",
            ),
        ),
        migrations.AddConstraint(
            model_name="controlledlistitemimagemetadata",
            constraint=models.UniqueConstraint(
                fields=("controlled_list_item_image", "metadata_type", "language"),
                name="unique_image_metadata_valuetype_language",
                violation_error_message="Only one metadata entry per language and metadata type is permitted.",
            ),
        ),
        migrations.AddConstraint(
            model_name="controlledlistitem",
            constraint=models.UniqueConstraint(
                deferrable=django.db.models.constraints.Deferrable["DEFERRED"],
                fields=("controlled_list", "sortorder"),
                name="unique_list_sortorder",
                violation_error_message="All items in this list must have distinct sort orders.",
            ),
        ),
        migrations.AddConstraint(
            model_name="controlledlistitem",
            constraint=models.UniqueConstraint(
                fields=("controlled_list", "uri"),
                name="unique_list_uri",
                violation_error_message="All items in this list must have distinct URIs.",
            ),
        ),
    ]
