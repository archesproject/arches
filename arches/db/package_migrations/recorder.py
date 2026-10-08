"""Applied-state ledger for package migrations, shaped like django_migrations."""

from django.apps.registry import Apps
from django.db import models
from django.db.migrations.recorder import MigrationRecorder
from django.utils.functional import classproperty
from django.utils.timezone import now


class PackageMigrationRecorder(MigrationRecorder):
    # Redeclared so the cache is not inherited from MigrationRecorder.
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
                    return f"Package migration {self.name} for {self.app}"

            cls._migration_class = Migration
        return cls._migration_class
