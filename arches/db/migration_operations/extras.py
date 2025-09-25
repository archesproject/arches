from django.db.migrations.operations.base import Operation
from django.db import Error
import logging


class CreateExtension(Operation):
    """
    Creates a database extension in postgres

    """

    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(__name__)

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        try:
            schema_editor.execute('CREATE EXTENSION IF NOT EXISTS "%s"' % self.name)
        except Error as e:
            self.logger.warning(
                'Operation to create extension "%s" failed. Must be executed by Postgres superuser \
account before running Arches.'
                % self.name
            )

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        try:
            schema_editor.execute('DROP EXTENSION IF EXISTS "%s"' % self.name)
        except Error as e:
            self.logger.warning(
                'Operation to drop extension "%s" failed. Must be executed by Postgres superuser \
account.'
                % self.name
            )

    def describe(self):
        return "Creates extension %s" % self.name


class CreateFunction(Operation):
    """
    Creates a database function

    """

    def __init__(
        self, name, body, returntype, arguments=[], declarations=[], language="plpgsql"
    ):
        """
        Keyword arguments:
        name -- name of the function
        body -- the body of the function within the BEGIN ... END block not including the BEGIN ... END phrases
        returntype -- return type of the function
        arguments -- list of argument name and types passes into the function (eg: "p_label text")
        declarations -- list of variables and their initializers (eg: "v_new_id = 2;")
        language -- the language of the sql statement (eg: sql, plpgsql, etc...)

        """

        self.name = name
        self.arguments = arguments
        self.declarations = declarations
        self.language = language
        self.body = body
        self.returntype = returntype

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        sql = """
        CREATE OR REPLACE FUNCTION %(name)s(%(arguments)s)
            RETURNS %(returntype)s
            LANGUAGE %(language)s
            AS $$
            DECLARE
                %(declarations)s
            BEGIN
                %(body)s
            END;
            $$;
        """
        sql = sql % {
            "name": self.name,
            "arguments": ", ".join(self.arguments),
            "declarations": ";\n\t\t".join(self.declarations) + ";",
            "language": self.language,
            "body": self.body,
            "returntype": self.returntype,
        }
        sql = sql.replace(";;", ";")

        schema_editor.execute(sql)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        sql = """
        DROP FUNCTION IF EXISTS %(name)s(%(arguments)s)
        """
        sql = sql % {"name": self.name, "arguments": ", ".join(self.arguments)}

        schema_editor.execute(sql)

    def describe(self):
        return "Creates a function named %s" % self.name
        return "Creates extension %s" % self.name
