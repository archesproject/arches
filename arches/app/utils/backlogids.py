import datetime
import re
from django.conf import settings
import uuid
import types
import copy
import arches.app.models.models as archesmodels
from arches.app.models.resource import Resource
from arches.app.models.entity import Entity
from arches.app.search.search_engine_factory import SearchEngineFactory
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import fromstr
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.core.exceptions import ObjectDoesNotExist

def createBacklogIds():
    entitytype = archesmodels.EntityTypes.objects.get(pk = "ACTOR.E39")
    type = 'ACTOR'
    all_entities = archesmodels.Entities.objects.filter(entitytypeid__exact = entitytype)
    entities =[]
    errors = []
    for count, entity in enumerate(all_entities, 1):
        if count % 5000 == 0:
            print "%s resources inspected" % count
        try:
            relation = archesmodels.Relations.objects.get(ruleid=archesmodels.Rules.objects.get(entitytypedomain=entitytype, entitytyperange="EAMENA_ID.E42").ruleid, entityiddomain =entity.entityid)
        except  ObjectDoesNotExist:
            entities.append(entity)
            
    print "There are %s resources and %s which do not have a EAMENA_ID.E42" % (all_entities.count(), len(entities))

    for count, entity in enumerate(entities, 1):
        if count % 1000 == 0:
            print "%s UniqueIds created" % count
        entity2 = archesmodels.Entities()
        entity2.entitytypeid = archesmodels.EntityTypes.objects.get(pk = "EAMENA_ID.E42")
        entity2.entityid = str(uuid.uuid4())
        entity2.save()
        rule = archesmodels.Rules.objects.get(entitytypedomain = entity.entitytypeid, entitytyperange = entity2.entitytypeid, propertyid = 'P1')
        archesmodels.Relations.objects.get_or_create(entityiddomain = entity, entityidrange = entity2, ruleid = rule)
        uniqueidmodel = Entity._get_model('uniqueids')
        uniqueidmodelinstance = uniqueidmodel()
        uniqueidmodelinstance.entityid = entity2
        uniqueidmodelinstance.id_type = type
        try:
            lastID = uniqueidmodel.objects.filter(id_type__exact=type).latest()
            IdInt = int(lastID.val) + 1
            uniqueidmodelinstance.val = str(IdInt)
        except ObjectDoesNotExist:
            print "The resource %s has been assigned the first ID with entityid %s" % (entity.entityid,entity2.entityid)
            uniqueidmodelinstance.val = str(1)
            
        uniqueidmodelinstance.order_date = datetime.datetime.now()
        uniqueidmodelinstance.save()
            
            
    
        zerosLength = settings.ID_LENGTH if  settings.ID_LENGTH > len(uniqueidmodelinstance.val) else len(uniqueidmodelinstance.val)
        value = type +"-"+uniqueidmodelinstance.val.zfill(zerosLength)
        
#         ReindexResource(entity.entityid, entity2.entityid, value)
        try:
            resource = Resource().get(entity.entityid)
            resource.index()
        except Exception as e:
            if e not in errors:
                errors.append(e)
                
        if len(errors) > 0:
            print errors[0], ':', len(errors)
