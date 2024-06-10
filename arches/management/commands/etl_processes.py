from arches.app.models.models import Concept, Value
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """
    Commands for running Arches ETL processes

    """
    
    def add_arguments(self, parser):
        parser.add_argument(
            "-o", 
            "--operation",
            action="store",
            dest="operation",
            choices=["migrate_collections_to_controlled_lists"],
            help="The operation to perform"
        )

        parser.add_argument(
            "-co",
            "--collections",
            dest="collections_to_migrate",
            nargs="*",
            required=True,
            help="One or more collections to migrate to controlled lists"
        )

        parser.add_argument(
            "-psl",
            "--preferred_sort_language",
            dest="preferred_sort_language",
            default="en",
            help="The language to use for sorting preferred labels"
        )

    def handle(self, *args, **options):
        if options["operation"] == "migrate_collections_to_controlled_lists":
            self.migrate_collections_to_controlled_lists(
                collections_to_migrate=options["collections_to_migrate"],
                preferred_sort_language=options["preferred_sort_language"]
            )
    
    def migrate_collections_to_controlled_lists(self, collections_to_migrate, preferred_sort_language):
        """
        Uses a postgres function to migrate collections to controlled lists

        Example usage: 
            python manage.py etl_processes 
                -o migrate_collections_to_controlled_lists 
                -co 'Johns list' 'Getty AAT'
                -psl 'en'
        """

        collections_in_db = list(Value.objects.filter(
            value__in=collections_to_migrate,
            valuetype__in=['prefLabel', 'identifier'],
            concept__nodetype='Collection'
        ).values_list('value', flat=True))

        failed_collections = [
            collection for collection in collections_to_migrate if collection not in collections_in_db
        ]

        if len(failed_collections) > 0:
            self.stdout.write(
                'Failed to find the following collections in the database: %s' % ', '.join(failed_collections)
            )

        if len(collections_in_db) > 0:
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute(
                """
                select * from __arches_migrate_collections_to_clm(
                    ARRAY[%s], %s
                );
                """,
                [collections_in_db, preferred_sort_language]
            )
            result = cursor.fetchone()
            self.stdout.write(result[0])