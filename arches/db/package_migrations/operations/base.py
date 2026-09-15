"""Base class for package-data migration operations.

Subclasses are public API: generated migration files import them by dotted path
and ship inside third-party wheels, so constructor signatures are additive-only.
"""

import inspect

from django.db.migrations.operations.base import Operation


class PackageOperation(Operation):
    # Package operations mutate rows and JSONB, not DDL. collect_sql would emit
    # a placeholder comment for them (and skip state_forwards), so there is no
    # sqlpkgmigrate; `migratepkg --plan` prints describe() instead.
    reduces_to_sql = False

    # Django's default. An operation that needs to escape the migration's
    # transaction cannot do it from here: only Migration.atomic = False achieves
    # that, which the autodetector sets when it sees requires_non_atomic_migration.
    atomic = False

    # Chunked data operations cannot run inside the migration transaction.
    requires_non_atomic_migration = False

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if inspect.isabstract(cls) or cls.__name__.startswith("_"):
            return

        # D6: Migration.unapply() raises IrreversibleError in phase 1 only when
        # reversible is False. A reversible=True operation whose backwards is
        # unimplemented instead lets phase 2 partially reverse the database and
        # then blow up, so the two must agree at class-definition time.
        implements_backwards = (
            cls.database_backwards is not PackageOperation.database_backwards
        )
        if cls.reversible and not implements_backwards:
            raise TypeError(
                "%s sets reversible = True but does not implement "
                "database_backwards(). Implement it, or declare "
                "reversible = False." % cls.__name__
            )

        for name in ("describe", "migration_name_fragment"):
            if getattr(cls, name, None) is getattr(PackageOperation, name, None):
                raise TypeError("%s must define %s." % (cls.__name__, name))

    def deconstruct(self):
        """Emit every constructor parameter explicitly.

        Operation.__new__ captures the raw call arguments before __init__ runs,
        so the inherited deconstruct() omits anything the caller left defaulted
        and reports pre-normalization values. Reading from self instead makes
        generated migration files fully self-describing.

        OperationWriter silently drops any kwarg whose name is not an __init__
        parameter, so attribute names must match parameter names -- a mismatch
        surfaces here as AttributeError rather than as a quietly empty call in a
        generated file.
        """
        kwargs = {}
        for name in self._constructor_parameters():
            kwargs[name] = getattr(self, name)
        return (self.__class__.__name__, [], kwargs)

    @classmethod
    def _constructor_parameters(cls):
        signature = inspect.signature(cls.__init__)
        return [
            name
            for name, parameter in signature.parameters.items()
            if name != "self"
            and parameter.kind not in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD)
        ]

    def qs(self, model, schema_editor):
        """Every query must be bound to the migration's connection.

        The executor opens its transaction and records the ledger row on the
        selected alias; a bare Model.objects would execute on `default`, outside
        that transaction.
        """
        return model.objects.using(schema_editor.connection.alias)

    def state_forwards(self, app_label, state):
        raise NotImplementedError(
            "%s must implement state_forwards()." % self.__class__.__name__
        )

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        raise NotImplementedError(
            "%s must implement database_forwards()." % self.__class__.__name__
        )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        raise NotImplementedError("%s is not reversible." % self.__class__.__name__)

    def describe(self):
        raise NotImplementedError

    @property
    def migration_name_fragment(self):
        raise NotImplementedError
