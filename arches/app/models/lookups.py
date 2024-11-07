from django.db.models import JSONField, Lookup


# TODO: manually merging parameters is usually a no-no,
# but are these already safe via the \" quotes?
# Look into sql.Identifier or AsIs().

# Seems like a Django bug that I need to override get_db_prep_lookup(). TODO: Ask.


@JSONField.register_lookup
class AnyLanguageEquals(Lookup):
    lookup_name = "any_lang"

    def get_db_prep_lookup(self, value, connection):
        return ("%s", (value,))

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        placeholder = "%s @? '$.*.value ? (@ == \"" + rhs_params[0] + "\")'"
        return placeholder % (lhs,), lhs_params


@JSONField.register_lookup
class AnyLanguageContains(Lookup):
    lookup_name = "any_lang_contains"

    def get_db_prep_lookup(self, value, connection):
        return ("%s", (value,))

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        placeholder = "%s @? '$.*.value ? (@ like_regex \"" + rhs_params[0] + "\")'"
        return placeholder % (lhs,), lhs_params


@JSONField.register_lookup
class AnyLanguageIContains(Lookup):
    lookup_name = "any_lang_icontains"

    def get_db_prep_lookup(self, value, connection):
        return ("%s", (value,))

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        placeholder = (
            "%s @? '$.*.value ? (@ like_regex \"" + rhs_params[0] + '" flag "i")\''
        )
        return placeholder % (lhs,), lhs_params


@JSONField.register_lookup
class AnyLanguageStartsWith(Lookup):
    lookup_name = "any_lang_startswith"

    def get_db_prep_lookup(self, value, connection):
        return ("%s", (value,))

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        placeholder = "%s @? '$.*.value ? (@ starts with \"" + rhs_params[0] + "\")'"
        return placeholder % (lhs,), lhs_params
