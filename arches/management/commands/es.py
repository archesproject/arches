"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

"""This module contains commands for building Arches."""

import uuid
import logging
from django.core.management.base import BaseCommand
from arches.app.models.system_settings import settings
from arches.app.search.base_index import get_index
from arches.app.search.mappings import (
    prepare_terms_index,
    prepare_concepts_index,
    delete_terms_index,
    delete_concepts_index,
    prepare_search_index,
    delete_search_index,
)
import arches.app.utils.index_database as index_database_util
from arches.app.utils.string_utils import str_to_bool

from arches.app.search.search_engine_factory import SearchEngineFactory

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Commands for running common elasticsearch commands

    """

    def add_arguments(self, parser):
        parser.add_argument(
            "operation",
            nargs="?",
            choices=[
                "install",
                "setup_indexes",
                "delete_indexes",
                "index_database",
                "reindex_database",
                "index_concepts",
                "index_resources",
                "index_resources_by_type",
                "index_resources_by_transaction",
                "add_index",
                "delete_index",
                "restore_snapshot",
                "create_snapshot",
                "list_snapshots",
                "snapshot_restore_status",
            ],
            help="Operation Type; "
            + "'setup_indexes'=Creates the indexes in Elastic Search needed by the system"
            + "'delete_indexes'=Deletes all indexes in Elasticsearch required by the system"
            + "'index_database'=Indexes all the data (resources, concepts, and resource relations) found in the database"
            + "'reindex_database'=Deletes and re-creates all indices in ElasticSearch, then indexes all data found in the database"
            + "'index_concepts'=Indexes all concepts from the database"
            + "'index_resources'=Indexes all resources from the database"
            + "'index_resources_by_type'=Indexes only resources of a given resource_model/graph"
            + "'index_resources_by_transaction'=Indexes only resources of a given transaction"
            + "'add_index'=Register a new index in Elasticsearch"
            + "'delete_index'=Deletes a named index from Elasticsearch"
            + "'restore_snapshot'=Restores a named snapshot from Elasticsearch"
            + "'create_snapshot'=Creates a new snapshot in specified Elasticsearch repository"
            + "'list_snapshots'=Lists snapshots in specified Elasticsearch repository"
            + "'snapshot_restore_status'=Lists snapshots restore status for the current indices",
        )

        parser.add_argument(
            "-d",
            "--dest_dir",
            action="store",
            dest="dest_dir",
            default="",
            help="Directory from where you want to run elasticsearch.",
        )

        parser.add_argument(
            "-p",
            "--port",
            action="store",
            dest="port",
            default=settings.ELASTICSEARCH_HTTP_PORT,
            help="Port to use for elasticsearch.",
        )

        parser.add_argument(
            "-rt",
            "--resource_type",
            action="store",
            dest="resource_types",
            default="",
            help="UUID of resource_model to index resources of.",
        )

        parser.add_argument(
            "-t",
            "--transaction",
            action="store",
            dest="transaction",
            default="",
            help="The transaction id of the resources to index.",
        )

        parser.add_argument(
            "-b",
            "--batch_size",
            action="store",
            dest="batch_size",
            type=int,
            default=settings.BULK_IMPORT_BATCH_SIZE,
            help="The number of records to index as a group, the larger the number to more memory required",
        )

        parser.add_argument(
            "-c",
            "--clear_index",
            action="store",
            dest="clear_index",
            default=True,
            type=str_to_bool,
            help="Whether to remove all target resources from the index before reindexing. Accepts 'true'/'false', 'yes'/'no', 'y'/'n', 't'/'f', 'on'/'off', or '1'/'0' (case-insensitive). Default is True.",
        )

        parser.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            dest="quiet",
            default=False,
            help="Silences the status bar output during certain operations, use in celery operations for example",
        )

        parser.add_argument(
            "-n",
            "--name ",
            action="store",
            dest="name",
            default=None,
            help="Name of the custom index",
        )

        parser.add_argument(
            "-sn",
            "--snapshot_name",
            action="store",
            dest="snapshot_name",
            default=None,
            help="Name of the snapshot",
        )

        parser.add_argument(
            "-rn",
            "--repository_name",
            action="store",
            dest="repository_name",
            default=None,
            help="Name of the snapshot repository",
        )

        parser.add_argument(
            "-mp",
            "--use_multiprocessing",
            action="store_true",
            dest="use_multiprocessing",
            default=False,
            help="indexes the batches in parallel processes",
        )

        parser.add_argument(
            "-mxp",
            "--max_subprocesses",
            action="store",
            type=int,
            dest="max_subprocesses",
            default=0,
            help="Changes the process pool size when using use_multiprocessing. Default is ceil(cpu_count()/2)",
        )

        parser.add_argument(
            "-rd",
            "--recalculate-descriptors",
            action="store_true",
            dest="recalculate_descriptors",
            default=False,
            help="forces the primary descriptors to be recalculated before (re)indexing",
        )

    def handle(self, *args, **options):
        if options["operation"] == "setup_indexes":
            self.setup_indexes(name=options["name"])

        if options["operation"] == "add_index":
            self.register_index(name=options["name"])

        if options["operation"] == "delete_indexes":
            self.delete_indexes(name=options["name"])

        if options["operation"] == "delete_index":
            self.remove_index(name=options["name"])

        if options["operation"] == "index_database":
            self.index_database(
                batch_size=options["batch_size"],
                clear_index=options["clear_index"],
                name=options["name"],
                quiet=options["quiet"],
                use_multiprocessing=options["use_multiprocessing"],
                max_subprocesses=options["max_subprocesses"],
                recalculate_descriptors=options["recalculate_descriptors"],
            )

        if options["operation"] == "reindex_database":
            self.reindex_database(
                batch_size=options["batch_size"],
                name=options["name"],
                quiet=options["quiet"],
                use_multiprocessing=options["use_multiprocessing"],
                max_subprocesses=options["max_subprocesses"],
                recalculate_descriptors=options["recalculate_descriptors"],
            )

        if options["operation"] == "index_concepts":
            index_database_util.index_concepts(
                clear_index=options["clear_index"], batch_size=options["batch_size"]
            )

        if options["operation"] == "index_resources":
            index_database_util.index_resources(
                clear_index=options["clear_index"],
                batch_size=options["batch_size"],
                quiet=options["quiet"],
                use_multiprocessing=options["use_multiprocessing"],
                max_subprocesses=options["max_subprocesses"],
                recalculate_descriptors=options["recalculate_descriptors"],
            )

        if options["operation"] == "index_resources_by_type":
            index_database_util.index_resources_by_type(
                resource_types=options["resource_types"],
                clear_index=options["clear_index"],
                batch_size=options["batch_size"],
                quiet=options["quiet"],
                use_multiprocessing=options["use_multiprocessing"],
                max_subprocesses=options["max_subprocesses"],
                recalculate_descriptors=options["recalculate_descriptors"],
            )

        if options["operation"] == "index_resources_by_transaction":
            try:
                uuid.UUID(options["transaction"])
            except ValueError:
                logger.error(
                    "A valid transaction id is required. Use -t or --transaction , eg. -t 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'"
                )
            index_database_util.index_resources_by_transaction(
                transaction_id=options["transaction"],
                batch_size=options["batch_size"],
                quiet=options["quiet"],
                use_multiprocessing=options["use_multiprocessing"],
                max_subprocesses=options["max_subprocesses"],
                recalculate_descriptors=options["recalculate_descriptors"],
            )
        if options["operation"] == "restore_snapshot":
            self.restore_snapshot(
                options["repository_name"], options["snapshot_name"], options
            )
        if options["operation"] == "create_snapshot":
            self.create_snapshot(options["repository_name"], options["snapshot_name"])
        if options["operation"] == "list_snapshots":
            self.list_snapshots(options["repository_name"])
        if options["operation"] == "snapshot_restore_status":
            self.snapshot_restore_status()

    def register_index(self, name):
        es_index = get_index(name)
        es_index.prepare_index()

    def remove_index(self, name):
        es_index = get_index(name)
        es_index.delete_index()

    def index_database(
        self,
        batch_size,
        clear_index=True,
        name=None,
        quiet=False,
        use_multiprocessing=False,
        max_subprocesses=0,
        recalculate_descriptors=False,
    ):
        if name is not None:
            index_database_util.index_custom_indexes(
                index_name=name,
                clear_index=clear_index,
                batch_size=batch_size,
                quiet=quiet,
                use_multiprocessing=use_multiprocessing,
                max_subprocesses=max_subprocesses,
            )
        else:
            index_database_util.index_db(
                clear_index=clear_index,
                batch_size=batch_size,
                quiet=quiet,
                use_multiprocessing=use_multiprocessing,
                max_subprocesses=max_subprocesses,
                recalculate_descriptors=recalculate_descriptors,
            )

    def reindex_database(
        self,
        batch_size,
        name=None,
        quiet=False,
        use_multiprocessing=False,
        max_subprocesses=0,
        recalculate_descriptors=False,
    ):
        self.delete_indexes(name=name)
        self.setup_indexes(name=name)
        self.index_database(
            batch_size=batch_size,
            clear_index=False,
            name=name,
            quiet=quiet,
            use_multiprocessing=use_multiprocessing,
            max_subprocesses=max_subprocesses,
            recalculate_descriptors=recalculate_descriptors,
        )

    def setup_indexes(self, name=None):
        if name is None:
            prepare_terms_index(create=True)
            prepare_concepts_index(create=True)
            prepare_search_index(create=True)

            # add custom indexes
            for index in settings.ELASTICSEARCH_CUSTOM_INDEXES:
                self.register_index(index["name"])
        else:
            self.register_index(name)

    def create_snapshot(self, repository_name=None, snapshot_name=None):
        if not repository_name:
            print("Repaository name is required.  Use -rn or --repository_name")
        else:
            SearchEngineFactory().create().create_snapshot(
                repository_name, snapshot_name
            )

    def restore_snapshot(self, repository_name=None, snapshot_name=None, options=None):
        if not repository_name or not snapshot_name:
            print(
                "Snapshot name and repository name are required.  Use -sn or --snapshot_name and -rn or --repository_name"
            )
        else:
            if (
                SearchEngineFactory()
                .create()
                .check_snapshot(repository_name, snapshot_name)
            ):
                self.delete_indexes()
                SearchEngineFactory().create().restore_snapshot(
                    repository_name, snapshot_name
                )
                if SearchEngineFactory().create().restore_status() == "done":
                    snapshot_response = (
                        SearchEngineFactory()
                        .create()
                        .get_snapshot(repository_name, snapshot_name)
                    )
                    prepare_concepts_index(create=True)
                    index_database_util.index_concepts(
                        batch_size=options["batch_size"],
                    )
                    index_database_util.index_resources_by_time(
                        start_time=snapshot_response["snapshots"][0]["start_time"],
                        batch_size=options["batch_size"],
                        quiet=options["quiet"],
                        use_multiprocessing=options["use_multiprocessing"],
                        max_subprocesses=options["max_subprocesses"],
                        recalculate_descriptors=options["recalculate_descriptors"],
                    )
                else:
                    print("Snapshot restore failed, manual intervention required.")
            else:
                print("Snapshot does not exist")

    def snapshot_restore_status(self):
        print(SearchEngineFactory().create().restore_status())

    def list_snapshots(self, repository_name):
        print(SearchEngineFactory().create().list_snapshots(repository_name))

    def delete_indexes(self, name=None):
        if name is None:
            delete_terms_index()
            delete_concepts_index()
            delete_search_index()

            # remove custom indexes
            for index in settings.ELASTICSEARCH_CUSTOM_INDEXES:
                self.remove_index(index["name"])
        else:
            self.remove_index(name)
