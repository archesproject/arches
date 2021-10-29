import json
import copy
from django.utils.translation import gettext_lazy as _
from arches.app.models.system_settings import settings
from django.contrib.postgres.fields import JSONField
from django.db.models.sql.compiler import SQLInsertCompiler
from django.utils.translation import get_language


class I18n_String(object):
    def __init__(self, value=None, lang=None, use_nulls=False, attname=None):
        self.attname = attname
        self.value = value
        self.raw_value = {}
        self.value_is_primitive = False
        self.lang = get_language() if lang is None else lang

        self._parse(self.value, self.lang, use_nulls)

    def _parse(self, value, lang, use_nulls):
        ret = {}

        if isinstance(value, str) and value != "null":
            try:
                ret = json.loads(value)
            except:
                ret[lang] = value
                self.value_is_primitive = True
        elif value is None or value == "null":
            ret[lang] = None if use_nulls else ""
        elif isinstance(value, I18n_String):
            ret = value.raw_value
        elif isinstance(value, dict):
            ret = value
        self.raw_value = ret

    def as_sql(self, compiler, connection):
        """
        The "as_sql" method of this class is called by Django when the sql statement
        for each field in a model instance is being generated.
        If we're inserting a new value then we can just set the localzed column to the json object.
        If we're updating a value for a specific language, then use the postgres "jsonb_set" command to do that
        https://www.postgresql.org/docs/9.5/functions-json.html
        """

        if (self.value_is_primitive or self.value is None) and not isinstance(compiler, SQLInsertCompiler):
            self.sql = "jsonb_set(" + self.attname + ", %s, %s)"
            params = (f"{{{self.lang}}}", json.dumps(self.value))
        else:
            params = [json.dumps(self.raw_value)]
            self.sql = "%s"

        return self.sql, params

    # need this to avoid a Django error when setting
    # the default value on the i18n_TextField
    def __call__(self):
        return self

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

    def __eq__(self, other):
        # this is here so you can compare a string against an instance of this class
        # eg I18n_String("toast") == "toast" would return True
        return str(self) == str(other)

    def serialize(self):
        return str(self)

    # Use this to call all the sting methods on our class so
    # this class can emulate the "string" type
    def __getattr__(self, name):
        string_methods = [
            "capitalize",
            "casefold",
            "center",
            "count",
            "encode",
            "endswith",
            "expandtabs",
            "find",
            "format",
            "format_map",
            "index",
            "isalnum",
            "isalpha",
            "isascii",
            "isdecimal",
            "isdigit",
            "isidentifier",
            "islower",
            "isnumeric",
            "isprintable",
            "isspace",
            "istitle",
            "isupper",
            "join",
            "ljust",
            "lower",
            "lstrip",
            "maketrans",
            "partition",
            "replace",
            "rfind",
            "rindex",
            "rjust",
            "rpartition",
            "rsplit",
            "rstrip",
            "split",
            "splitlines",
            "startswith",
            "strip",
            "swapcase",
            "title",
            "translate",
            "upper",
            "zfill",
        ]
        if name in string_methods:
            return getattr(str(self), name)
        raise AttributeError


class I18n_TextField(JSONField):
    description = _("A I18n_TextField object")

    def __init__(self, *args, **kwargs):
        self.use_nulls = kwargs.get("null", False)
        kwargs["default"] = I18n_String(use_nulls=self.use_nulls)
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is not None:
            return I18n_String(value, use_nulls=self.use_nulls)
        return None

    def to_python(self, value):
        if isinstance(value, I18n_String):
            return value
        if value is None:
            return value
        return I18n_String(value, use_nulls=self.use_nulls)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return str(value)

    def get_prep_value(self, value):
        """
        If the value was set to a string, then check to see if it's
        a json object like {"en": "boat", "es": "barco"}, or just a simple string like "boat".
        If it's a json object then use the I18n_String.as_sql method to insert it directly to the database.
        If it's just a simple string then use the I18n_String.as_sql method is used to update one language value
        out of potentially several previously stored languages using the currently active language.
        See I18n_String.as_sql to see how this magic happens.  :)
        """

        return I18n_String(value, attname=self.attname, use_nulls=self.use_nulls)


class I18n_JSON(object):
    def __init__(self, value=None, lang=None, use_nulls=False, attname=None):
        self.attname = attname
        self.value = value
        self.raw_value = {}
        self.i18n_properties = []
        self.lang = get_language() if lang is None else lang

        self._parse(self.value, self.lang, use_nulls)

    def _parse(self, value, lang, use_nulls):
        ret = {}

        if isinstance(value, str):
            ret = json.loads(value)
        elif value is None:
            ret[lang] = None if use_nulls else ""
        elif isinstance(value, I18n_JSON):
            ret = value.raw_value
        elif isinstance(value, dict):
            ret = value
        self.raw_value = ret

        if "i18n_properties" in self.raw_value:
            self.i18n_properties = self.raw_value["i18n_properties"]

    def as_sql(self, compiler, connection):
        """
        The "as_sql" method of this class is called by Django when the sql statement
        for each field in a model instance is being generated.
        If we're inserting a new value then we can just set the localzed column to the json object.
        If we're updating a value for a specific language, then use the postgres "jsonb_set" command to do that
        https://www.postgresql.org/docs/9.5/functions-json.html
        """

        if len(self.i18n_properties) == 0 or isinstance(compiler, SQLInsertCompiler):
            params = [json.dumps(self.raw_value)]
            self.sql = "%s"
        else:
            self.sql = self.attname
            params = []
            for prop in self.raw_value["i18n_properties"]:
                self.sql = f"jsonb_set({self.sql}, '{{{prop},{self.lang}}}', %s)"
                params.append(json.dumps(self.raw_value[prop]))
        return self.sql, params

    # need this to avoid a Django error when setting
    # the default value on the I18n_JSONField
    def __call__(self):
        return self

    def __str__(self):
        return json.dumps(self.serialize())

    # adding this so that we can treat it like a dict object
    def __getitem__(self, item):
        return self.raw_value[item]

    def __setitem__(self, item, value):
        self.raw_value[item] = value

    def __iter__(self):
        return self.raw_value.__iter__()

    # Use this to call all the sting methods on our class so
    # this class can emulate the "string" type
    # see https://docs.python.org/3/reference/datamodel.html?emulating-container-types#emulating-container-types
    def __getattr__(self, name):
        mapping_methods = [
            "keys", 
            "values", 
            "items", 
            "get", 
            "clear", 
            "setdefault", 
            "pop", 
            "popitem", 
            "copy", 
            "update"
        ]
        if name in mapping_methods:
            return getattr(self.raw_value, name)
        raise AttributeError

    def serialize(self):
        ret = copy.deepcopy(self.raw_value)
        if "i18n_properties" in ret:
            for prop in ret["i18n_properties"]:
                ret[prop] = str(I18n_String(ret[prop]))
        return ret


class I18n_JSONField(JSONField):
    description = _("A I18n_JSONField object")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is not None:
            return I18n_JSON(value)
        return I18n_JSON("{}")

    def to_python(self, value):
        if isinstance(value, I18n_JSON):
            return value
        if value is None:
            return value
        return I18n_JSON(value)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return str(value)

    def get_prep_value(self, value):
        """
        Perpares the value for insertion into the database
        """

        return I18n_JSON(value, attname=self.attname)
