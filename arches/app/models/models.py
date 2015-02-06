'''
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from operator import methodcaller
from django.dispatch import receiver
from django.conf import settings
from django.contrib.gis.db import models
import uuid
import types
import os
import json
from arches.app.utils.betterJSONSerializer import JSONSerializer
from django.contrib.auth.models import User
from django.db.models import Q

# from django.contrib.auth.models import User

# def _func(self):
#     return 'you did it'


# User.get_mapping = types.MethodType(_func, None, User)

class AuthGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=80)
    class Meta:
        db_table = u'auth_group'

class AuthUser(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=75)
    password = models.CharField(max_length=128)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    is_superuser = models.BooleanField()
    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()
    class Meta:
        db_table = u'auth_user'

class Classes(models.Model):
    classid = models.TextField(primary_key=True)
    classname = models.TextField()
    isactive = models.BooleanField()
    defaultbusinesstable = models.TextField()
    class Meta:
        db_table = u'classes'

    def __unicode__(self):
        return self.classname

class DNodetypes(models.Model):
    nodetype = models.TextField(primary_key=True)
    namespace = models.TextField()
    class Meta:
        db_table = u'd_nodetypes'

class DLanguages(models.Model):
    languageid = models.TextField(primary_key=True)
    languagename = models.TextField()
    isdefault = models.BooleanField()
    class Meta:
        db_table = u'd_languages'

class DRelationtypes(models.Model):
    relationtype = models.TextField(primary_key=True)
    category = models.TextField()
    namespace = models.TextField()
    class Meta:
        db_table = u'd_relationtypes'

class DjangoAdminLog(models.Model):
    id = models.IntegerField(primary_key=True)
    action_time = models.DateTimeField()
    user_id = models.IntegerField()
    content_type_id = models.IntegerField()
    object_id = models.TextField()
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    class Meta:
        db_table = u'django_admin_log'

class DjangoContentType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    class Meta:
        db_table = u'django_content_type'

class DjangoSession(models.Model):
    session_key = models.CharField(max_length=40, primary_key=True)
    session_data = models.TextField()
    expire_date = models.DateTimeField()
    class Meta:
        db_table = u'django_session'

class DjangoSite(models.Model):
    id = models.IntegerField(primary_key=True)
    domain = models.CharField(max_length=100)
    name = models.CharField(max_length=50)
    class Meta:
        db_table = u'django_site'

class GeographyColumns(models.Model):
    f_table_catalog = models.TextField() # This field type is a guess.
    f_table_schema = models.TextField() # This field type is a guess.
    f_table_name = models.TextField() # This field type is a guess.
    f_geography_column = models.TextField() # This field type is a guess.
    coord_dimension = models.IntegerField()
    srid = models.IntegerField()
    type = models.TextField()
    class Meta:
        db_table = u'geography_columns'

class GeometryColumns(models.Model):
    f_table_catalog = models.CharField(max_length=256)
    f_table_schema = models.CharField(max_length=256)
    f_table_name = models.CharField(max_length=256)
    f_geometry_column = models.CharField(max_length=256)
    coord_dimension = models.IntegerField()
    srid = models.IntegerField()
    type = models.CharField(max_length=30)
    class Meta:
        db_table = u'geometry_columns'

class RasterColumns(models.Model):
    r_table_catalog = models.TextField() # This field type is a guess.
    r_table_schema = models.TextField() # This field type is a guess.
    r_table_name = models.TextField() # This field type is a guess.
    r_raster_column = models.TextField() # This field type is a guess.
    srid = models.IntegerField()
    scale_x = models.FloatField()
    scale_y = models.FloatField()
    blocksize_x = models.IntegerField()
    blocksize_y = models.IntegerField()
    same_alignment = models.BooleanField()
    regular_blocking = models.BooleanField()
    num_bands = models.IntegerField()
    pixel_types = models.TextField() # This field type is a guess.
    nodata_values = models.TextField() # This field type is a guess.
    out_db = models.TextField() # This field type is a guess.
    extent = models.GeometryField(srid=0)
    objects = models.GeoManager()
    class Meta:
        db_table = u'raster_columns'

class RasterOverviews(models.Model):
    o_table_catalog = models.TextField() # This field type is a guess.
    o_table_schema = models.TextField() # This field type is a guess.
    o_table_name = models.TextField() # This field type is a guess.
    o_raster_column = models.TextField() # This field type is a guess.
    r_table_catalog = models.TextField() # This field type is a guess.
    r_table_schema = models.TextField() # This field type is a guess.
    r_table_name = models.TextField() # This field type is a guess.
    r_raster_column = models.TextField() # This field type is a guess.
    overview_factor = models.IntegerField()
    class Meta:
        db_table = u'raster_overviews'

class SpatialRefSys(models.Model):
    srid = models.IntegerField(primary_key=True)
    auth_name = models.CharField(max_length=256)
    auth_srid = models.IntegerField()
    srtext = models.CharField(max_length=2048)
    proj4text = models.CharField(max_length=2048)
    class Meta:
        db_table = u'spatial_ref_sys'

class VwConcepts(models.Model):
    conceptid = models.TextField(primary_key=True) # This field type is a guess.
    conceptlabel = models.TextField()
    legacyoid = models.TextField()
    class Meta:
        db_table = u'vw_concepts'

class VwEdges(models.Model):
    source = models.TextField() # This field type is a guess.
    label = models.TextField()
    target = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'vw_edges'

class VwEntityTypes(models.Model):
    entitytypeid = models.TextField()
    entitytypename = models.TextField()
    description = models.TextField()
    languageid = models.TextField()
    reportwidget = models.TextField()
    icon = models.TextField()
    isresource = models.BooleanField()
    conceptid = models.TextField() # This field type is a guess.
    class Meta:
        db_table = u'vw_entity_types'

class VwNodes(models.Model):
    label = models.TextField()
    id = models.TextField(primary_key=True) # This field type is a guess.
    val = models.TextField()
    class Meta:
        db_table = u'vw_nodes'

class VwEntitytypeDomains(models.Model):
    id = models.TextField(primary_key=True) # This field type is a guess.
    entitytypeid = models.TextField(blank=True)
    conceptid = models.TextField(blank=True) # This field type is a guess.
    value = models.TextField(blank=True)
    valuetype = models.TextField(blank=True)
    languageid = models.TextField(blank=True)
    sortorder = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'vw_entitytype_domains'

class AuthMessage(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey('AuthUser')
    message = models.TextField()
    class Meta:
        db_table = u'auth_message'

class AuthPermission(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    content_type = models.ForeignKey('DjangoContentType')
    codename = models.CharField(max_length=100)
    class Meta:
        db_table = u'auth_permission'

class Concepts(models.Model):
    conceptid = models.TextField(primary_key=True) # This field type is a guess.
    nodetype = models.ForeignKey('DNodetypes', db_column='nodetype')
    legacyoid = models.TextField()
    class Meta:
        db_table = u'concepts'

    def __unicode__(self):
        return ('%s') % (self.conceptid)

class ConceptRelations(models.Model):
    relationid = models.TextField(primary_key=True)
    conceptidfrom = models.ForeignKey('Concepts', db_column='conceptidfrom', related_name='concept_relation_from')
    conceptidto = models.ForeignKey('Concepts', db_column='conceptidto', related_name='concept_relation_to')
    relationtype = models.ForeignKey('DRelationtypes', db_column='relationtype', related_name='concept_relation_type')
    class Meta:
        db_table = u'concepts"."relations'

    def __unicode__(self):
        return ('%s') % (self.relationid)

    def save(self, *args, **kwargs):
        # prevent insert of duplicate records
        if ConceptRelations.objects.filter(conceptidfrom = self.conceptidfrom, conceptidto = self.conceptidto, relationtype = self.relationtype).exists():
            return # can't insert duplicate values
        elif self.relationtype_id == 'related':
            # check to see if the recipocal relationship exists as well (mostly for when we load a skos file)
            if ConceptRelations.objects.filter(conceptidfrom = self.conceptidto, conceptidto = self.conceptidfrom, relationtype = self.relationtype).exists():
                return

        super(ConceptRelations, self).save(*args, **kwargs) # Call the "real" save() method.

class ValueTypes(models.Model):
    valuetype = models.TextField(primary_key=True)
    category = models.TextField()
    description = models.TextField()
    namespace = models.TextField()
    class Meta:
        db_table = u'concepts"."d_valuetypes'

    def __unicode__(self):
        return ('valuetype: %s, category: %s') % (self.valuetype, self.category)

class Values(models.Model):
    valueid = models.TextField(primary_key=True) # This field type is a guess.
    conceptid = models.ForeignKey('Concepts', db_column='conceptid')
    valuetype = models.ForeignKey('ValueTypes', db_column='valuetype')
    value = models.TextField()
    languageid = models.ForeignKey('DLanguages', db_column='languageid')
    class Meta:
        db_table = u'values'

class FileValues(models.Model):
    valueid = models.TextField(primary_key=True) # This field type is a guess.
    conceptid = models.ForeignKey('Concepts', db_column='conceptid')
    valuetype = models.ForeignKey('ValueTypes', db_column='valuetype')
    value = models.FileField(upload_to='concepts')
    languageid = models.ForeignKey('DLanguages', db_column='languageid')
    class Meta:
        db_table = u'values'

    def geturl(self):
        if self.value != None:
            return self.value.url
        return ''

    def getname(self):
        if self.value != None:
            return self.value.name[6:]
        return ''

class AuthGroupPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    group = models.ForeignKey('AuthGroup')
    permission = models.ForeignKey('AuthPermission')
    class Meta:
        db_table = u'auth_group_permissions'

class AuthUserGroups(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey('AuthUser')
    group = models.ForeignKey('AuthGroup')
    class Meta:
        db_table = u'auth_user_groups'

class AuthUserUserPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey('AuthUser')
    permission = models.ForeignKey('AuthPermission')
    class Meta:
        db_table = u'auth_user_user_permissions'

class Properties(models.Model):
    propertyid = models.TextField(primary_key=True)
    classdomain = models.ForeignKey('Classes', db_column='classdomain', related_name='properties_classdomain')
    classrange = models.ForeignKey('Classes', db_column='classrange', related_name='properties_classrange')
    propertydisplay = models.TextField()
    class Meta:
        db_table = u'properties'

class EntityTypes(models.Model):
    classid = models.ForeignKey('Classes', db_column='classid', related_name='entitytypes_classid')
    conceptid = models.ForeignKey('Concepts', db_column='conceptid', related_name='entitytypes_conceptid')
    businesstablename = models.TextField()
    publishbydefault = models.BooleanField()
    icon = models.TextField()
    defaultvectorcolor = models.TextField()
    entitytypeid = models.TextField(primary_key=True)
    isresource = models.BooleanField()
    class Meta:
        db_table = u'data"."entity_types'

    def getcolumnname(self):
        ret = None
        if self.businesstablename is not None and self.businesstablename != 'entities':
            ret = 'val'

        return ret     

    def __unicode__(self):
        return ('%s') % (self.entitytypeid)

class Entities(models.Model):
    entityid = models.TextField(primary_key=True) # This field type is a guess.
    entitytypeid = models.ForeignKey('EntityTypes', db_column='entitytypeid')
    class Meta:
        db_table = u'data"."entities'

    def __unicode__(self):
        return ('%s of type %s') % (self.entityid, self.entitytypeid)

class Strings(models.Model):
    entityid = models.ForeignKey('Entities', primary_key=True, db_column='entityid')
    val = models.TextField()
    class Meta:
        db_table = u'strings'

class Dates(models.Model):
    entityid = models.ForeignKey('Entities', primary_key=True, db_column='entityid')
    val = models.DateTimeField()
    class Meta:
        db_table = u'dates'

    def __unicode__(self):
        return ('%s') % (self.val)

class Numbers(models.Model):
    entityid = models.ForeignKey('Entities', primary_key=True, db_column='entityid')
    val = models.DecimalField(max_digits=65535, decimal_places=65534)
    class Meta:
        db_table = u'numbers'
        
class Files(models.Model):
    entityid = models.ForeignKey('Entities', primary_key=True, db_column='entityid')
    val = models.FileField(upload_to='files')
    class Meta:
        db_table = u'files'

    def geturl(self):
        if self.val != None:
            return self.val.url
        return ''

    def getname(self):
        if self.val != None:
            return self.val.name[6:]
        return ''

# These two event listeners auto-delete files from filesystem when they are unneeded:
# from http://stackoverflow.com/questions/16041232/django-delete-filefield
@receiver(models.signals.post_delete, sender=Files)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `Files` object is deleted.
    """
    if instance.val:
        if os.path.isfile(instance.val.path):
            os.remove(instance.val.path)

@receiver(models.signals.pre_save, sender=Files)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `Files` object is changed.
    """

    if not instance.pk:
        return False

    try:
        old_file = Files.objects.get(pk=instance.pk).val
    except Files.DoesNotExist:
        return False

    new_file = instance.val
    if not old_file == new_file:
        try:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
        except Exception:
            return False

class Geometries(models.Model):
    entityid = models.ForeignKey('Entities', primary_key=True, db_column='entityid')
    val = models.GeometryField()
    objects = models.GeoManager()
    class Meta:
        db_table = u'geometries'

class EditLog(models.Model):
    editlogid = models.TextField(primary_key=True)
    resourceentitytypeid = models.TextField()
    resourceid = models.TextField()
    attributeentitytypeid = models.TextField()
    edittype = models.TextField()
    userid = models.TextField()
    timestamp = models.DateTimeField()
    oldvalue = models.TextField()
    newvalue = models.TextField()
    user_email = models.TextField()
    user_firstname = models.TextField()
    user_lastname = models.TextField()
    note = models.TextField()
    class Meta:
        db_table = u'data"."edit_log'

class Domains(models.Model):
    entityid = models.ForeignKey('Entities', primary_key=True, db_column='entityid')
    val = models.ForeignKey('Values', db_column='val', null=True)
    class Meta:
        db_table = u'domains'

    def getlabelid(self):
        if self.val_id != None:
            return self.val_id
        return ''

    def getlabelvalue(self):
        if self.val != None:
            return self.val.value   
        return ''

    # def __getattr__(self, name):
    #     print name        
    #     if name == 'val' and self.val_id != None:

    #         return self.val_id
    #     else:
    #         return super(Domains, self).__getattr__(name)

    def __setattr__(self, name, value):
        if name == 'val':
            if not isinstance(value, Values):
                try:
                    uuid.UUID(value)
                    value = Values.objects.get(valueid = value)
                except(ValueError, TypeError):
                    # print value, 'attr value'
                    concepts = Concepts.objects.filter(legacyoid = value)
                    if len(concepts) == 1:
                        value = Values.objects.get(conceptid = concepts[0], valuetype = 'prefLabel')
                    else:
                        # print 'unable to find, or found more then 1 Concept with legacyoid: %s' % (value)
                        value = None

        super(Domains, self).__setattr__(name, value)

class Mappings(models.Model):
    mappingid = models.TextField(primary_key=True) # This field type is a guess.
    entitytypeidfrom = models.ForeignKey('EntityTypes', db_column='entitytypeidfrom', related_name='mappings_entitytypeidfrom')
    entitytypeidto = models.ForeignKey('EntityTypes', db_column='entitytypeidto', related_name='mappings_entitytypeidto')
    mergenodeid = models.TextField()
    class Meta:
        db_table = u'ontology"."mappings'

    def __unicode__(self):
        return ('%s -- %s') % (self.entitytypeidfrom, self.entitytypeidto)

class Rules(models.Model):
    ruleid = models.TextField(primary_key=True) # This field type is a guess.
    entitytypedomain = models.ForeignKey('EntityTypes', db_column='entitytypedomain', related_name='rules_entitytypedomain')
    entitytyperange = models.ForeignKey('EntityTypes', db_column='entitytyperange', related_name='rules_entitytyperange')
    propertyid = models.ForeignKey('Properties', db_column='propertyid')
    class Meta:
        db_table = u'rules'

class MappingSteps(models.Model):
    mappingid = models.ForeignKey('Mappings', primary_key=True, db_column='mappingid')
    ruleid = models.ForeignKey('Rules', db_column='ruleid')
    order = models.IntegerField()
    class Meta:
        db_table = u'mapping_steps'

class Relations(models.Model):
    relationid = models.AutoField(primary_key=True)
    ruleid = models.ForeignKey('Rules', db_column='ruleid')
    entityiddomain = models.ForeignKey('Entities', db_column='entityiddomain', related_name='rules_entityiddomain')
    entityidrange = models.ForeignKey('Entities', db_column='entityidrange', related_name='rules_entityidrange')
    notes = models.TextField()
    class Meta:
        db_table = u'data"."relations'

    def __unicode__(self):
        return ('%s is the parent of %s') % (self.entityiddomain, self.entityidrange)

    def save(self, *args, **kwargs):
        if Relations.objects.filter(ruleid = self.ruleid, entityiddomain = self.entityiddomain, entityidrange = self.entityidrange).exists():
            return # can't insert duplicate values
        else:
            super(Relations, self).save(*args, **kwargs) # Call the "real" save() method.

class RelatedResource(models.Model):
    resourcexid = models.AutoField(primary_key=True)
    entityid1 = models.TextField()
    entityid2 = models.TextField()
    notes = models.TextField()
    relationshiptype = models.TextField()
    datestarted = models.DateField()
    dateended = models.DateField()
    class Meta:
        db_table = u'data"."resource_x_resource'

class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    details = models.TextField()

    class Meta:
        db_table = u'user_profile'

    def __unicode__(self):
        return str(self.user.username)

    def save(self, *args, **kwargs):
        """Validates JSON prior to saving"""
        try:
            json.loads(self.details)
            super(UserProfile, self).save(*args, **kwargs) # Call the "real" save() method.
        except:
            return #'json invalid'