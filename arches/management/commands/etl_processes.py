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
            dest="lists_to_migrate",
            nargs="*",
            default=[],
            help="One or more collections to migrate to controlled lists"
        )

        parser.add_argument(
            "-preferred_sort_language",
            "--preferred_sort_language",
            dest="preferred_sort_language",
            default="en",
            help="The language to use for sorting preferred labels"
        )

    def handle(self, *args, **options):
        if options["operation"] == "migrate_collections_to_controlled_lists":
            self.migrate_collections_to_controlled_lists(
                lists_to_migrate=options["lists_to_migrate"],
                preferred_sort_language=options["preferred_sort_language"]
            )
    
    def migrate_collections_to_controlled_lists(self, lists_to_migrate, preferred_sort_language):
        """
        Uses a postgres function to migrate collections to controlled lists

        """

        from django.db import connection
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    """
                    select * from __arches_migrate_collections_to_clm(
                        ARRAY[%s], %s
                    );
                    """,
                    [lists_to_migrate, preferred_sort_language]
                )
                result = cursor.fetchone()
                if result:
                    self.stdout.write(result[0])
            except Exception as e:
                self.stdout.write(str(e))