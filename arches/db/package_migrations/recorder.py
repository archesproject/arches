"""Applied-state ledger for package migrations.

The table is created by a real Django schema migration rather than by
``ensure_schema()``. Django can self-bootstrap ``django_migrations`` only
because its three columns are frozen; this table will gain columns.
"""

from django.apps.registry import Apps
from django.db import models
from django.db.migrations.exceptions import MigrationSchemaMissing
from django.db.migrations.recorder import MigrationRecorder
from django.utils.functional import classproperty
from django.utils.timezone import now

PACKAGE_MIGRATIONS_TABLE = "arches_package_migrations"


class PackageMigrationRecorder(MigrationRecorder):
    # MigrationRecorder caches its floating model with ``if cls._migration_class
    # is None``, which reads through the MRO. Without redeclaring it here, a
    # subclass silently returns the BASE model and writes to django_migrations
    # whenever anything has touched MigrationRecorder.Migration first.
    _migration_class = None

    @classproperty
    def Migration(cls):
        if cls._migration_class is None:

            class Migration(models.Model):
                app = models.CharField(max_length=255)
                name = models.CharField(max_length=255)
                applied = models.DateTimeField(default=now)
                from_publication = models.UUIDField(null=True)
                to_publication = models.UUIDField(null=True)
                resume_cursor = models.JSONField(null=True)
                touched_graphs = models.JSONField(null=True)

                class Meta:
                    apps = Apps()
                    app_label = "package_migrations"
                    db_table = PACKAGE_MIGRATIONS_TABLE
                    constraints = [
                        models.UniqueConstraint(
                            fields=["app", "name"],
                            name="unique_arches_package_migration",
                        )
                    ]

                def __str__(self):
                    return "Package migration %s for %s" % (self.name, self.app)

            cls._migration_class = Migration
        return cls._migration_class

    def ensure_schema(self):
        """The base implementation creates the table and reports the wrong name
        on failure. Ours is owned by a Django schema migration, so this is only
        a guard against running before `manage.py migrate`.
        """
        if self.has_table():
            return
        raise MigrationSchemaMissing(
            "The %s table does not exist. Run `manage.py migrate` first."
            % PACKAGE_MIGRATIONS_TABLE
        )

    def record_applied(self, app, name, **fields):
        """Idempotent: the UniqueConstraint would otherwise turn a re-record
        (load_package stamping over an applied migration) into an IntegrityError.
        """
        self.ensure_schema()
        self.migration_qs.update_or_create(app=app, name=name, defaults=fields)
