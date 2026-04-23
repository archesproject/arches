from abc import abstractmethod

from django.db.models import Q
from django.utils.translation import gettext as _

from arches.app.datatypes.base import BaseDataType
from arches.app.search.elasticsearch_dsl_builder import Term


class BaseExternalDomainDataType(BaseDataType):
    """Base datatype for domain-like values sourced from an external DB table.

    Subclasses define which table/queryset to use, how to extract the stored
    value (option id) and display value from each record, and how records are
    looked up by either id or display text.
    """

    def __init__(self, model=None):
        super().__init__(model=model)
        self._record_cache = {}

    @abstractmethod
    def get_options_queryset(self):
        """Return a Django QuerySet that yields all valid option records."""

    @abstractmethod
    def get_option_id(self, record):
        """Return the value that gets stored in tile data for *record*."""

    @abstractmethod
    def get_option_display(self, record):
        """Return the human-readable display string for *record*."""

    @abstractmethod
    def get_lookup_filter(self, value):
        """Return a ``Q`` object that filters the options queryset for *value*.

        The filter should match on both the stored id field and the display
        field so that callers can pass either form.
        """

    @abstractmethod
    def get_invalid_message(self, value):
        """Return a ``(message, title)`` tuple for a failed validation."""

    def lookup_record(self, value):
        """Look up a single option record by id or display text.

        Results are cached for the lifetime of this datatype instance.
        Returns ``None`` when no match is found.
        """
        if isinstance(value, list) and len(value) > 0:
            value = value[0]
        if not value:
            return None
        if value in self._record_cache:
            return self._record_cache[value]

        record = (
            self.get_options_queryset().filter(self.get_lookup_filter(value)).first()
        )

        if record:
            option_id = self.get_option_id(record)
            display = self.get_option_display(record)
            self._record_cache[option_id] = record
            self._record_cache[display] = record
        return record

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

    def is_a_literal_in_rdf(self):
        return True
