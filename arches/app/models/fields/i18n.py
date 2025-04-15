import json
import copy
from arches.app.models.system_settings import settings
from arches.app.utils import import_class_from_string
from django.utils.translation import gettext_lazy as _
from django.db.migrations.serializer import BaseSerializer, Serializer
from django.db.models import JSONField
from django.db.models.sql import Query
from django.db.models.sql.compiler import SQLInsertCompiler
from django.db.models.sql.where import NothingNode
from django.utils.translation import get_language


class I18n_String(NothingNode):
    """Subclassing NothingNode works around https://code.djangoproject.com/ticket/34745."""

    def __init__(self, value=None, lang=None, use_nulls=False, attname=None):
        self.attname = attname
        self.value = value
        self.use_nulls = use_nulls
        self.raw_value = {}
        self.value_is_primitive = False
        self.lang = get_language() if lang is None else lang

        self._parse(self.value, self.lang, self.use_nulls)

    def _parse(self, value, lang, use_nulls):
        ret = {}

        if isinstance(value, str) and value != "null":
            try:
                ret = json.loads(value)

                # the following is a fix for issue #9623 - using double quotation marks in i18n input
                # re https://github.com/archesproject/arches/issues/9623
                # the reason we have to do this next check is that we assumed that if the
                # json.loads method doesn't fail we have a python dict.  That's usually
                # true unless you have a simple string wrapped in quotes
                # eg: '"hello world"' rather than simply 'hello world'
                # the quoted string loads without error but is not a dict
                # hence the need for this check
                if not isinstance(ret, dict):
                    ret = {}
                    raise Exception("value is not a json object")
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
        If we're inserting a new value then we can just set the localized column to the json object.
        If we're updating a value for a specific language, then use the postgres "jsonb_set" command to do that
        https://www.postgresql.org/docs/9.5/functions-json.html
        """

        if (self.value_is_primitive or self.value is None) and not isinstance(
            compiler, SQLInsertCompiler
        ):
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

    # adding this so that we can treat it like a dict object
    def __getitem__(self, *args):
        return self.raw_value.__getitem__(*args)

    def __contains__(self, *args):
        return self.raw_value.__contains__(*args)

    # adding this so that we can update it like a dict object
    def __setitem__(self, key, item):
        self.raw_value[key] = item

    # added to remove items like a dict with del keyword
    def __delitem__(self, key):
        del self.raw_value[key]

    # added to pop items like a dict
    def pop(self, *args):
        return self.raw_value.pop(*args)

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
        return "" if ret is None else ret

    def __eq__(self, other):
        # this is here so you can compare a string against an instance of this class
        # eg I18n_String("toast") == "toast" would return True
        return str(self) == str(other)

    def serialize(self, use_raw_i18n_json=False, **kwargs):
        if use_raw_i18n_json:
            return self.raw_value
        else:
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
        from arches.app.utils.betterJSONSerializer import JSONSerializer

        self.use_nulls = kwargs.get("null", False)
        kwargs["encoder"] = JSONSerializer
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

    def get_db_prep_save(self, value, connection):
        if isinstance(value, (str, I18n_String)) or value is None:
            return self.get_prep_value(value)
        # ORM expressions should go through super().get_db_prep_save().
        # Plain dicts don't need transforming either.
        return super().get_db_prep_save(value, connection)


class I18n_JSON(NothingNode):
    def __init__(self, value=None, lang=None, use_nulls=False, attname=None):
        self.attname = attname
        self.value = value
        self.raw_value = {}
        self.i18n_properties = []
        self.function = None
        self.lang = get_language() if lang is None else lang

        self._parse(self.value, self.lang, use_nulls)

    def _parse(self, value, lang, use_nulls):
        ret = {}

        if isinstance(value, str):
            try:
                ret = json.loads(value)
            except:
                ret = json.loads(json.dumps(value))
        elif value is None:
            ret[lang] = None if use_nulls else ""
        elif isinstance(value, I18n_JSON):
            ret = value.raw_value
        elif isinstance(value, dict):
            ret = value
        else:
            raise TypeError(value)
        self.raw_value = ret

        if "i18n_properties" in self.raw_value:
            self.i18n_properties = self.raw_value["i18n_properties"]
        try:
            self.function = self.raw_value["i18n_config"]["fn"]
        except:
            pass

    def as_sql(self, compiler, connection):
        """
        The "as_sql" method of this class is called by Django when the sql statement
        for each field in a model instance is being generated.
        If we're inserting a new value then we can just set the localzed column to the json object.
        If we're updating a value for a specific language, then use the postgres "jsonb_set" command to do that
        https://www.postgresql.org/docs/9.5/functions-json.html

        Dangerous keys raise ValueError (with a descriptive message from Django).
        """

        if (len(self.i18n_properties) == 0 and self.function is None) or isinstance(
            compiler, SQLInsertCompiler
        ):
            params = [json.dumps(self.to_localized_object())]
            sql = "%s"
        else:
            # Forbid dangerous values.
            sanitizer = Query(model=None)
            for prop in (self.attname, *self.raw_value):
                if prop is None:
                    continue
                if "%" in prop:
                    raise ValueError
                sanitizer.check_alias(prop)

            params = []
            sql = "'{}'::jsonb"
            if self.function is not None:
                clss = import_class_from_string(self.function)()
                sql = clss.i18n_as_sql(self, compiler, connection)
            elif self.attname:
                sql = self.attname
                for prop, value in self.raw_value.items():
                    escaped_value = (
                        json.dumps(value).replace("%", "%%").replace("'", "''")
                    )
                    if prop in self.i18n_properties and isinstance(value, str):
                        sql = f"""CASE WHEN jsonb_typeof({self.attname}->'{prop}') = 'object'
                        THEN jsonb_set({sql}, array['{prop}','{self.lang}'], '{escaped_value}')
                        ELSE jsonb_set({sql}, array['{prop}'], jsonb_build_object('{self.lang}', '{escaped_value}'))
                        END"""
                    else:
                        sql = f"jsonb_set({sql}, array['{prop}'], '{escaped_value}')"

            # If all of root keys of the json object we're saving are the same as what is
            # currently in that json value stored in the db then all we do is update those
            # specific values using the jsonb_set method from above
            # If on the other hand the root keys are different, then we assume that we can
            # just completely overwrite the saved object with our new json object
            sql = f"""
                CASE WHEN {self.attname or "'{}'::jsonb"} ?& ARRAY{list(self.raw_value.keys())}
                THEN {sql}
                ELSE %s
                END
            """
            params.append(json.dumps(self.to_localized_object()).replace("%", "%%"))

        return sql, tuple(params)

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
            "update",
        ]
        if name in mapping_methods:
            return getattr(self.raw_value, name)
        raise AttributeError

    def serialize(self, use_raw_i18n_json=False, **kwargs):
        """
        Takes a localized object
        eg: {"Color": {"en": "blue", "es": "azul"}}
        and returns the value as a string based on the active language
        eg: if the active language is Spanish then the above returned
        object would be {"Color": "asul"}

        Keyword Arguments:
        use_raw_i18n_json -- defaults to False, set to True to return the raw object saved in the db
        """

        if use_raw_i18n_json or (
            "i18n_properties" not in self.raw_value
            and "i18n_config" not in self.raw_value
        ):
            return self.raw_value
        else:
            if self.function is not None:
                clss = import_class_from_string(self.function)()
                ret = clss.i18n_serialize(self)
            else:
                ret = copy.deepcopy(self.raw_value)
                if not use_raw_i18n_json and "i18n_properties" in ret:
                    for prop in ret["i18n_properties"]:
                        try:
                            ret[prop] = str(I18n_String(ret[prop]))
                        except:
                            pass
            return ret

    def to_localized_object(self):
        """
        Takes an object that is assumed to hold a localized value
        eg: {"Color": "azul"}
        and returns the value as an object keyed to the active language
        Eg: if the active language is Spanish then the above returned
        object would be {"Color": {"es": "asul"}}
        """

        if self.function is not None:
            clss = import_class_from_string(self.function)()
            ret = clss.i18n_to_localized_object(self)
        else:
            ret = copy.deepcopy(self.raw_value)
            if "i18n_properties" in ret:
                for prop in ret["i18n_properties"]:
                    if not isinstance(ret[prop], dict):
                        ret[prop] = {self.lang: ret[prop]}
        return ret


class I18n_JSONField(JSONField):
    description = _("A I18n_JSONField object")

    def __init__(self, *args, **kwargs):
        from arches.app.utils.betterJSONSerializer import JSONSerializer

        kwargs["encoder"] = JSONSerializer
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
        Prepares the value for insertion into the database
        """

        return I18n_JSON(value, attname=self.attname)

    def get_db_prep_save(self, value, connection):
        if isinstance(value, (str, dict)):
            return self.get_prep_value(value)
        # ORM expressions should go through super().get_db_prep_save().
        return super().get_db_prep_save(value, connection)


# Register a lighter-weight serializer sufficient for generating migrations.
class I18NFieldMigrationSerializer(BaseSerializer):
    def serialize(self):
        if isinstance(self.value, (I18n_String, I18n_JSONField)):
            return f'"{self.value.serialize()}"', set()
        return super().serialize()


Serializer.register(I18n_String, I18NFieldMigrationSerializer)
Serializer.register(I18n_JSONField, I18NFieldMigrationSerializer)
