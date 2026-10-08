"""Base classes for package migration operations.

Subclasses are public API imported by generated migrations, so constructor
signatures are additive-only.
"""

import inspect

from django.db.migrations.operations.base import Operation
from django.utils.inspect import get_func_args

from arches.db.package_migrations.state import collection_for, fields_for

DEFAULT_BATCH_SIZE = 5000


class PackageMigrationError(Exception):
    pass


def keyset_batches(queryset, pk_field, batch_size):
    """Yield lists of primary keys in pk order, resuming after the last one seen."""
    last = None
    while True:
        batch = queryset
        if last is not None:
            batch = batch.filter(**{f"{pk_field}__gt": last})
        keys = list(
            batch.order_by(pk_field).values_list(pk_field, flat=True)[:batch_size]
        )
        if not keys:
            return
        yield keys
        last = keys[-1]


def _short(value):
    return str(value).replace("-", "")[:8]


class PackageOperation(Operation):
    reduces_to_sql = False
    atomic = False

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if inspect.isabstract(cls) or cls.__name__.startswith("_"):
            return

        # Otherwise unapply() partially reverses the database before failing.
        implements_backwards = (
            cls.database_backwards is not PackageOperation.database_backwards
        )
        if cls.reversible and not implements_backwards:
            raise TypeError(
                f"{cls.__name__} sets reversible = True but does not implement "
                "database_backwards(). Implement it, or declare "
                "reversible = False."
            )

        if cls.scope not in ("graph", "data"):
            raise TypeError(
                f'{cls.__name__} must set scope to "graph" or "data"; it decides '
                "which migration the operation is written into."
            )
        for name in ("describe", "migration_name_fragment"):
            if getattr(cls, name, None) is getattr(PackageOperation, name, None):
                raise TypeError(f"{cls.__name__} must define {name}.")

    def deconstruct(self):
        """Emit every constructor parameter explicitly, read back from self.

        Attribute names must match __init__ parameter names: OperationWriter
        filters kwargs with get_func_args and silently drops the rest.
        """
        kwargs = {name: getattr(self, name) for name in get_func_args(self.__init__)}
        return (self.__class__.__name__, [], kwargs)

    def qs(self, model, schema_editor):
        return model.objects.using(schema_editor.connection.alias)

    def has_pending_work(self, using):
        return True


class _AlterRowOperation(PackageOperation):
    reversible = True
    scope = "graph"
    model = None
    verbose_name = None

    @property
    def state_collection(self):
        return collection_for(self.model)[0]

    @property
    def _pk(self):
        return str(self.pk)

    def __init__(self, graphid, pk, changes):
        self.graphid = graphid
        self.pk = pk
        self.changes = changes

    def _entry(self, state):
        return (
            state.graph(self.graphid).get(self.state_collection, {}).get(self._pk, {})
        )

    def _entry_for_write(self, state):
        collection = state.graph_for_write(self.graphid).setdefault(
            self.state_collection, {}
        )
        # Replace rather than mutate: the row may be shared with the cloned-from state.
        row = dict(collection.get(self._pk, {}))
        collection[self._pk] = row
        return row

    def state_forwards(self, app_label, state):
        self._entry_for_write(state).update(self.changes)

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        self.qs(self.model, schema_editor).filter(pk=self._pk).update(**self.changes)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        previous = self._entry(to_state)
        # Index rather than .get(): a KeyError beats writing NULLs.
        self.qs(self.model, schema_editor).filter(pk=self._pk).update(
            **{field: previous[field] for field in self.changes}
        )

    def describe(self):
        changed = ", ".join(sorted(self.changes))
        return f"Alter {self.verbose_name} {self._pk} ({changed})"

    @property
    def migration_name_fragment(self):
        return f"alter_{self.verbose_name}_{_short(self._pk)}"


class _RowOperation(PackageOperation):
    # A single fields dict, not **kwargs: OperationWriter drops VAR_KEYWORD args.
    scope = "graph"
    model = None
    verbose_name = None

    @property
    def state_collection(self):
        return collection_for(self.model)[0]

    @property
    def pk_field(self):
        return collection_for(self.model)[1]

    @property
    def has_graph_fk(self):
        return "graph_id" in {
            field.attname for field in self.model._meta.concrete_fields
        }

    serialization_expand_args = ["fields"]

    def __init__(self, graphid, fields):
        self.graphid = graphid
        self.fields = fields

    def _complete_fields(self):
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
                missing_required.append(name)
        if missing_required:
            raise ValueError(
                f"{type(self).__name__} is missing required field(s) "
                f"{', '.join(sorted(missing_required))} for "
                f"{self.model.__name__}. Supply them in fields."
            )
        return completed

    @property
    def _pk(self):
        return str(self.fields[self.pk_field])

    @property
    def _label(self):
        return self._pk

    @property
    def _fragment(self):
        return _short(self._pk)

    def _collection(self, state):
        return state.graph(self.graphid).get(self.state_collection, {})

    def _collection_for_write(self, state):
        return state.graph_for_write(self.graphid).setdefault(self.state_collection, {})

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

    def describe(self):
        return f"Create {self.verbose_name} {self._label} on graph {self.graphid}"

    @property
    def migration_name_fragment(self):
        return f"{self.verbose_name}_{self._fragment}"

    def state_forwards(self, app_label, state):
        self._collection_for_write(state)[self._pk] = self._complete_fields()

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        self._create_row(schema_editor)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        self._delete_row(schema_editor)


class _DeleteRowOperation(_RowOperation):
    reversible = True

    def __init__(self, graphid, pk):
        self.graphid = graphid
        self.pk = pk

    @property
    def _pk(self):
        return str(self.pk)

    def state_forwards(self, app_label, state):
        del self._collection_for_write(state)[self._pk]

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        self._delete_row(schema_editor)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        self.fields = self._collection(to_state)[self._pk]
        self._create_row(schema_editor)

    def describe(self):
        return f"Delete {self.verbose_name} {self._pk} from graph {self.graphid}"

    @property
    def migration_name_fragment(self):
        return f"delete_{self.verbose_name}_{_short(self._pk)}"
