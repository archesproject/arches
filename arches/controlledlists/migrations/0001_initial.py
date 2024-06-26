# Generated by Django 4.2.14 on 2024-07-11 12:20

import textwrap
import uuid

import django.core.validators
from django.db import migrations, models
import django.db.models.constraints
import django.db.models.deletion
from guardian.ctypes import get_content_type

from arches.app.models.fields.i18n import I18n_String

PLUGIN_ID = uuid.UUID("60aa3e80-4aea-4042-a76e-5a872b1c36a0")


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("models", "9526_node_lists_reffed_by_node_idx"),
        ("guardian", "0002_generic_permissions_index"),
    ]

    def add_plugin(apps, schema_editor):
        Plugin = apps.get_model("models", "Plugin")

        Plugin(
            pluginid=PLUGIN_ID,
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

    def assign_view_plugin(apps, schema_editor):
        Group = apps.get_model("auth", "Group")
        Plugin = apps.get_model("models", "Plugin")
        Permission = apps.get_model("auth", "Permission")
        GroupObjectPermission = apps.get_model("guardian", "GroupObjectPermission")

        view_plugin = Permission.objects.get(codename="view_plugin")
        rdm_administrators = Group.objects.get(name="RDM Administrator")
        controlled_list_manager = Plugin.objects.get(pk=PLUGIN_ID)

        # Cannot use django_guardian shortcuts or object managers
        # https://github.com/django-guardian/django-guardian/issues/751
        GroupObjectPermission(
            permission=view_plugin,
            group=rdm_administrators,
            content_type_id=get_content_type(controlled_list_manager).pk,
            object_pk=PLUGIN_ID,
        ).save()

    def remove_view_plugin(apps, schema_editor):
        Group = apps.get_model("auth", "Group")
        Plugin = apps.get_model("models", "Plugin")
        Permission = apps.get_model("auth", "Permission")
        GroupObjectPermission = apps.get_model("guardian", "GroupObjectPermission")

        view_plugin = Permission.objects.get(codename="view_plugin")
        rdm_administrators = Group.objects.get(name="RDM Administrator")
        controlled_list_manager = Plugin.objects.get(pk=PLUGIN_ID)

        GroupObjectPermission.objects.filter(
            permission=view_plugin,
            group=rdm_administrators,
            content_type_id=get_content_type(controlled_list_manager).pk,
            object_pk=PLUGIN_ID,
        ).delete()

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
        migrations.RunPython(assign_view_plugin, remove_view_plugin),
        migrations.RunSQL(add_reference_datatype, migrations.RunSQL.noop),
        migrations.CreateModel(
            name="ListItemImage",
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
                ("value", models.FileField(upload_to="list_item_images")),
            ],
            options={
                "db_table": "controlledlists_listitemvalue",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="List",
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
                ("name", models.CharField(blank=True, max_length=127)),
                ("dynamic", models.BooleanField(default=False)),
                ("search_only", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="ListItem",
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
                (
                    "list",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="list_items",
                        to="controlledlists.list",
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="controlledlists.listitem",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ListItemValue",
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
                ("value", models.CharField(blank=True, max_length=1024)),
                (
                    "language",
                    models.ForeignKey(
                        blank=True,
                        db_column="languageid",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="models.language",
                        to_field="code",
                    ),
                ),
                (
                    "list_item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="list_item_values",
                        to="controlledlists.listitem",
                    ),
                ),
                (
                    "valuetype",
                    models.ForeignKey(
                        limit_choices_to=models.Q(
                            ("category__in", ("label", "image", "note"))
                        ),
                        on_delete=django.db.models.deletion.PROTECT,
                        to="models.dvaluetype",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ListItemImageMetadata",
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
                (
                    "language",
                    models.ForeignKey(
                        db_column="languageid",
                        on_delete=django.db.models.deletion.PROTECT,
                        to="models.language",
                        to_field="code",
                    ),
                ),
                (
                    "list_item_image",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="list_item_image_metadata",
                        to="controlledlists.listitemimage",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="listitemvalue",
            constraint=models.UniqueConstraint(
                fields=("list_item", "value", "valuetype", "language"),
                name="unique_item_value_valuetype_language",
                violation_error_message="The same item value cannot be stored twice in the same language.",
            ),
        ),
        migrations.AddConstraint(
            model_name="listitemvalue",
            constraint=models.UniqueConstraint(
                condition=models.Q(("valuetype", "prefLabel")),
                fields=("list_item", "language"),
                name="unique_item_preflabel_language",
                violation_error_message="Only one preferred label per language is permitted.",
            ),
        ),
        migrations.AddConstraint(
            model_name="listitemvalue",
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
            model_name="listitemimagemetadata",
            constraint=models.UniqueConstraint(
                fields=("list_item_image", "metadata_type", "language"),
                name="unique_image_metadata_valuetype_language",
                violation_error_message="Only one metadata entry per language and metadata type is permitted.",
            ),
        ),
        migrations.AddConstraint(
            model_name="listitem",
            constraint=models.UniqueConstraint(
                deferrable=django.db.models.constraints.Deferrable["DEFERRED"],
                fields=("list", "sortorder"),
                name="unique_list_sortorder",
                violation_error_message="All items in this list must have distinct sort orders.",
            ),
        ),
        migrations.AddConstraint(
            model_name="listitem",
            constraint=models.UniqueConstraint(
                fields=("list", "uri"),
                name="unique_list_uri",
                violation_error_message="All items in this list must have distinct URIs.",
            ),
        ),
    ]
