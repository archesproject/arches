from __future__ import unicode_literals

import keyword
import re
from optparse import make_option

from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError
from django.db import connections, DEFAULT_DB_ALIAS
from django.utils.datastructures import SortedDict


class Command(NoArgsCommand):
    help = "Introspects the database tables in the given database and outputs a Django model module."

    option_list = NoArgsCommand.option_list + (
        make_option('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a database to '
                'introspect.  Defaults to using the "default" database.'),
    )

    requires_model_validation = False

    db_module = 'django.db'

    def handle_noargs(self, **options):
        try:
            for line in self.handle_inspection(options):
                self.stdout.write("%s\n" % line)
        except NotImplementedError:
            raise CommandError("Database inspection isn't supported for the currently selected database backend.")
    
    # from https://code.djangoproject.com/ticket/1561
    def topological_sort(self, cursor, introspection_module, table_names):
        """
        Generator, Sorting the table names in a way that there are no forward references, if possible.
        Yields tuples ( table_name, forward_refs, comment_lines ) in an order that avoids forward references.
        Here, forward_refs is a set of table names that are referenced with a forward reference
        that could not be avoided since circular dependencies exist.
        comment_lines is a list of comment lines for this table (about forward references)
        """
        # tables_in is a list [ (table_name, [ referenced_table_name ] ], excluding self references
        tables_in = [(name, [val[1]
                             for val in introspection_module.get_relations(cursor, name).values()
                             if val[1] != name])
                     for name in table_names]
        # unhandled_tables contains all unhandled table_names as a set for quick lookup
        unhandled_tables = set(table_names)
        # tables_in contains all table_names that still need to be handled.
        # Initially, sort all tables by number of references and lexically
        # (to get a defined order that doesn't change from inspect to inspect)
        tables_in.sort(lambda (name1,refs1),(name2,refs2): cmp(len(refs1),len(refs2)) or cmp(name1,name2))
        # go through list until everything is handled
        while tables_in != []:
            for i, (table_name, refs) in enumerate(tables_in):
                # does it have references to unhandled tables?
                if not unhandled_tables.intersection(refs):
                    # no, take it
                    unhandled_tables.remove(table_name)
                    del tables_in[i]
                    yield (table_name, set(), [])
                    break;
            else:
                # There is no element without forward references in tables_in
                # i.e. we have circular references
                # strategy: use the table that is referenced most often
                # This will most probably break the cycle
                # with the least number of trouble makers.
                # --> First, build a cross-ref:
                #     referrers[table_name] is a set of all unhandled tables referencing table_name
                referrers = {}
                max_refcount = -1
                for table_name, refs in tables_in:
                    for ref in refs:
                        referrers.setdefault(ref,set()).add(table_name)
                # first entry in table_name getting maximal references
                for i, (table_name, refs) in enumerate(tables_in):
                    refcount = len(referrers.get(table_name,set()))
                    if refcount > max_refcount:
                        max_refcount, candidate = (refcount, i)
                # got it.
                bad_table_name, forward_references = tables_in[candidate]
                forward_references = unhandled_tables.intersection(forward_references)
                bad_referrers = list(unhandled_tables.intersection(referrers[bad_table_name]))
                bad_referrers.sort()
                comments = ["# cyclic references detected at this point",
                            "# %s contains these forward references: %s"
                                % (bad_table_name, ", ".join(forward_references)),
                            "# and is referenced by %s" % ", ".join(bad_referrers)]
                unhandled_tables.remove(bad_table_name)
                del tables_in[candidate]
                yield (bad_table_name, set(forward_references), comments)
        return

    def handle_inspection(self, options):
        connection = connections[options.get('database')]
        # 'table_name_filter' is a stealth option
        table_name_filter = options.get('table_name_filter')

        table2model = lambda table_name: table_name.title().replace('_', '').replace(' ', '').replace('-', '')
        strip_prefix = lambda s: s[1:] if s.startswith("u'") else s

        cursor = connection.cursor()
        # https://gist.github.com/1031701 
        cursor.execute("SET search_path TO " + settings.DATABASES[DEFAULT_DB_ALIAS]['SCHEMAS'])
        yield "# This is an auto-generated Django model module."
        yield "# You'll have to do the following manually to clean this up:"
        yield "#   * Rearrange models' order"
        yield "#   * Make sure each model has one field with primary_key=True"
        yield "#   * Remove `managed = False` lines for those models you wish to give write DB access"
        yield "# Feel free to rename the models, but don't rename db_table values or field names."
        yield "#"
        yield "# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'"
        yield "# into your database."
        yield "from __future__ import unicode_literals"
        yield ''
        yield 'from %s import models' % self.db_module
        yield ''
        known_models = []
        for (table_name, forward_referenced_tables, comments
            ) in (self.topological_sort(cursor, connection.introspection,
                                   connection.introspection.get_table_list(cursor))):
            for comment in comments:
                yield comment

            if table_name_filter is not None and callable(table_name_filter):
                if not table_name_filter(table_name):
                    continue
            yield 'class %s(models.Model):' % table2model(table_name)
            known_models.append(table2model(table_name))
            try:
                relations = connection.introspection.get_relations(cursor, table_name)
            except NotImplementedError:
                relations = {}
            
            relation_count = {}
            for (field_index, (field_index_other_table, other_table)) in relations.iteritems():
                relation_count[other_table] = relation_count.setdefault(other_table,0) + 1
            try:
                indexes = connection.introspection.get_indexes(cursor, table_name)
            except NotImplementedError:
                indexes = {}
            used_column_names = [] # Holds column names used in the table so far
            for i, row in enumerate(connection.introspection.get_table_description(cursor, table_name)):
                comment_notes = [] # Holds Field notes, to be displayed in a Python comment.
                extra_params = SortedDict()  # Holds Field parameters such as 'db_column'.
                column_name = row[0]
                is_relation = i in relations

                att_name, params, notes = self.normalize_col_name(
                    column_name, used_column_names, is_relation)
                extra_params.update(params)
                comment_notes.extend(notes)

                used_column_names.append(att_name)

                # Add primary_key and unique, if necessary.
                if column_name in indexes:
                    if indexes[column_name]['primary_key']:
                        extra_params['primary_key'] = True
                    elif indexes[column_name]['unique']:
                        extra_params['unique'] = True

                if is_relation and relations[i][1] not in forward_referenced_tables:
                    rel_to = "self" if relations[i][1] == table_name else table2model(relations[i][1])
                    if rel_to in known_models:
                        field_type = 'ForeignKey(%s' % rel_to
                    else:
                        field_type = "ForeignKey('%s'" % rel_to
                else:
                    if relations.has_key(i):
                        comment_notes.append('This is a forward foreign key reference to %s.' % table2model(relations[i][1]))
                    # Calling `get_field_type` to get the field type string and any
                    # additional paramters and notes.
                    field_type, field_params, field_notes = self.get_field_type(connection, table_name, row)
                    extra_params.update(field_params)
                    comment_notes.extend(field_notes)

                    field_type += '('

                # Don't output 'id = meta.AutoField(primary_key=True)', because
                # that's assumed if it doesn't exist.
                if att_name == 'id' and field_type == 'AutoField(' and extra_params == {'primary_key': True}:
                    continue

                # Add 'null' and 'blank', if the 'null_ok' flag was present in the
                # table description.
                if row[6]: # If it's NULL...
                    if field_type == 'BooleanField(':
                        field_type = 'NullBooleanField('
                    else:
                        extra_params['blank'] = True
                        if not field_type in ('TextField(', 'CharField('):
                            extra_params['null'] = True

                field_desc = '%s = models.%s' % (att_name, field_type)
                if extra_params:
                    if not field_desc.endswith('('):
                        field_desc += ', '
                    field_desc += ', '.join([
                        '%s=%s' % (k, strip_prefix(repr(v)))
                        for k, v in extra_params.items()])
                field_desc += ')'
                if comment_notes:
                    field_desc += ' # ' + ' '.join(comment_notes)
                yield '    %s' % field_desc
            for meta_line in self.get_meta(table_name):
                yield meta_line

    def normalize_col_name(self, col_name, used_column_names, is_relation):
        """
        Modify the column name to make it Python-compatible as a field name
        """
        field_params = {}
        field_notes = []

        new_name = col_name.lower()
        if new_name != col_name:
            field_notes.append('Field name made lowercase.')

        if is_relation:
            if new_name.endswith('_id'):
                new_name = new_name[:-3]
            else:
                field_params['db_column'] = col_name

        new_name, num_repl = re.subn(r'\W', '_', new_name)
        if num_repl > 0:
            field_notes.append('Field renamed to remove unsuitable characters.')

        if new_name.find('__') >= 0:
            while new_name.find('__') >= 0:
                new_name = new_name.replace('__', '_')
            if col_name.lower().find('__') >= 0:
                # Only add the comment if the double underscore was in the original name
                field_notes.append("Field renamed because it contained more than one '_' in a row.")

        if new_name.startswith('_'):
            new_name = 'field%s' % new_name
            field_notes.append("Field renamed because it started with '_'.")

        if new_name.endswith('_'):
            new_name = '%sfield' % new_name
            field_notes.append("Field renamed because it ended with '_'.")

        if keyword.iskeyword(new_name):
            new_name += '_field'
            field_notes.append('Field renamed because it was a Python reserved word.')

        if new_name[0].isdigit():
            new_name = 'number_%s' % new_name
            field_notes.append("Field renamed because it wasn't a valid Python identifier.")

        if new_name in used_column_names:
            num = 0
            while '%s_%d' % (new_name, num) in used_column_names:
                num += 1
            new_name = '%s_%d' % (new_name, num)
            field_notes.append('Field renamed because of name conflict.')

        if col_name != new_name and field_notes:
            field_params['db_column'] = col_name

        return new_name, field_params, field_notes

    def get_field_type(self, connection, table_name, row):
        """
        Given the database connection, the table name, and the cursor row
        description, this routine will return the given field type name, as
        well as any additional keyword parameters and notes for the field.
        """
        field_params = SortedDict()
        field_notes = []

        try:
            field_type = connection.introspection.get_field_type(row[1], row)
        except KeyError:
            field_type = 'TextField'
            field_notes.append('This field type is a guess.')

        # This is a hook for DATA_TYPES_REVERSE to return a tuple of
        # (field_type, field_params_dict).
        if type(field_type) is tuple:
            field_type, new_params = field_type
            field_params.update(new_params)

        # Add max_length for all CharFields.
        if field_type == 'CharField' and row[3]:
            field_params['max_length'] = int(row[3])

        if field_type == 'DecimalField':
            if row[4] is None or row[5] is None:
                field_notes.append(
                    'max_digits and decimal_places have been guessed, as this '
                    'database handles decimal fields as float')
                field_params['max_digits'] = row[4] if row[4] is not None else 10
                field_params['decimal_places'] = row[5] if row[5] is not None else 5
            else:
                field_params['max_digits'] = row[4]
                field_params['decimal_places'] = row[5]

        return field_type, field_params, field_notes

    def get_meta(self, table_name):
        """
        Return a sequence comprising the lines of code necessary
        to construct the inner Meta class for the model corresponding
        to the given database table name.
        """
        return ["    class Meta:",
                "        managed = False",
                "        db_table = '%s'" % table_name,
                ""]
