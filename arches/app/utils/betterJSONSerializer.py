import datetime
import decimal
import types
import json
import inspect
import uuid
from io import StringIO
from itertools import chain
from django.db import models, DEFAULT_DB_ALIAS
from django.db.models import Model
from django.db.models.query import QuerySet
from django.utils.encoding import smart_unicode
from django.core.serializers.python import Serializer as PythonSerializer
from django.core.serializers.python import Deserializer as PythonDeserializer
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.contrib.gis.geos import GEOSGeometry
from django.core.files import File


class UnableToSerializeError(Exception):
    """ Error for not implemented classes """
    def __init__(self, value):
        self.value = value
        Exception.__init__(self)

    def __str__(self):
        return repr(self.value)

class UnableToSerializeMethodTypesError(Exception):
    """ Error for not implemented classes """
    def __init__(self, value):
        self.value = value
        Exception.__init__(self)

    def __str__(self):
        return repr(self.value)

class JSONSerializer(object):
    def serializeToPython(self, obj, **options):
        self.options = options.copy()

        self.stream = options.pop("stream", StringIO())
        self.selected_fields = options.pop("fields", None)
        self.use_natural_keys = options.pop("use_natural_keys", False)
        self.geom_format = options.pop("geom_format", "wkt")

        return self.handle_object(obj)

    def serialize(self, obj, **options):
        obj = self.serializeToPython(obj, **options)

        # prevent raw strings from begin re-encoded
        # this is especially important when doing bulk operations in elasticsearch
        if (isinstance(obj, basestring)):
            return obj
            
        ret = self.handle_object(obj)

        return json.dumps(ret, cls=DjangoJSONEncoder, **options.copy())


    def handle_object(self, object):
        """ Called to handle everything, looks for the correct handling """
        # print type(object)
        # print object
        # print inspect.isclass(object)
        # print inspect.ismethod(object)
        # print inspect.isfunction(object)
        # print inspect.isbuiltin(object)
        # print inspect.isroutine(object)
        # print inspect.isabstract(object)
        # print type(object) == 'staticmethod'
        if (inspect.isroutine(object) or
            inspect.isbuiltin(object) or
            inspect.isclass(object)):
            raise UnableToSerializeMethodTypesError(type(object))
        elif isinstance(object, dict):
            return self.handle_dictionary(object)
        elif (isinstance(object, list) or 
              isinstance(object, tuple)):
            return self.handle_list(object)
        elif isinstance(object, Model):
            if hasattr(object, 'serialize'):
                return self.handle_object(getattr(object, 'serialize')())
            else:
                return self.handle_model(object)
            #return PythonSerializer().serialize([object],**self.options.copy())[0]['fields']
        elif isinstance(object, QuerySet):
            #return super(JSONSerializer,self).serialize(object, **self.options.copy())[0]
            ret = []
            for item in object:
                ret.append(self.handle_object(item))
            return ret
        elif (isinstance(object, int) or
              isinstance(object, float) or 
              isinstance(object, long) or 
              isinstance(object, basestring) or 
              isinstance(object, bool) or 
              object is None):
            return object
        elif (isinstance(object, datetime.datetime) or
              isinstance(object, datetime.date) or
              isinstance(object, datetime.time) or
              isinstance(object, decimal.Decimal)):
            return DjangoJSONEncoder().default(object)
        elif isinstance(object, GEOSGeometry):
            return getattr(object, self.geom_format)
        elif isinstance(object, File):
            return object.name
        elif isinstance(object, uuid.UUID):
            return str(object)
        elif hasattr(object, '__dict__'):
            # call an objects serialize method if it exists
            if hasattr(object, 'serialize'):
                return getattr(object, 'serialize')()  
            else:
                return self.handle_dictionary(object.__dict__)
        else:
            raise UnableToSerializeError(type(object))

    def handle_dictionary(self, d):
        """Called to handle a Dictionary"""
        obj = {}
        for key, value in d.iteritems():
            try:
                #print key + ': ' + str(type(value))
                obj[str(key)] = self.handle_object(value)
            except(UnableToSerializeMethodTypesError):
                pass

        return obj


    def handle_list(self, l):
        """Called to handle a list"""
        arr = []
        for item in l:
            arr.append(self.handle_object(item))

        return arr

    # a slighty modified version of django.forms.models.model_to_dict
    def handle_model(self, instance, fields=None, exclude=None):
        """
        Returns a dict containing the data in ``instance`` suitable for passing as
        a Form's ``initial`` keyword argument.

        ``fields`` is an optional list of field names. If provided, only the named
        fields will be included in the returned dict.

        ``exclude`` is an optional list of field names. If provided, the named
        fields will be excluded from the returned dict, even if they are listed in
        the ``fields`` argument.
        """
        # avoid a circular import
        from django.db.models.fields.related import ManyToManyField, ForeignKey
        opts = instance._meta
        data = {}
        #print '='*40
        for f in chain(opts.concrete_fields, opts.virtual_fields, opts.many_to_many):
            #print f.name
            if not getattr(f, 'editable', False):
                continue
            if fields and f.name not in fields:
                continue
            if exclude and f.name in exclude:
                continue
            if isinstance(f, ForeignKey):
                # Emulate the naming convention used by django when accessing the 
                # related model's id field
                # see https://github.com/django/django/blob/master/django/db/models/fields/__init__.py
                val = getattr(instance, f.name, None)
                data[f.attname] = val.pk if val else val
            elif isinstance(f, ManyToManyField):
                # If the object doesn't have a primary key yet, just use an empty
                # list for its m2m fields. Calling f.value_from_object will raise
                # an exception.
                if instance.pk is None:
                    data[f.name] = []
                else:
                    # MultipleChoiceWidget needs a list of pks, not object instances.
                    qs = f.value_from_object(instance)
                    if qs._result_cache is not None:
                        data[f.name] = [item.pk for item in qs]
                    else:
                        data[f.name] = list(qs.values_list('pk', flat=True))
            else:
                data[f.name] = self.handle_object(f.value_from_object(instance))
        return data


