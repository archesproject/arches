from datetime import timedelta
from uuid import uuid4

from django.db import connection
from django.utils import timezone

from arches.app.const import DefaultLifecycleStates
from arches.app.models.models import NodeGroup, ResourceInstance, TileModel
from tests.base_test import ArchesTestCase
from tests.constants import CardinalityTestGraph

# these tests can be run from the command line via
# python manage.py test tests.models.row_metadata_tests --settings="tests.test_settings"

METADATA_FIELDS = ("id", "createdtime", "last_updated")
TRIGGER_NAME = "__arches_manage_row_metadata_trigger"
NODEGROUP_ID = "99999999-0000-0000-0000-0000000000aa"


class RowMetadataTestsMixin:
    """
    Regression tests for the database-managed id/createdtime/last_updated
    columns (see migration 13002). Subclasses provide the model-specific hooks.
    """

    model = None
    # A regular field that change() modifies.
    changed_field = None
    # Columns copied from an existing row to build raw SQL inserts.
    raw_copy_columns = ()

    def build(self, **kwargs):
        raise NotImplementedError

    def change(self, instance):
        """Modify changed_field on instance."""
        raise NotImplementedError

    def create(self, **kwargs):
        instance = self.build(**kwargs)
        instance.save()
        return instance

    def persisted_metadata(self, instance):
        return self.model.objects.values(*METADATA_FIELDS).get(pk=instance.pk)

    def instance_metadata(self, instance):
        return {field: getattr(instance, field) for field in METADATA_FIELDS}

    def assertMatchesDatabase(self, instance):
        """The ORM never writes these fields, so values on a saved instance
        must have come back from the database via RETURNING."""
        self.assertEqual(
            self.instance_metadata(instance), self.persisted_metadata(instance)
        )

    def backdate(self, instance):
        """Push createdtime/last_updated into the past (bypassing the trigger),
        so later bumps are detectable without relying on clock resolution."""
        table = self.model._meta.db_table
        backdated_timestamp = timezone.now() - timedelta(days=365)
        with connection.cursor() as cursor:
            # ALTER TABLE refuses to run while deferred trigger events
            # (e.g. tiles' spatial constraint trigger) are pending.
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
            cursor.execute(f"ALTER TABLE {table} DISABLE TRIGGER {TRIGGER_NAME}")
            cursor.execute(
                f"UPDATE {table} SET createdtime = %s, last_updated = %s "
                f"WHERE {self.model._meta.pk.column} = %s",
                [backdated_timestamp, backdated_timestamp, instance.pk],
            )
            cursor.execute(f"ALTER TABLE {table} ENABLE TRIGGER {TRIGGER_NAME}")
        return self.model.objects.get(pk=instance.pk)

    def raw_insert_copy(self, source, explicit_metadata=None):
        """Insert a copy of source via raw SQL, optionally supplying metadata."""
        table = self.model._meta.db_table
        pk_column = self.model._meta.pk.column
        copy_columns = ", ".join(self.raw_copy_columns)
        new_pk = uuid4()
        metadata_columns = ""
        metadata_values = ""
        params = [new_pk]
        if explicit_metadata:
            metadata_columns = ", " + ", ".join(explicit_metadata)
            metadata_values = ", " + ", ".join(["%s"] * len(explicit_metadata))
            params.extend(explicit_metadata.values())
        params.append(source.pk)
        with connection.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO {table} ({pk_column}, {copy_columns}{metadata_columns}) "
                f"SELECT %s, {copy_columns}{metadata_values} FROM {table} "
                f"WHERE {pk_column} = %s",
                params,
            )
        return self.model.objects.get(pk=new_pk)

    def assertWriteManagesMetadata(
        self, write, *, overwrite_metadata=True, refreshes_instance=False
    ):
        """
        Run write(instance) against one row twice: first unchanged, then after
        changing changed_field (and, if overwrite_metadata, setting bogus
        metadata values for the write to try to persist).
        """
        instance = self.backdate(self.create())
        original = self.instance_metadata(instance)

        with self.subTest("unchanged row keeps all metadata"):
            write(instance)

            self.assertEqual(self.persisted_metadata(instance), original)
            if refreshes_instance:
                self.assertMatchesDatabase(instance)

        with self.subTest("changed row keeps id/createdtime, bumps last_updated"):
            self.change(instance)
            if overwrite_metadata:
                instance.id = original["id"] + 1000
                instance.createdtime = timezone.now()
                instance.last_updated = original["last_updated"] - timedelta(days=1)
            write(instance)

            persisted = self.persisted_metadata(instance)
            self.assertEqual(persisted["id"], original["id"])
            self.assertEqual(persisted["createdtime"], original["createdtime"])
            self.assertGreater(persisted["last_updated"], original["last_updated"])
            if refreshes_instance:
                self.assertMatchesDatabase(instance)

    # Inserts

    def test_insert_generates_metadata(self):
        unsaved = self.build()
        self.assertEqual(
            self.instance_metadata(unsaved), dict.fromkeys(METADATA_FIELDS)
        )

        first = self.create()
        self.assertIsNotNone(first.id)
        self.assertIsNotNone(first.createdtime)
        self.assertEqual(first.createdtime, first.last_updated)
        self.assertMatchesDatabase(first)

        explicit_id = first.id + 1000
        explicit_timestamp = timezone.now() - timedelta(days=365)
        second = self.create(
            id=explicit_id,
            createdtime=explicit_timestamp,
            last_updated=explicit_timestamp,
        )
        self.assertNotEqual(second.id, explicit_id)
        self.assertGreater(second.id, first.id)
        self.assertGreater(second.createdtime, explicit_timestamp)
        self.assertGreater(second.last_updated, explicit_timestamp)
        self.assertMatchesDatabase(second)

    def test_bulk_create_generates_metadata(self):
        explicit_timestamp = timezone.now() - timedelta(days=365)
        instances = self.model.objects.bulk_create(
            [
                self.build(id=1, createdtime=explicit_timestamp),
                self.build(id=1, last_updated=explicit_timestamp),
            ]
        )

        first, second = instances
        self.assertGreater(second.id, first.id)
        for instance in instances:
            self.assertGreater(instance.createdtime, explicit_timestamp)
            self.assertEqual(instance.createdtime, instance.last_updated)
            self.assertMatchesDatabase(instance)

    def test_raw_insert_generates_metadata(self):
        source = self.create()

        omitted = self.raw_insert_copy(source)
        self.assertGreater(omitted.id, source.id)
        self.assertIsNotNone(omitted.createdtime)
        self.assertEqual(omitted.createdtime, omitted.last_updated)

        explicit_id = source.id + 1000
        explicit_timestamp = timezone.now() - timedelta(days=365)
        explicit = self.raw_insert_copy(
            source,
            explicit_metadata={
                "id": explicit_id,
                "createdtime": explicit_timestamp,
                "last_updated": explicit_timestamp,
            },
        )
        self.assertNotEqual(explicit.id, explicit_id)
        self.assertGreater(explicit.id, omitted.id)
        self.assertGreater(explicit.createdtime, explicit_timestamp)
        self.assertGreater(explicit.last_updated, explicit_timestamp)

    # Updates

    def test_save_manages_metadata(self):
        self.assertWriteManagesMetadata(
            lambda instance: instance.save(), refreshes_instance=True
        )

    def test_partial_save_manages_metadata(self):
        # Fields outside update_fields aren't refreshed, so leave them intact.
        self.assertWriteManagesMetadata(
            lambda instance: instance.save(update_fields=[self.changed_field]),
            overwrite_metadata=False,
            refreshes_instance=True,
        )

    def test_queryset_update_manages_metadata(self):
        written_fields = (self.changed_field, *METADATA_FIELDS)
        self.assertWriteManagesMetadata(
            lambda instance: self.model.objects.filter(pk=instance.pk).update(
                **{field: getattr(instance, field) for field in written_fields}
            )
        )

    def test_bulk_update_manages_metadata(self):
        written_fields = [self.changed_field, *METADATA_FIELDS]
        self.assertWriteManagesMetadata(
            lambda instance: self.model.objects.bulk_update([instance], written_fields)
        )

    def test_raw_update_manages_metadata(self):
        written_fields = (self.changed_field, *METADATA_FIELDS)
        assignments = ", ".join(
            f"{self.model._meta.get_field(field).column} = %s"
            for field in written_fields
        )

        def raw_update(instance):
            with connection.cursor() as cursor:
                cursor.execute(
                    f"UPDATE {self.model._meta.db_table} SET {assignments} "
                    f"WHERE {self.model._meta.pk.column} = %s",
                    [getattr(instance, field) for field in written_fields]
                    + [instance.pk],
                )

        self.assertWriteManagesMetadata(raw_update)

    def test_blind_overwrite_preserves_id_and_createdtime(self):
        instance = self.backdate(self.create())
        original = self.instance_metadata(instance)

        unfetched = self.build(pk=instance.pk)
        self.change(unfetched)
        unfetched.save()

        self.assertEqual(unfetched.id, original["id"])
        self.assertEqual(unfetched.createdtime, original["createdtime"])
        self.assertGreater(unfetched.last_updated, original["last_updated"])
        self.assertMatchesDatabase(unfetched)

    # Instance construction

    def test_first_positional_argument_is_primary_key(self):
        """id is declared after the pk so Model(pk_value) keeps working."""
        pk_value = uuid4()

        instance = self.model(pk_value)

        self.assertEqual(instance.pk, pk_value)
        self.assertIsNone(instance.id)

    def test_copied_instance_passes_unique_validation(self):
        """A copy still carrying the source's id must not fail full_clean();
        the ORM never writes id, so it can't collide."""
        instance = self.create()
        copy = self.model.objects.get(pk=instance.pk)
        copy.pk = uuid4()
        copy._state.adding = True

        copy.validate_unique()

        copy.save()
        self.assertNotEqual(copy.id, instance.id)
        self.assertMatchesDatabase(copy)


