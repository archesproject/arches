from django.db.models import Lookup
from django.db.models.lookups import Contains, IContains
from psycopg2.extensions import AsIs, QuotedString

from arches_querysets.fields import Cardinality1JSONField, CardinalityNField


class JSONPathFilter:
    def process_rhs(self, compiler, connection):
        rhs, params = super().process_rhs(compiler, connection)
        if '"' in params[0]:
            raise ValueError("Double quotes are not allowed in JSONPath filters.")
        quoted = AsIs(QuotedString(params[0]).getquoted().decode()[1:-1])
        return rhs, (quoted,)


@CardinalityNField.register_lookup
class ArrayContains(Contains):
    """Provide a string. Adapted from https://code.djangoproject.com/ticket/34942"""

    def as_sql(self, compiler, connection):
        # Avoid connection.ops.lookup_cast in BuiltinLookup.process_lhs()
        lhs, lhs_params = Lookup.process_lhs(self, compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return (
            "EXISTS(SELECT * FROM UNNEST(%s) AS a WHERE a LIKE %s)" % (lhs, rhs),
            params,
        )


@CardinalityNField.register_lookup
class ArrayIContains(IContains):
    """Provide a string. Adapted from https://code.djangoproject.com/ticket/34942"""

    def as_sql(self, compiler, connection):
        # Avoid connection.ops.lookup_cast in BuiltinLookup.process_lhs()
        lhs, lhs_params = Lookup.process_lhs(self, compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return (
            "EXISTS(SELECT * FROM UNNEST(%s) AS a WHERE a ILIKE %s)" % (lhs, rhs),
            params,
        )


@Cardinality1JSONField.register_lookup
class AnyLanguageStartsWith(JSONPathFilter, Lookup):
    lookup_name = "any_lang_startswith"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return "%s @? '$.*.value ? (@ starts with \"%s\")'" % (lhs, rhs), params


@Cardinality1JSONField.register_lookup
class AnyLanguageIStartsWith(JSONPathFilter, Lookup):
    lookup_name = "any_lang_istartswith"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return (
            '%s @? \'$.*.value ? (@ like_regex "^%s" flag "i")\'' % (lhs, rhs),
            params,
        )


@Cardinality1JSONField.register_lookup
class AnyLanguageContains(JSONPathFilter, Lookup):
    lookup_name = "any_lang_contains"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return "%s @? '$.*.value ? (@ like_regex \"%s\")'" % (lhs, rhs), params


@Cardinality1JSONField.register_lookup
class AnyLanguageIContains(JSONPathFilter, Lookup):
    lookup_name = "any_lang_icontains"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return '%s @? \'$.*.value ? (@ like_regex "%s" flag "i")\'' % (lhs, rhs), params


@CardinalityNField.register_lookup
class ArrayAnyLanguageEquals(JSONPathFilter, Lookup):
    lookup_name = "any_lang"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return "TO_JSONB(%s) @? '$[*].*.value ? (@ == \"%s\")'" % (lhs, rhs), params


@CardinalityNField.register_lookup
class ArrayAnyLanguageContains(JSONPathFilter, Lookup):
    lookup_name = "any_lang_contains"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return (
            "TO_JSONB(%s) @? '$[*].*.value ? (@ like_regex \"%s\")'" % (lhs, rhs),
            params,
        )


@CardinalityNField.register_lookup
class ArrayAnyLanguageIContains(JSONPathFilter, Lookup):
    lookup_name = "any_lang_icontains"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return (
            'TO_JSONB(%s) @? \'$[*].*.value ? (@ like_regex "%s" flag "i")\''
            % (lhs, rhs),
            params,
        )


@CardinalityNField.register_lookup
class ArrayAnyLanguageStartsWith(JSONPathFilter, Lookup):
    lookup_name = "any_lang_startswith"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return (
            "TO_JSONB(%s) @? '$[*].*.value ? (@ starts with \"%s\")'" % (lhs, rhs),
            params,
        )


@CardinalityNField.register_lookup
class ArrayAnyLanguageIStartsWith(JSONPathFilter, Lookup):
    lookup_name = "any_lang_istartswith"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return (
            'TO_JSONB(%s) @? \'$[*].*.value ? (@ like_regex "^%s" flag "i")\''
            % (lhs, rhs),
            params,
        )