class JSONDeserializer(object):
    """
    Deserialize a stream or string of JSON data.
    """
    def deserialize(self, stream_or_string, **options):
        self.options = options.copy()

        self.stream = options.pop("stream", StringIO())
        self.selected_fields = options.pop("fields", None)
        self.use_natural_keys = options.pop("use_natural_keys", False)

        if isinstance(stream_or_string, basestring):
            stream = StringIO(smart_unicode(stream_or_string))
        else:
            stream = stream_or_string

        ret = self.handle_object(json.load(stream))

        return ret


    def handle_object(self, object):
        """ Called to handle everything, looks for the correct handling """
        if isinstance(object, dict):
            if ('pk' in object and 'model' in object and 'fields' in object):
                # assume that this is a serialized django model
                return self.handle_model(object)
            else:
                return self.handle_dictionary(object)
        elif (isinstance(object, list) or 
              isinstance(object, tuple)):
            return self.handle_list(object)
        elif (isinstance(object, int) or
              isinstance(object, float) or 
              isinstance(object, long) or 
              isinstance(object, basestring) or 
              isinstance(object, bool) or 
              object is None):
            return object
        #elif isinstance(object, tuple):
        #    return tuple(self.serialize([item for item in obj]))
        elif hasattr(object, '__dict__'):
            return self.handle_dictionary(object.__dict__)
        else:
            raise UnableToSerializeError(type(object))


    def handle_dictionary(self, d):
        """Called to handle a Dictionary"""
        obj = {}
        for key, value in d.iteritems():
            obj[key] = self.handle_object(value)

        return obj


    def handle_list(self, l):
        """Called to handle a list"""
        arr = []
        for item in l:
            arr.append(self.handle_object(item))

        return arr


    def handle_model(self, m):
        """Called to handle a model"""
        a = []
        for obj in PythonDeserializer([m],**self.options.copy()):
            a.append(obj)
        return a
