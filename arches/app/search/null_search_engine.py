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

import logging


class NullSearchEngine(object):
    """
    A no-op stand-in for arches.app.search.search.SearchEngine, used when
    settings.ELASTICSEARCH_ENABLED is False.

    This module itself imports nothing from the ``elasticsearch`` package and
    makes no network connection, so no running cluster is needed. Note that the
    client library must still be installed: other Arches modules (e.g.
    arches.app.search.search) import it at module level.

    Write operations are silently discarded. Read operations return the same
    shapes Elasticsearch would return for an empty result, so callers that are
    not guarded by the ELASTICSEARCH_ENABLED flag degrade to "no results"
    rather than raising KeyError or TypeError.

    Snapshot operations have no meaningful no-op, so they raise.
    """

    def __init__(self, **kwargs):
        self.prefix = kwargs.pop("prefix", "").lower()
        self.es = None
        self.logger = logging.getLogger(__name__)

    def _add_prefix(self, *args, **kwargs):
        """Mirrors SearchEngine._add_prefix so index names are built identically."""

        if args:
            index = args[0].strip()
        else:
            index = kwargs.get("index", "").strip()
        if index is None or index == "":
            raise NotImplementedError("Search index not specified.")

        prefix = (
            "%s_" % self.prefix.strip()
            if self.prefix and self.prefix.strip() != ""
            else ""
        )
        ret = ["%s%s" % (prefix, idx) for idx in index.split(",")]

        index = ",".join(ret)
        if args:
            return index
        else:
            return dict(kwargs, index=index)

    def get_index_names(self):
        return []

    # Reads

    def search(self, **kwargs):
        """
        Returns an empty result in whichever shape the caller asked for:
        a get by id, an mget by list of ids, or a query.
        """

        id = kwargs.pop("id", None)

        if id:
            if isinstance(id, str):
                id = id.split(",")
                if len(id) == 1:
                    id = id[0]
            if isinstance(id, list):
                return {"docs": [{"_id": _id, "found": False} for _id in id]}
            # SearchEngine.get raises NotFoundError on a miss; None is the closest no-op.
            return None

        return {
            "took": 0,
            "timed_out": False,
            "_scroll_id": None,
            "hits": {
                "total": {"value": 0, "relation": "eq"},
                "max_score": None,
                "hits": [],
            },
            "aggregations": {},
        }

    def count(self, **kwargs):
        return 0

    # Writes

    def index_data(self, index=None, body=None, idfield=None, id=None, **kwargs):
        pass

    def bulk_index(self, data, **kwargs):
        pass

    def create_bulk_item(self, op_type="index", index=None, id=None, data=None):
        return {
            "_op_type": op_type,
            "_index": self._add_prefix(index),
            "_id": id,
            "_source": data,
        }

    def create_index(self, **kwargs):
        pass

    def create_mapping(
        self, index, fieldname="", fieldtype="string", fieldindex=None, body=None
    ):
        pass

    def delete(self, **kwargs):
        pass

    def delete_index(self, **kwargs):
        pass

    def refresh(self, **kwargs):
        pass

    def BulkIndexer(outer_self, batch_size=500, **kwargs):
        class _NullBulkIndexer(object):
            def add(self, op_type="index", index=None, id=None, data=None):
                pass

            def close(self):
                pass

            def __enter__(self, **kwargs):
                return self

            def __exit__(self, type, value, traceback):
                return self.close()

        return _NullBulkIndexer()

    # Snapshots

    def _unavailable(self, operation):
        raise NotImplementedError(
            "'%s' requires Elasticsearch, but ELASTICSEARCH_ENABLED is False."
            % operation
        )

    def create_snapshot(self, repository, snapshot=None, **kwargs):
        self._unavailable("create_snapshot")

    def check_snapshot(self, repository, snapshot, **kwargs):
        self._unavailable("check_snapshot")

    def restore_snapshot(self, repository, snapshot, **kwargs):
        self._unavailable("restore_snapshot")

    def get_snapshot(self, repository_name, snapshot_name, **kwargs):
        self._unavailable("get_snapshot")

    def restore_status(self):
        self._unavailable("restore_status")

    def list_snapshots(self, repository, **kwargs):
        self._unavailable("list_snapshots")
