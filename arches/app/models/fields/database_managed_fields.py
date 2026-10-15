from django.db import models
from django.db.models.expressions import DatabaseDefault
from django.db.models.functions import Now


class NextVal(models.Func):
    """nextval() on a named sequence, usable as a db_default."""

    function = "nextval"
    template = "%(function)s('%(sequence_name)s'::regclass)"
    output_field = models.BigIntegerField()

    def __init__(self, sequence_name, **extra):
        if not sequence_name.isidentifier():
            raise ValueError(f"Invalid sequence name: {sequence_name!r}")
        super().__init__(sequence_name=sequence_name, **extra)


class DatabaseManagedFieldMixin:
    """
    A field whose value is owned by the database: populated by its db_default
    on insert and protected/maintained by a trigger on update (see the
    __arches_manage_row_metadata() trigger function). The ORM never writes
    a value of its own; it only reads back what the database decided via
    RETURNING.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("editable", False)
        super().__init__(*args, **kwargs)

    def get_default(self):
        # Unsaved instances hold None rather than a DatabaseDefault
        # placeholder, so they can still be serialized.
        return None

    def pre_save(self, model_instance, add):
        if add:
            # Omits the column from the INSERT so db_default applies.
            return DatabaseDefault(self.db_default, output_field=self)
        # A no-op assignment (the trigger decides the real value) that makes
        # Django return the stored value via RETURNING.
        return models.F(self.attname)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs.pop("db_default", None)
        if kwargs.get("editable") is False:
            del kwargs["editable"]
        return name, path, args, kwargs


class DatabaseManagedFieldsModelMixin:
    """
    Skips ORM uniqueness checks on database-managed fields. The ORM never
    writes their values, so e.g. a copied instance still carrying the
    original's id would otherwise fail full_clean() despite saving fine.
    """

    def validate_unique(self, exclude=None):
        database_managed_field_names = {
            field.name
            for field in self._meta.concrete_fields
            if isinstance(field, DatabaseManagedFieldMixin)
        }
        super().validate_unique(
            exclude={*(exclude or ()), *database_managed_field_names}
        )


class NonPrimaryIdentityField(DatabaseManagedFieldMixin, models.BigIntegerField):
    """
    A unique, sequence-backed bigint that behaves like an AutoField but is not
    the primary key.
    """

    def __init__(self, *args, sequence_name, **kwargs):
        self.sequence_name = sequence_name
        kwargs["db_default"] = NextVal(sequence_name)
        kwargs.setdefault("unique", True)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["sequence_name"] = self.sequence_name
        if kwargs.get("unique") is True:
            del kwargs["unique"]
        return name, path, args, kwargs


class DatabaseTimestampField(DatabaseManagedFieldMixin, models.DateTimeField):
    def __init__(self, *args, **kwargs):
        kwargs["db_default"] = Now()
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        # Unlike ids, an explicit timestamp is kept on insert (matching the
        # trigger), so imports can preserve original creation times.
        if add and (value := getattr(model_instance, self.attname)) is not None:
            return value
        return super().pre_save(model_instance, add)
