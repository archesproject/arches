# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.

from __future__ import unicode_literals

import os
import uuid
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.core.files.storage import FileSystemStorage

widget_storage_location = FileSystemStorage(location=os.path.join(settings.ROOT_DIR, 'app/templates/views/forms/widgets/'))


class Address(models.Model):
    addressnum = models.TextField(blank=True, null=True)
    addressstreet = models.TextField(blank=True, null=True)
    vintage = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    postalcode = models.TextField(blank=True, null=True)
    addressesid = models.AutoField(primary_key=True)
    geometry = models.PointField(blank=True, null=True)
    objects = models.GeoManager()

    class Meta:
        managed = True
        db_table = 'addresses'


class BranchMetadata(models.Model):
    branchmetadataid = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)  # This field type is a guess.
    name = models.BigIntegerField(blank=True, null=True)
    deploymentfile = models.TextField(blank=True, null=True)
    author = models.TextField(blank=True, null=True)
    deploymentdate = models.DateTimeField(blank=True, null=True)
    version = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'branchmetadata'


class Card(models.Model):
    cardid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    name = models.TextField()
    title = models.TextField()
    subtitle = models.TextField(blank=True, null=True)
    helptext = models.TextField(blank=True, null=True)
    nodegroupid = models.ForeignKey('NodeGroup', db_column='nodegroupid', blank=True, null=True)
    parentcardid = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'cards'


class CardXNodeXWidget(models.Model):
    nodeid = models.ForeignKey('Node', db_column='nodeid')
    cardid = models.ForeignKey(Card, db_column='cardid')
    widgetid = models.ForeignKey('Widget', db_column='widgetid')

    class Meta:
        managed = True
        db_table = 'cards_x_nodes_x_widgets'
        unique_together = (('nodeid', 'cardid', 'widgetid'),)


class Concept(models.Model):
    conceptid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    nodetype = models.ForeignKey('DNodeType', db_column='nodetype')
    legacyoid = models.TextField(unique=True)

    class Meta:
        managed = True
        db_table = 'concepts'


class DLanguage(models.Model):
    languageid = models.TextField(primary_key=True)
    languagename = models.TextField()
    isdefault = models.BooleanField()

    class Meta:
        managed = True
        db_table = 'd_languages'


class DNodeType(models.Model):
    nodetype = models.TextField(primary_key=True)
    namespace = models.TextField()

    class Meta:
        managed = True
        db_table = 'd_nodetypes'


class DRelationType(models.Model):
    relationtype = models.TextField(primary_key=True)
    category = models.TextField()
    namespace = models.TextField()

    class Meta:
        managed = True
        db_table = 'd_relationtypes'


class DValueType(models.Model):
    valuetype = models.TextField(primary_key=True)
    category = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    namespace = models.TextField()
    datatype = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'd_valuetypes'


