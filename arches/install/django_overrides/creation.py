import sys, os
from django.conf import settings
from django.db.backends.creation import BaseDatabaseCreation
from django.db.backends.util import truncate_name
from arches.db.install import install_db

class DatabaseCreation(BaseDatabaseCreation):
    # This dictionary maps Field objects to their associated PostgreSQL column
    # types, as strings. Column-type strings can contain format strings; they'll
    # be interpolated against the values of Field.__dict__ before being output.
    # If a column type is set to None, it won't be included in the output.
    data_types = {
        'AutoField':         'serial',
        'BinaryField':       'bytea',
        'BooleanField':      'boolean',
        'CharField':         'varchar(%(max_length)s)',
        'CommaSeparatedIntegerField': 'varchar(%(max_length)s)',
        'DateField':         'date',
        'DateTimeField':     'timestamp with time zone',
        'DecimalField':      'numeric(%(max_digits)s, %(decimal_places)s)',
        'FileField':         'varchar(%(max_length)s)',
        'FilePathField':     'varchar(%(max_length)s)',
        'FloatField':        'double precision',
        'IntegerField':      'integer',
        'BigIntegerField':   'bigint',
        'IPAddressField':    'inet',
        'GenericIPAddressField': 'inet',
        'NullBooleanField':  'boolean',
        'OneToOneField':     'integer',
        'PositiveIntegerField': 'integer CHECK ("%(column)s" >= 0)',
        'PositiveSmallIntegerField': 'smallint CHECK ("%(column)s" >= 0)',
        'SlugField':         'varchar(%(max_length)s)',
        'SmallIntegerField': 'smallint',
        'TextField':         'text',
        'TimeField':         'time',
    }

    def sql_table_creation_suffix(self):
        assert self.connection.settings_dict['TEST_COLLATION'] is None, "PostgreSQL does not support collation setting at database creation time."
        if self.connection.settings_dict['TEST_CHARSET']:
            return "WITH ENCODING '%s'" % self.connection.settings_dict['TEST_CHARSET']
        return ''

    def sql_indexes_for_field(self, model, f, style):
        output = []
        if f.db_index or f.unique:
            qn = self.connection.ops.quote_name
            db_table = model._meta.db_table
            tablespace = f.db_tablespace or model._meta.db_tablespace
            if tablespace:
                tablespace_sql = self.connection.ops.tablespace_sql(tablespace)
                if tablespace_sql:
                    tablespace_sql = ' ' + tablespace_sql
            else:
                tablespace_sql = ''

            def get_index_sql(index_name, opclass=''):
                return (style.SQL_KEYWORD('CREATE INDEX') + ' ' +
                        style.SQL_TABLE(qn(truncate_name(index_name,self.connection.ops.max_name_length()))) + ' ' +
                        style.SQL_KEYWORD('ON') + ' ' +
                        style.SQL_TABLE(qn(db_table)) + ' ' +
                        "(%s%s)" % (style.SQL_FIELD(qn(f.column)), opclass) +
                        "%s;" % tablespace_sql)

            if not f.unique:
                output = [get_index_sql('%s_%s' % (db_table, f.column))]

            # Fields with database column types of `varchar` and `text` need
            # a second index that specifies their operator class, which is
            # needed when performing correct LIKE queries outside the
            # C locale. See #12234.
            db_type = f.db_type(connection=self.connection)
            if db_type.startswith('varchar'):
                output.append(get_index_sql('%s_%s_like' % (db_table, f.column),
                                            ' varchar_pattern_ops'))
            elif db_type.startswith('text'):
                output.append(get_index_sql('%s_%s_like' % (db_table, f.column),
                                            ' text_pattern_ops'))
        return output

    def create_test_db(self, verbosity=1, autoclobber=False):
        """
        Creates a test database, prompting the user for confirmation if the
        database already exists. Returns the name of the test database created.
        """
        # Don't import django.core.management if it isn't needed.
        from django.core.management import call_command

        test_database_name = self._get_test_db_name()

        if verbosity >= 1:
            test_db_repr = ''
            if verbosity >= 2:
                test_db_repr = " ('%s')" % test_database_name
            print("Creating test database for alias '%s'%s..." % (
                self.connection.alias, test_db_repr))

        self._create_test_db(verbosity, autoclobber)

        self.connection.close()
        settings.DATABASES[self.connection.alias]["NAME"] = test_database_name
        self.connection.settings_dict["NAME"] = test_database_name

        # Report syncdb messages at one level lower than that requested.
        # This ensures we don't get flooded with messages during testing
        # (unless you really ask to be flooded)
        # call_command('syncdb',
        #     verbosity=max(verbosity - 1, 0),
        #     interactive=False,
        #     database=self.connection.alias,
        #     load_initial_data=False)

        # We need to then do a flush to ensure that any data installed by
        # custom SQL has been removed. The only test data should come from
        # test fixtures, or autogenerated from post_syncdb triggers.
        # This has the side effect of loading initial data (which was
        # intentionally skipped in the syncdb).
        # call_command('flush',
        #     verbosity=max(verbosity - 1, 0),
        #     interactive=False,
        #     database=self.connection.alias)

        from django.core.cache import get_cache
        from django.core.cache.backends.db import BaseDatabaseCache
        for cache_alias in settings.CACHES:
            cache = get_cache(cache_alias)
            if isinstance(cache, BaseDatabaseCache):
                call_command('createcachetable', cache._table,
                             database=self.connection.alias)

        # Get a cursor (even though we don't need one yet). This has
        # the side effect of initializing the test database.
        self.connection.cursor()

        return test_database_name

    def _create_test_db(self, verbosity, autoclobber):
        """
        Internal implementation - creates the test db tables.
        """
        suffix = 'test' #self.sql_table_creation_suffix()

        test_database_name = self._get_test_db_name()

        qn = self.connection.ops.quote_name

        try:

            # Create the base arches database and connect to it.
            db_settings = settings.DATABASES['default']
            db_settings['NAME'] = test_database_name
            install_path = os.path.join(settings.ROOT_DIR, 'db', 'install', 'install_db.sql')  
            db_settings['install_path'] = install_path   
            install_db.create_sqlfile(db_settings, install_path)
            
            os.system('psql -h %(HOST)s -p %(PORT)s -U %(USER)s -d postgres -c "DROP DATABASE IF EXISTS %(NAME)s;"' % db_settings)
            os.system('psql -h %(HOST)s -p %(PORT)s -U %(USER)s -d postgres -c "CREATE DATABASE %(NAME)s WITH ENCODING=\'UTF8\' OWNER=%(USER)s CONNECTION LIMIT=-1;"' % db_settings)
            
            os.system('psql -h %(HOST)s -p %(PORT)s -U %(USER)s -d %(NAME)s -f "%(install_path)s"' % db_settings)

        except Exception as e:
            sys.stderr.write(
                "Got an error creating the test database: %s\n" % e)
            if not autoclobber:
                confirm = input(
                    "Type 'yes' if you would like to try deleting the test "
                    "database '%s', or 'no' to cancel: " % test_database_name)
            if autoclobber or confirm == 'yes':
                try:
                    if verbosity >= 1:
                        print("Destroying old test database '%s'..."
                              % self.connection.alias)
                    cursor.execute(
                        "DROP DATABASE %s" % qn(test_database_name))
                    cursor.execute(
                        "CREATE DATABASE %s %s" % (qn(test_database_name),
                                                   suffix))
                except Exception as e:
                    sys.stderr.write(
                        "Got an error recreating the test database: %s\n" % e)
                    sys.exit(2)
            else:
                print("Tests cancelled.")
                sys.exit(1)

        return test_database_name

    def _destroy_test_db(self, test_database_name, verbosity):
        """
        Internal implementation - remove the test db tables.
        """

        db_settings = settings.DATABASES['default']
        db_settings['NAME'] = test_database_name
        os.system('psql -h %(HOST)s -p %(PORT)s -U %(USER)s -d postgres -c "DROP DATABASE IF EXISTS %(NAME)s;"' % db_settings)
