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

import csv
import time
import uuid
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from elasticsearch import ApiError, ConnectionTimeout, TransportError
from django.core.management.base import BaseCommand, CommandError

from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.search.mappings import RESOURCES_INDEX
from arches.app.search.search_engine_factory import SearchEngineFactory

FILTER_PATH = "_scroll_id,hits.hits._id,hits.hits.fields.graph_id"
RETRY_STATUSES = {429, 502, 503, 504}
MAX_RETRIES = 3
MIN_BATCH_SIZE = 500


class Command(BaseCommand):
    help = (
        "Compares resource instances in Postgres with the Elasticsearch resources index. "
        "Writes missing_from_es.csv (in the database, not indexed), orphaned_in_es.csv "
        "(indexed, not in the database) and summary.txt to the output directory. "
        "The UUID space is processed in hex-prefix partitions to bound memory use. "
        "Scroll slices are auto-tuned from the shard and CPU counts unless --slices is given; "
        "timed-out partitions are retried with a smaller batch size."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            default=None,
            help="Directory for the reports. Default: ./es_index_diff_<YYYYmmdd_HHMMSS>",
        )
        parser.add_argument(
            "--partitions",
            type=int,
            choices=[1, 16, 256],
            default=16,
            help="Number of UUID hex-prefix partitions (more = less memory). Default: 16",
        )
        parser.add_argument(
            "--slices",
            type=int,
            default=None,
            help="Parallel scroll slices per partition. Default: auto "
            "(min(shards, cluster CPUs), or min(shards, 2) if CPUs can't be read)",
        )
        parser.add_argument(
            "--request-timeout",
            type=float,
            default=120,
            help="Elasticsearch request timeout in seconds. Default: 120",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=10000,
            help="Elasticsearch scroll page size. Default: 10000",
        )
        parser.add_argument(
            "--scroll",
            default="5m",
            help="Elasticsearch scroll keep-alive. Default: 5m",
        )
        parser.add_argument(
            "--include-system-settings",
            action="store_true",
            help="Include the system settings resource, which Arches does not index.",
        )

    def handle(self, *args, **options):
        if not settings.ELASTICSEARCH_ENABLED:
            raise CommandError(
                "The 'es_index_diff' command requires Elasticsearch, but ELASTICSEARCH_ENABLED is False."
            )

        if not 1 <= options["batch_size"] <= 10000:
            raise CommandError("--batch-size must be between 1 and 10000.")
        if options["slices"] is not None and options["slices"] < 1:
            raise CommandError("--slices must be at least 1.")

        self.batch_size = options["batch_size"]
        self.scroll = options["scroll"]
        self.se = SearchEngineFactory().create()
        self.es = self.se.es.options(request_timeout=options["request_timeout"])
        self.index = self.se._add_prefix(RESOURCES_INDEX)
        self.slices = options["slices"] or self.auto_slices()

        out_dir = Path(
            options["output_dir"] or f"./es_index_diff_{datetime.now():%Y%m%d_%H%M%S}"
        )
        out_dir.mkdir(parents=True, exist_ok=True)

        db_query = models.ResourceInstance.objects.all()
        if not options["include_system_settings"]:
            db_query = db_query.exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_ID)
        self.db_query = db_query

        n = options["partitions"]
        width = {1: 0, 16: 1, 256: 2}[n]
        prefixes = [f"{i:0{width}x}" for i in range(n)] if width else [""]

        es_scrolled = es_dupes = missing_total = orphan_total = 0
        missing_by_graph = Counter()
        with (
            open(out_dir / "missing_from_es.csv", "w", newline="") as mf,
            open(out_dir / "orphaned_in_es.csv", "w", newline="") as of,
        ):
            missing_csv, orphan_csv = csv.writer(mf), csv.writer(of)
            missing_csv.writerow(["resourceinstanceid", "graphid"])
            orphan_csv.writerow(["resourceinstanceid", "graph_id"])

            for prefix in prefixes:
                es_docs, scrolled = self.fetch_es_with_retry(prefix)
                db_docs = self.fetch_db(prefix)
                missing = sorted(db_docs.keys() - es_docs.keys())
                orphaned = sorted(es_docs.keys() - db_docs.keys())
                missing_csv.writerows((i, db_docs[i]) for i in missing)
                orphan_csv.writerows((i, es_docs[i]) for i in orphaned)
                missing_by_graph.update(db_docs[i] for i in missing)

                es_scrolled += scrolled
                es_dupes += scrolled - len(es_docs)
                missing_total += len(missing)
                orphan_total += len(orphaned)
                self.stdout.write(
                    f"[{prefix or 'all'}] db={len(db_docs)} es={len(es_docs)} "
                    f"missing={len(missing)} orphaned={len(orphaned)}"
                )

        es_count = self.es.count(index=self.index)["count"]
        lines = [
            f"ES index: {self.index}",
            f"Postgres resources: {self.db_query.count()}",
            f"ES _count: {es_count}",
            f"ES docs scrolled: {es_scrolled}",
            f"ES duplicate ids: {es_dupes}",
            f"Missing from ES: {missing_total}",
            f"Orphaned in ES: {orphan_total}",
            "Missing by graphid:",
            *(f"  {g}: {c}" for g, c in missing_by_graph.most_common()),
        ]
        if es_scrolled != es_count:
            warning = (
                f"WARNING: scrolled {es_scrolled} ES docs but _count is {es_count}. "
                "Docs with a missing or non-hex resourceinstanceid are not covered "
                "by the prefix partitions, or the index changed during the run."
            )
            self.stderr.write(self.style.WARNING(warning))
            lines.append(warning)
        (out_dir / "summary.txt").write_text("\n".join(lines) + "\n")
        self.stdout.write("\n".join(lines))
        self.stdout.write(f"Reports written to {out_dir}")

    def fetch_db(self, prefix):
        query = self.db_query
        if prefix:
            width = 32 - len(prefix)
            lo = int(prefix.ljust(32, "0"), 16)
            hi = lo + 16**width
            query = query.filter(resourceinstanceid__gte=uuid.UUID(int=lo))
            if hi < 1 << 128:
                query = query.filter(resourceinstanceid__lt=uuid.UUID(int=hi))
        return {
            str(rid).lower(): str(gid).lower()
            for rid, gid in query.values_list(
                "resourceinstanceid", "graph_id"
            ).iterator(chunk_size=self.batch_size)
        }

    @staticmethod
    def pick_slices(shards, cpus):
        """Slices beyond the shard count force costly per-doc _id filtering."""
        return max(1, min(shards, cpus or 2))

    def auto_slices(self):
        shards = self.es.search(index=self.index, size=0, filter_path="_shards.total")[
            "_shards"
        ]["total"]
        try:
            stats = self.es.cluster.stats(filter_path="nodes.os.allocated_processors")
            cpus, reason = stats["nodes"]["os"]["allocated_processors"], None
        except (ApiError, TransportError, KeyError, TypeError) as e:
            cpus, reason = None, getattr(e, "status_code", type(e).__name__)
        slices = self.pick_slices(shards, cpus)
        self.stdout.write(
            f"slices={slices} (shards={shards}, cpus={cpus or f'unknown: {reason}'})"
        )
        return slices

    def fetch_es_with_retry(self, prefix):
        """Retries the whole partition with a smaller page size on timeouts/overload."""
        for attempt in range(MAX_RETRIES + 1):
            try:
                return self.fetch_es(prefix)
            except (ConnectionTimeout, ApiError) as e:
                retryable = isinstance(e, ConnectionTimeout) or (
                    e.status_code in RETRY_STATUSES
                )
                if not retryable or attempt == MAX_RETRIES:
                    raise
                self.batch_size = max(self.batch_size // 2, MIN_BATCH_SIZE)
                self.stderr.write(
                    f"[{prefix or 'all'}] {type(e).__name__}; retry {attempt + 1}/{MAX_RETRIES} "
                    f"with batch size {self.batch_size}"
                )
                time.sleep(2**attempt)

    def fetch_es(self, prefix):
        """Returns ({id: graph_id}, number of hits scrolled including duplicates)."""
        docs = {}
        with ThreadPoolExecutor(max_workers=self.slices) as pool:
            results = pool.map(
                lambda i: self.scroll_slice(prefix, i), range(self.slices)
            )
            scrolled = 0
            for hits in results:
                scrolled += len(hits)
                docs.update(hits)
        return docs, scrolled

    def scroll_slice(self, prefix, slice_id):
        """Returns a list of (_id, graph_id) tuples so duplicates can be counted."""
        es = self.es
        kwargs = dict(
            index=self.index,
            size=self.batch_size,
            source=False,
            docvalue_fields=["graph_id"],
            sort=["_doc"],
            query=(
                {"prefix": {"resourceinstanceid": prefix}}
                if prefix
                else {"match_all": {}}
            ),
            scroll=self.scroll,
            filter_path=FILTER_PATH,
        )
        if self.slices > 1:
            kwargs["slice"] = {"id": slice_id, "max": self.slices}

        hits, scroll_id = [], None
        try:
            resp = es.search(**kwargs)
            while True:
                scroll_id = resp.get("_scroll_id", scroll_id)
                page = resp.get("hits", {}).get("hits", [])
                if not page:
                    break
                hits.extend(
                    (
                        h["_id"].lower(),
                        (h.get("fields", {}).get("graph_id") or [""])[0].lower(),
                    )
                    for h in page
                )
                resp = es.scroll(
                    scroll_id=scroll_id, scroll=self.scroll, filter_path=FILTER_PATH
                )
        finally:
            if scroll_id:
                es.options(ignore_status=404).clear_scroll(scroll_id=scroll_id)
        return hits
