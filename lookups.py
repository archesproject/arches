from django.contrib.postgres.fields import ArrayField
from django.db.models import JSONField, Lookup
from psycopg2.extensions import AsIs, QuotedString


class JSONPathFilter:
    def process_rhs(self, compiler, connection):
        rhs, params = super().process_rhs(compiler, connection)
        if '"' in params[0]:
            raise ValueError("Double quotes are not allowed in JSONPath filters.")
        quoted = AsIs(QuotedString(params[0]).getquoted().decode()[1:-1])
        return rhs, (quoted,)


## JSONField lookups (Cardinality 1)


@JSONField.register_lookup
class AnyLanguageEquals(JSONPathFilter, Lookup):
    lookup_name = "any_lang"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return "%s @? '$.*.value ? (@ == \"%s\")'" % (lhs, rhs), params


@JSONField.register_lookup
class AnyLanguageContains(JSONPathFilter, Lookup):
    lookup_name = "any_lang_contains"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return "%s @? '$.*.value ? (@ like_regex \"%s\")'" % (lhs, rhs), params


@JSONField.register_lookup
class AnyLanguageIContains(JSONPathFilter, Lookup):
    lookup_name = "any_lang_icontains"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return '%s @? \'$.*.value ? (@ like_regex "%s" flag "i")\'' % (lhs, rhs), params


@JSONField.register_lookup
class AnyLanguageStartsWith(JSONPathFilter, Lookup):
    lookup_name = "any_lang_startswith"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return "%s @? '$.*.value ? (@ starts with \"%s\")'" % (lhs, rhs), params


## ArrayField lookups (Cardinality N)


@ArrayField.register_lookup
class ArrayAnyLanguageEquals(JSONPathFilter, Lookup):
    lookup_name = "any_lang"

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return "TO_JSONB(%s) @? '$[*].*.value ? (@ == \"%s\")'" % (lhs, rhs), params


@ArrayField.register_lookup
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


@ArrayField.register_lookup
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


@ArrayField.register_lookup
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
