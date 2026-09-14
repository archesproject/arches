from django.db.models.lookups import Lookup, PatternLookup, Transform
from psycopg2.extensions import AsIs, QuotedString

from arches_querysets.fields import (
    CardinalityNResourceInstanceField,
    CardinalityNResourceInstanceListField,
    CardinalityNLocalizedStringField,
    CardinalityNTextField,
    ResourceInstanceListField,
    ResourceInstanceField,
    LocalizedStringField,
)


class JSONPathFilter:
    def process_rhs(self, compiler, connection):
        rhs, params = super().process_rhs(compiler, connection)
        if '"' in params[0]:
            raise ValueError("Double quotes are not allowed in JSONPath filters.")
        quoted = AsIs(QuotedString(params[0]).getquoted().decode()[1:-1])
        return rhs, (quoted,)


@CardinalityNTextField.register_lookup
class AnyContains(PatternLookup):
    """Provide a single string. Adapted from https://code.djangoproject.com/ticket/34942"""

    lookup_name = "any_contains"
    like_operator = "LIKE"

    def as_sql(self, compiler, connection):
        # Avoid connection.ops.lookup_cast in BuiltinLookup.process_lhs()
        lhs, lhs_params = Lookup.process_lhs(self, compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return (
            "EXISTS(SELECT * FROM UNNEST(%s) AS a WHERE a %s %s)"
            % (lhs, self.like_operator, rhs),
            params,
        )


@CardinalityNTextField.register_lookup
class AnyIContains(AnyContains):
    lookup_name = "any_icontains"
    like_operator = "ILIKE"


@LocalizedStringField.register_lookup
class AnyLanguageStartsWith(JSONPathFilter, Lookup):
    lookup_name = "any_lang_startswith"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return "%s @? '$.*.value ? (@ starts with \"%s\")'" % (lhs, rhs), params


@LocalizedStringField.register_lookup
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


@LocalizedStringField.register_lookup
class AnyLanguageContains(JSONPathFilter, Lookup):
    lookup_name = "any_lang_contains"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return "%s @? '$.*.value ? (@ like_regex \"%s\")'" % (lhs, rhs), params


@LocalizedStringField.register_lookup
class AnyLanguageIContains(JSONPathFilter, Lookup):
    lookup_name = "any_lang_icontains"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return '%s @? \'$.*.value ? (@ like_regex "%s" flag "i")\'' % (lhs, rhs), params


@ResourceInstanceField.register_lookup
class ResourceInstanceId(Transform):
    lookup_name = "id"
    template = "(%(expressions)s -> 0 -> 'resourceId')"


@CardinalityNResourceInstanceField.register_lookup
class ArrayResourceInstanceId(JSONPathFilter, Lookup):
    lookup_name = "ids_contain"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return (
            "TO_JSONB(%s) @? '$[*][*].resourceId ? (@ == \"%s\")'" % (lhs, rhs),
            params,
        )


@CardinalityNResourceInstanceListField.register_lookup
class ArrayAnyResourceInstanceId(JSONPathFilter, Lookup):
    lookup_name = "ids_contain"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return (
            "TO_JSONB(%s) @? '$[*][*][*].resourceId ? (@ == \"%s\")'" % (lhs, rhs),
            params,
        )


@ResourceInstanceListField.register_lookup
class ResourceInstanceListContains(JSONPathFilter, Lookup):
    lookup_name = "contains"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return "%s @? '$[*].resourceId ? (@ == \"%s\")'" % (lhs, rhs), params


@CardinalityNLocalizedStringField.register_lookup
class ArrayAnyLanguageEquals(JSONPathFilter, Lookup):
    lookup_name = "any_lang"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return "TO_JSONB(%s) @? '$[*].*.value ? (@ == \"%s\")'" % (lhs, rhs), params


@CardinalityNLocalizedStringField.register_lookup
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


@CardinalityNLocalizedStringField.register_lookup
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


@CardinalityNLocalizedStringField.register_lookup
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


@CardinalityNLocalizedStringField.register_lookup
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
