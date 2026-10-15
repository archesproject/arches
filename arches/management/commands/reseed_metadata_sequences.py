from django.core.management.base import BaseCommand
from django.db import connection


TABLES = (
    ("resource_instances", "resource_instances_id_seq"),
    ("tiles", "tiles_id_seq"),
)


class Command(BaseCommand):
    help = (
        "Reseed row metadata ID sequences after importing explicit IDs into "
        "resource_instances or tiles."
    )

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            for table, sequence in TABLES:
                cursor.execute(
                    f"""
                    SELECT setval(
                        '{sequence}'::regclass,
                        GREATEST(
                            COALESCE(MAX(id), 1),
                            (SELECT last_value FROM {sequence})
                        ),
                        MAX(id) IS NOT NULL OR (SELECT is_called FROM {sequence})
                    )
                    FROM {table}
                    """
                )
        self.stdout.write("Metadata ID sequences reseeded.")