class Edge(models.Model):
    edgeid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    name = models.TextField()
    description = models.TextField()
    crmproperty = models.TextField()
    domainnodeid = models.ForeignKey('Node', db_column='domainnodeid', related_name='edge_domains')
    rangenodeid = models.ForeignKey('Node', db_column='rangenodeid', related_name='edge_ranges')
    branchmetadataid = models.ForeignKey(BranchMetadata, db_column='branchmetadataid', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'edges'
        unique_together = (('rangenodeid', 'domainnodeid'),)


class EditLog(models.Model):
    editlogid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    resourceclassid = models.TextField(blank=True, null=True)  # This field type is a guess.
    resourceinstanceid = models.TextField(blank=True, null=True)  # This field type is a guess.
    attributenodeid = models.TextField(blank=True, null=True)  # This field type is a guess.
    tileinstanceid = models.TextField(blank=True, null=True)  # This field type is a guess.
    edittype = models.TextField(blank=True, null=True)
    newvalue = models.TextField(blank=True, null=True)
    oldvalue = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    userid = models.TextField(blank=True, null=True)
    user_firstname = models.TextField(blank=True, null=True)
    user_lastname = models.TextField(blank=True, null=True)
    user_email = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'edit_log'


class Form(models.Model):
    formid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    name = models.TextField()
    title = models.TextField(blank=True, null=True)
    subtitle = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'forms'


class FormXCard(models.Model):
    formid = models.ForeignKey(Form, db_column='formid')
    parentcardid = models.ForeignKey(Card, db_column='parentcardid')

    class Meta:
        managed = True
        db_table = 'forms_x_card'
        unique_together = (('formid', 'parentcardid'),)


class NodeGroup(models.Model):
    nodegroupid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    cardinality = models.TextField()
    legacygroupid = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'nodegroups'


class Node(models.Model):
    """
    Name is unique across all resources because it ties a node to values within tiles. Recommend prepending resource class to node name.
    """
    nodeid = models.UUIDField(primary_key=True, default=uuid.uuid1)
    name = models.TextField(unique=True)
    description = models.TextField()
    istopnode = models.BooleanField()
    crmclass = models.TextField()
    datatype = models.TextField()
    validation = models.TextField(blank=True, null=True)
    inputlabel = models.TextField(blank=True, null=True)
    inputmask = models.TextField(blank=True, null=True)
    status = models.BigIntegerField(blank=True, null=True)
    nodegroupid = models.ForeignKey(NodeGroup, db_column='nodegroupid', blank=True, null=True)
    branchmetadataid = models.ForeignKey(BranchMetadata, db_column='branchmetadataid', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'nodes'


class Overlay(models.Model):
    overlaytyp = models.TextField(blank=True, null=True)
    overlayval = models.TextField(blank=True, null=True)
    overlayid = models.AutoField(primary_key=True)  # This field type is a guess.
    geometry = models.PolygonField(blank=True, null=True)
    objects = models.GeoManager()

    class Meta:
        managed = True
        db_table = 'overlays'


class Parcel(models.Model):
    parcelapn = models.TextField(blank=True, null=True)
    vintage = models.TextField(blank=True, null=True)
    parcelsid = models.AutoField(primary_key=True)
    geometry = models.PolygonField(blank=True, null=True)
    objects = models.GeoManager()

    class Meta:
        managed = True
        db_table = 'parcels'


class Relation(models.Model):
    conceptidfrom = models.ForeignKey(Concept, db_column='conceptidfrom', related_name='relation_concepts_from')
    conceptidto = models.ForeignKey(Concept, db_column='conceptidto', related_name='relation_concepts_to')
    relationtype = models.ForeignKey(DRelationType, db_column='relationtype')
    relationid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.

    class Meta:
        managed = True
        db_table = 'relations'


class Resource2ResourceConstraint(models.Model):
    resource2resourceid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    resourceclassfrom = models.ForeignKey(Node, db_column='resourceclassfrom', blank=True, null=True, related_name='resxres_contstraint_classes_from')
    resourceclassto = models.ForeignKey(Node, db_column='resourceclassto', blank=True, null=True, related_name='resxres_contstraint_classes_to')
    cardinality = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'resource2resource_constraints'


class ResourceXResource(models.Model):
    resourcexid = models.AutoField(primary_key=True)
    resourceinstanceidfrom = models.ForeignKey('ResourceInstance', db_column='resourceinstanceidfrom', blank=True, null=True, related_name='resxres_resource_instance_ids_from')
    resourceinstanceidto = models.ForeignKey('ResourceInstance', db_column='resourceinstanceidto', blank=True, null=True, related_name='resxres_resource_instance_ids_to')
    notes = models.TextField(blank=True, null=True)
    relationshiptype = models.ForeignKey('Value', db_column='relationshiptype')
    datestarted = models.DateField(blank=True, null=True)
    dateended = models.DateField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'resource_x_resource'


class ResourceClassXForm(models.Model):
    resourceclassid = models.ForeignKey(Node, db_column='resourceclassid', blank=True, null=True)
    formid = models.ForeignKey(Form, db_column='formid')

    class Meta:
        managed = True
        db_table = 'resourceclasses_x_forms'
        unique_together = (('resourceclassid', 'formid'),)


class ResourceInstance(models.Model):
    resourceinstanceid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    resourceclassid = models.ForeignKey(Node, db_column='resourceclassid')
    col1 = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'resourceinstances'


class Tile(models.Model): #Tile
    tileid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    resourceinstanceid = models.ForeignKey(ResourceInstance, db_column='resourceinstanceid')
    parenttileid = models.ForeignKey('self', db_column='parenttileid', blank=True, null=True)
    tiledata = JSONField(blank=True, null=True, db_column='tiledata')  # This field type is a guess.
    nodegroupid = models.ForeignKey(NodeGroup, db_column='nodegroupid')

    class Meta:
        managed = True
        db_table = 'tiles'


class Value(models.Model):
    valueid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    conceptid = models.ForeignKey('Concept', db_column='conceptid')
    valuetype = models.ForeignKey(DValueType, db_column='valuetype')
    value = models.TextField()
    languageid = models.ForeignKey(DLanguage, db_column='languageid', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'values'


class Widget(models.Model):
    widgetid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    name = models.TextField()
    template = models.FileField(storage=widget_storage_location)
    defaultlabel = models.TextField(blank=True, null=True)
    defaultmask = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'widgets'
