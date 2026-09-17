"""Applied-state ledger for package migrations.

The same three columns as django_migrations, in a table of its own, so the base
MigrationRecorder.ensure_schema() creates it on first use exactly as it creates
django_migrations.
"""

from django.apps.registry import Apps
from django.db import models
from django.db.migrations.recorder import MigrationRecorder
from django.utils.functional import classproperty
from django.utils.timezone import now


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

                class Meta:
                    apps = Apps()
                    app_label = "package_migrations"
                    db_table = "arches_package_migrations"

                def __str__(self):
                    return "Package migration %s for %s" % (self.name, self.app)

            cls._migration_class = Migration
        return cls._migration_class
