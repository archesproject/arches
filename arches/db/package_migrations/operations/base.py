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


class _AlterRowOperation(PackageOperation):
    """Shared implementation for the Alter* family.

    All six do the same thing: write a dict of field changes onto one row, and
    reverse by reading the previous values back out of the replayed state. The
    operation carries only the NEW values -- unapply() phase 1 replays state
    forwards, so to_state still holds the old ones, exactly as Django's
    AlterField recovers the previous field definition.

    Subclasses set ``model``, ``state_collection`` and ``pk_attribute``.
    """

    reversible = True

    model = None
    state_collection = None  # "nodes", "cards", ...
    pk_attribute = None  # the __init__ parameter holding the row's pk

    def __init__(self, graphid, changes):
        self.graphid = graphid
        self.changes = changes

    @property
    def _pk(self):
        return getattr(self, self.pk_attribute)

    def _entry(self, state):
        return (
            state.graph(self.graphid)
            .setdefault(self.state_collection, {})
            .setdefault(str(self._pk), {})
        )

    def state_forwards(self, app_label, state):
        self._entry(state).update(self.changes)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        self.qs(self.model, schema_editor).filter(pk=self._pk).update(**self.changes)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        previous = self._entry(to_state)
        self.qs(self.model, schema_editor).filter(pk=self._pk).update(
            **{field: previous.get(field) for field in self.changes}
        )


class _RowOperation(PackageOperation):
    """Shared plumbing for the per-row operations.

    Every one of them carries the row as a single ``fields`` dict rather than an
    enumerated signature. That dict IS the canonical projection of the row, so it
    cannot drift from the model the way a hand-maintained parameter list does,
    and adding a column to a model never changes a public constructor signature.

    (A ``**kwargs`` signature would not work: get_func_args excludes VAR_KEYWORD,
    so OperationWriter silently drops every extra kwarg and writes an empty call.
    A single dict parameter is the only shape that both stays open and
    round-trips.)
    """

    model = None
    state_collection = None
    pk_field = None
    # NodeGroup and CardXNodeXWidget rows carry no graph FK.
    has_graph_fk = True

    # Renders one key per line in generated migrations instead of one long dict.
    serialization_expand_args = ["fields"]

    def __init__(self, graphid, fields):
        self.graphid = graphid
        self.fields = fields

    def _complete_fields(self):
        """Fill any column the caller left out from the model's own default.

        The canonical projection always supplies every field, but a hand-written
        migration reasonably names only the ones it cares about. Defaults come
        from the model rather than from a constructor signature, so they cannot
        drift from it.
        """
        from arches.db.package_migrations.canonical import fields_for

        completed = {}
        missing_required = []
        for name in fields_for(self.model):
            if name in self.fields:
                completed[name] = self.fields[name]
                continue
            field = self.model._meta.get_field(name.removesuffix("_id"))
            if field.has_default():
                completed[name] = field.get_default()
            elif field.null or field.blank:
                completed[name] = None
            else:
                # Guessing a value for a NOT NULL column with no default would be
                # inventing package content. Say so here rather than surfacing an
                # IntegrityError from deep inside the apply.
                missing_required.append(name)
        if missing_required:
            raise ValueError(
                "%s is missing required field(s) %s for %s. Supply them in fields."
                % (
                    type(self).__name__,
                    ", ".join(sorted(missing_required)),
                    self.model.__name__,
                )
            )
        return completed

    @property
    def _pk(self):
        return str(self.fields[self.pk_field])

    def _collection(self, state):
        return state.graph(self.graphid).setdefault(self.state_collection, {})

    def _row_kwargs(self):
        kwargs = self._complete_fields()
        if self.has_graph_fk:
            kwargs["graph_id"] = self.graphid
        return kwargs

    def _create_row(self, schema_editor):
        self.qs(self.model, schema_editor).create(**self._row_kwargs())

    def _delete_row(self, schema_editor):
        self.qs(self.model, schema_editor).filter(pk=self._pk).delete()


class _CreateRowOperation(_RowOperation):
    reversible = True

    def state_forwards(self, app_label, state):
        # Store the completed row, so replayed state and the database agree.
        self._collection(state)[self._pk] = self._complete_fields()

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        self._create_row(schema_editor)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        self._delete_row(schema_editor)


class _DeleteRowOperation(_RowOperation):
    """Reversible because unapply() phase 1 replays state forwards, so to_state
    still holds the row's full definition to recreate from."""

    reversible = True

    def __init__(self, graphid, pk):
        self.graphid = graphid
        self.pk = pk

    @property
    def _pk(self):
        return str(self.pk)

    def state_forwards(self, app_label, state):
        del self._collection(state)[self._pk]

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        self._delete_row(schema_editor)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        self.fields = self._collection(to_state)[self._pk]
        self._create_row(schema_editor)
