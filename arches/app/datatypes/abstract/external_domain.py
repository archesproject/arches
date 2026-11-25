from abc import abstractmethod
from functools import cached_property

from arches.app.datatypes.base import BaseDataType
from arches.app.search.elasticsearch_dsl_builder import Term


class BaseExternalDomainDataType(BaseDataType):
    """Base datatype for domain-like values sourced from an external DB table.

    Subclasses define which table/queryset to use, how to extract the stored
    value (option id) and display value from each record. Records can be
    looked up by either id or display text.
    """

    @abstractmethod
    def get_options_queryset(self):
        """Return a Django QuerySet that yields all valid option records."""

    @abstractmethod
    def get_option_id(self, record):
        """Return the value that gets stored in tile data."""

    @abstractmethod
    def get_option_display(self, record):
        """Return the human-readable display string."""

    @abstractmethod
    def get_invalid_message(self, value):
        """Return a ``(message, title)`` tuple for a failed validation."""

    @cached_property
    def _options_index(self):
        index = {}
        for record in self.get_options_queryset():
            index[self.get_option_id(record)] = record
            index[self.get_option_display(record)] = record
        return index

    def lookup_record(self, value):
        if isinstance(value, list) and len(value) > 0:
            value = value[0]
        if not value:
            return None
        return self._options_index.get(value)

    def validate(
        self,
        value,
        row_number=None,
        source="",
        node=None,
        nodeid=None,
        strict=False,
        **kwargs,
    ):
        errors = []
        if value is not None:
            record = self.lookup_record(value)
            if not record:
                message, title = self.get_invalid_message(value)
                errors.append(
                    self.create_error_message(value, source, row_number, message, title)
                )
        return errors

    def transform_value_for_tile(self, value, **kwargs):
        if value is not None:
            record = self.lookup_record(value)
            if record:
                return self.get_option_id(record)
        return None

    def get_display_value(self, tile, node, **kwargs):
        data = self.get_tile_data(tile)
        if data:
            record = self.lookup_record(data[str(node.nodeid)])
            if record:
                return self.get_option_display(record)
        return ""

    def append_search_filters(self, value, node, query, request):
        try:
            operation = value["op"]
            if operation in ("null", "not_null"):
                self.append_null_search_filters(value, node, query, request)
            elif value["val"] != "":
                field = f"tiles.data.{str(node.pk)}"
                match_query = Term(field=field, term=value["val"])
                if "!" not in operation:
                    query.must(match_query)
                else:
                    query.must_not(match_query)
        except KeyError:
            pass
