import datetime
import decimal
import types
import json
import inspect
from io import StringIO
from django.db import models, DEFAULT_DB_ALIAS
from django.db.models import Model
from django.db.models.query import QuerySet
from django.utils.encoding import smart_unicode
from django.core.serializers.python import Serializer as PythonSerializer
from django.core.serializers.python import Deserializer as PythonDeserializer
from django.core.serializers.json import DjangoJSONEncoder
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
        self.options = options.copy()

        self.stream = options.pop("stream", StringIO())
        self.selected_fields = options.pop("fields", None)
        self.use_natural_keys = options.pop("use_natural_keys", False)
        self.geom_format = options.pop("geom_format", "wkt")

        ret = self.handle_object(obj)

        return json.dumps(ret, cls=DjangoJSONEncoder, **options.copy())


    def handle_object(self, object):
        """ Called to handle everything, looks for the correct handling """
        # print type(object)
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
            #return super(JSONSerializer,self).serialize([object], **self.options.copy())[0]
            return PythonSerializer().serialize([object],**self.options.copy())
        elif isinstance(object, QuerySet):
            #return super(JSONSerializer,self).serialize(object, **self.options.copy())[0]
            return PythonSerializer().serialize(object,**self.options.copy())
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
        elif hasattr(object, '__dict__'):
            return self.handle_dictionary(object.__dict__)
        else:
            raise UnableToSerializeError(type(object))

    def handle_dictionary(self, d):
        """Called to handle a Dictionary"""
        obj = {}
        for key, value in d.iteritems():
            try:
                #print key + ': ' + str(type(value))
                obj[key] = self.handle_object(value)
            except(UnableToSerializeMethodTypesError):
                pass

        return obj


    def handle_list(self, l):
        """Called to handle a list"""
        arr = []
        for item in l:
            arr.append(self.handle_object(item))

        return arr


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
