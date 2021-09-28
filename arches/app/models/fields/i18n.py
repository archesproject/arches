import json
from django.utils.translation import gettext_lazy as _
# from json.decoder import JSONDecodeError
from arches.app.models.system_settings import settings
from django.contrib.postgres.fields import JSONField
from django.db.models.sql.compiler import SQLInsertCompiler
from django.utils.translation import get_language


class JSONBSet(object):
    """
    The "as_sql" method of this class is called by Django when the sql statement 
    for each field in a model instance is being generated.  
    If we're inserting a new value then we can just set the localzed column to the json object.
    If we're updating a value for a specific language, then use the postgres "jsonb_set" command to do that
    https://www.postgresql.org/docs/9.5/functions-json.html
    """
    def __init__(self, column_name, value):
        self.column_name = column_name
        self.value = value

    def as_sql(self, compiler, connection):
        if isinstance(compiler, SQLInsertCompiler):
            params = [f'{{"{get_language()}": {json.dumps(self.value)}}}']
            self.sql = "%s"
        else: # SQLUpdateCompiler
            lang = f"{{{get_language()}}}"
            self.sql = "jsonb_set(" + self.column_name + ", %s, %s)"
            params = (lang, json.dumps(self.value))

        # print(self.sql % params)
        return self.sql, params


class I18n_String(object):
    def __init__(self, value=None, lang=None, use_nulls=False):
        ret = {}
        if lang is None:
            lang = get_language()

        if isinstance(value, str):
            try:
                ret = json.loads(value)
            except:
                ret[lang] = value
        elif value is None:
            ret[lang] = None if use_nulls else ""
        elif isinstance(value, I18n_String):
            ret = value.raw_value
        elif isinstance(value, dict):
            ret = value
        self.raw_value = ret

    def __str__(self):
        ret = None
        try:
            ret = self.raw_value[get_language()]
        except KeyError as e:
            try:
                # if you can't return the requested language because the value doesn't exist then 
                # return the default language.
                # the reasoning is that for display in the UI, we want to show what the user initially entered
                ret = self.raw_value[settings.LANGUAGE_CODE]
            except KeyError as e:
                try:
                    # if the default language doesn't exist then return the first language available
                    ret = list(self.raw_value.values())[0]
                except:
                    # if there are no languages available return an empty string
                    ret = ""
        return json.dumps(ret) if ret is None else ret

    def serialize(self):
        return str(self)


class I18n_TextField(JSONField):
    description = _('A I18n_TextField object') 

    def __init__(self, *args, **kwargs):
        use_nulls = kwargs.get("null", False)
        kwargs["default"] = I18n_String(use_nulls=use_nulls)
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        print('in from_db_value')
        if value is not None:
            return I18n_String(value)
        return None

    def to_python(self, value):
        print('in to_python')
        if isinstance(value, I18n_String):
            return value
        if value is None:
            return value
        value = super().to_python(value)
        return I18n_String(value)

    def get_prep_value(self, value):
        print(type(value))
        print(f'in get_prep_value, value={value}')
        """
        If the value was set to a string rather then using I18n_String, then check to see if it's 
        a json object like {"en": "boat", "es": "barco"}, or just a simple string like "boat".
        If it's a json object then save it directly to the database.
        If it's just a simple string then return a JSONBset object that can just update one language value
        out of potentially several previously stored languages using the currently set language.
        See JSONBSet to see how this magic happens.  :)
        """
        if isinstance(value, str):
            try:
                json.loads(value)
            except:
                value = JSONBSet(self.attname, value)
        elif isinstance(value, I18n_String):
            value = json.dumps(value.raw_value)
        elif isinstance(value, dict):
            value = json.dumps(value)
        return value

    # def get_db_prep_value(self, value, connection, prepared=False):
    #     print(f'in get_db_prep_value, value={value}')
    #     return super().get_db_prep_value(value, connection, prepared)