class ResourceInstanceRowMetadataTests(RowMetadataTestsMixin, ArchesTestCase):
    graph_fixtures = ["Cardinality Test Model"]
    model = ResourceInstance
    changed_field = "legacyid"
    raw_copy_columns = ("graphid", "resource_instance_lifecycle_state_id")

    def build(self, **kwargs):
        return ResourceInstance(
            graph_id=CardinalityTestGraph.GRAPH_ID.value,
            resource_instance_lifecycle_state_id=DefaultLifecycleStates.PERPETUAL.value,
            **kwargs,
        )

    def change(self, instance):
        instance.legacyid = str(uuid4())


class TileModelRowMetadataTests(RowMetadataTestsMixin, ArchesTestCase):
    graph_fixtures = ["Cardinality Test Model"]
    model = TileModel
    changed_field = "sortorder"
    raw_copy_columns = ("resourceinstanceid", "nodegroupid", "tiledata", "sortorder")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.resource = ResourceInstance.objects.create(
            graph_id=CardinalityTestGraph.GRAPH_ID.value,
            resource_instance_lifecycle_state_id=DefaultLifecycleStates.PERPETUAL.value,
        )
        NodeGroup.objects.create(pk=NODEGROUP_ID, cardinality="n")

    def build(self, **kwargs):
        return TileModel(
            resourceinstance_id=self.resource.pk,
            nodegroup_id=NODEGROUP_ID,
            data={},
            sortorder=0,
            **kwargs,
        )

    def change(self, instance):
        instance.sortorder += 1
