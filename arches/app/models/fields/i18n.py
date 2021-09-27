import json
from django.contrib.postgres.fields import JSONField
from arches.app.models.system_settings import settings
from django.utils.translation import get_language
from django.contrib.postgres.fields.jsonb import JsonAdapter


def default_lang_node_json(value=None, lang=None):
    print('in default_lang_node_json')
    ret = {}
    ret[settings.LANGUAGE_CODE] = ""
    for lang_setting in settings.LANGUAGES:
        ret[lang_setting[0]] = ""

    if value is not None:
        available_languages = [settings.LANGUAGE_CODE] if len(settings.LANGUAGES) == 0 else [lang[0] for lang in settings.LANGUAGES]
        if lang is None:
            lang = get_language()
        if lang in available_languages:
            ret[lang] = value
        else:
            raise Exception("The language code requested is not enabled in settings.LANGUAGES or settings.LANGUAGE_CODE")

    return I18n_Field(ret)


class JSONBSet(object):
    def __init__(self, attname, value):
        print('in JSONBset init')
        self.sql = "jsonb_set(" + attname + ", %s, %s)"
        self.value = value

    def as_sql(self, compiler, connection):
        # import ipdb; ipdb.sset_trace()
        from django.db.models.sql.compiler import SQLInsertCompiler
        lang = f"{{{get_language()}}}"
        params = (lang, json.dumps(self.value))
        if isinstance(compiler, SQLInsertCompiler):
            # import ipdb; ipdb.sset_trace()
            params = [f'{{"{get_language()}": {json.dumps(self.value)}}}']
            # params = (get_language(), json.dumps(self.value))
            self.sql = "%s"
            print(self.sql % params)
            
        
        return self.sql, params


class I18n_Field(object):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        if self.value is None:
            return self.value

        try:
            ret = json.loads(self.value)
        except TypeError:
            ret = self.value

        try:
            return ret[get_language()]
        except KeyError as e:
            try:
                return ret[settings.LANGUAGE_CODE]
            except KeyError as e:
                try:
                    return list(ret.values())[0]
                except:
                    print('error')
                    return ""

    def serialize(self):
        return str(self)


class I18n_TextField(JSONField):
    def __init__(self, *args, **kwargs):
        kwargs["default"] = default_lang_node_json
        super().__init__(*args, **kwargs)
        pass

    def from_db_value(self, value, expression, connection):
        # import ipdb; ipdb.sset_trace()
        print('in from_db_value')
        if value is not None:
            return I18n_Field(value)
        return None

    # def to_python(self, value):
    #     # import ipdb; ipdb.sset_trace()
    #     print('in to_python')
    #     if isinstance(value, I18n_Field):
    #         return value
    #     if value is None:
    #         return value
    #     value = super().to_python(value)
    #     return I18n_Field(value)

    def get_prep_value(self, value):
        # import ipdb; ipdb.sset_trace()
        print(f'in get_prep_value, value={value}')
        if isinstance(value, str):
            try:
                json.loads(value)
            except:
                value = JSONBSet(self.attname, value)
        elif isinstance(value, I18n_Field):
            value = json.dumps(value.value)
        elif isinstance(value, dict):
            value = json.dumps(value)
        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        print(f'in get_db_prep_value, value={value}')
        return super().get_db_prep_value(value, connection, prepared)
