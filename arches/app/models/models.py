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

from django.contrib.gis.db import models
import uuid

class Addresses(models.Model):
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


class Branchmetadata(models.Model):
    branchmetadataid = models.UUIDField(primary_key=True, default=uuid.uuid1, editable=False)  # This field type is a guess.
    name = models.BigIntegerField(blank=True, null=True)
    deploymentfile = models.TextField(blank=True, null=True)
    author = models.TextField(blank=True, null=True)
    deploymentdate = models.DateTimeField(blank=True, null=True)
    version = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'branchmetadata'


class Cardgroups(models.Model):
    cardgroupid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    name = models.TextField()
    title = models.TextField()
    subtitle = models.TextField(blank=True, null=True)
    nodeid = models.ForeignKey('Nodes', db_column='nodeid', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'cardgroups'


class Cards(models.Model):
    cardid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    name = models.TextField()
    htmltemplate = models.TextField()
    title = models.TextField()
    subtitle = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'cards'


class CardsXCardgroups(models.Model):
    cardgroupid = models.ForeignKey(Cardgroups, db_column='cardgroupid')
    cardid = models.ForeignKey('Cards', db_column='cardid')

    class Meta:
        managed = True
        db_table = 'cards_x_cardgroups'
        unique_together = (('cardgroupid', 'cardid'),)


class CardsXNodesXWidgets(models.Model):
    nodeid = models.ForeignKey('Nodes', db_column='nodeid')
    cardid = models.ForeignKey(Cards, db_column='cardid')
    widgetid = models.ForeignKey('Widgets', db_column='widgetid')

    class Meta:
        managed = True
        db_table = 'cards_x_nodes_x_widgets'
        unique_together = (('nodeid', 'cardid', 'widgetid'),)


class Classes(models.Model):
    classid = models.UUIDField(primary_key=True, default=uuid.uuid1)
    classname = models.TextField()
    isactive = models.BooleanField()

    class Meta:
        managed = True
        db_table = 'classes'


class Concepts(models.Model):
    conceptid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    nodetype = models.ForeignKey('DNodetypes', db_column='nodetype')
    legacyoid = models.TextField(unique=True)

    class Meta:
        managed = True
        db_table = 'concepts'


class DLanguages(models.Model):
    languageid = models.TextField(primary_key=True)
    languagename = models.TextField()
    isdefault = models.BooleanField()

    class Meta:
        managed = True
        db_table = 'd_languages'


class DNodetypes(models.Model):
    nodetype = models.TextField(primary_key=True)
    namespace = models.TextField()

    class Meta:
        managed = True
        db_table = 'd_nodetypes'


class DRelationtypes(models.Model):
    relationtype = models.TextField(primary_key=True)
    category = models.TextField()
    namespace = models.TextField()

    class Meta:
        managed = True
        db_table = 'd_relationtypes'


class DValuetypes(models.Model):
    valuetype = models.TextField(primary_key=True)
    category = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    namespace = models.TextField()
    datatype = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'd_valuetypes'


class Edges(models.Model):
    edgeid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    name = models.TextField()
    description = models.TextField()
    crmproperty = models.TextField()
    domainnodeid = models.ForeignKey('Nodes', db_column='domainnodeid', related_name='edge_domains')
    rangenodeid = models.ForeignKey('Nodes', db_column='rangenodeid', related_name='edge_ranges')
    branchmetadataid = models.ForeignKey(Branchmetadata, db_column='branchmetadataid', blank=True, null=True)

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


class Forms(models.Model):
    formid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    name = models.TextField()
    title = models.TextField(blank=True, null=True)
    subtitle = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'forms'


class FormsXCardGroups(models.Model):
    formid = models.ForeignKey(Forms, db_column='formid')
    cardgroupid = models.ForeignKey(Cardgroups, db_column='cardgroupid')

    class Meta:
        managed = True
        db_table = 'forms_x_card_groups'
        unique_together = (('formid', 'cardgroupid'),)


class Nodegroups(models.Model):
    nodegroupid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    cardinality = models.TextField()
    legacygroupid = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'nodegroups'


class Nodes(models.Model):
    nodeid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    name = models.TextField()
    description = models.TextField()
    istopnode = models.BooleanField()
    crmclass = models.TextField()
    datatype = models.TextField()
    validation = models.TextField(blank=True, null=True)
    inputlabel = models.TextField(blank=True, null=True)
    inputmask = models.TextField(blank=True, null=True)
    status = models.BigIntegerField(blank=True, null=True)
    nodegroupid = models.ForeignKey(Nodegroups, db_column='nodegroupid', blank=True, null=True)
    branchmetadataid = models.ForeignKey(Branchmetadata, db_column='branchmetadataid', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'nodes'


class Overlays(models.Model):
    overlaytyp = models.TextField(blank=True, null=True)
    overlayval = models.TextField(blank=True, null=True)
    overlayid = models.AutoField(primary_key=True)  # This field type is a guess.
    geometry = models.PolygonField(blank=True, null=True)
    objects = models.GeoManager()

    class Meta:
        managed = True
        db_table = 'overlays'


class Parcels(models.Model):
    parcelapn = models.TextField(blank=True, null=True)
    vintage = models.TextField(blank=True, null=True)
    parcelsid = models.AutoField(primary_key=True)
    geometry = models.PolygonField(blank=True, null=True)
    objects = models.GeoManager()

    class Meta:
        managed = True
        db_table = 'parcels'


class Properties(models.Model):
    propertyid = models.UUIDField(primary_key=True, default=uuid.uuid1)
    classdomain = models.ForeignKey(Classes, db_column='classdomain', related_name='property_classdomains')
    classrange = models.ForeignKey(Classes, db_column='classrange', related_name='property_classranges')
    propertydisplay = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'properties'


class Relations(models.Model):
    conceptidfrom = models.ForeignKey(Concepts, db_column='conceptidfrom', related_name='relation_concepts_from')
    conceptidto = models.ForeignKey(Concepts, db_column='conceptidto', related_name='relation_concepts_to')
    relationtype = models.ForeignKey(DRelationtypes, db_column='relationtype')
    relationid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.

    class Meta:
        managed = True
        db_table = 'relations'


class Resource2ResourceConstraints(models.Model):
    resource2resourceid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    resourceclassfrom = models.ForeignKey(Nodes, db_column='resourceclassfrom', blank=True, null=True, related_name='resxres_contstraint_classes_from')
    resourceclassto = models.ForeignKey(Nodes, db_column='resourceclassto', blank=True, null=True, related_name='resxres_contstraint_classes_to')
    cardinality = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'resource2resource_constraints'


class ResourceXResource(models.Model):
    resourcexid = models.AutoField(primary_key=True)
    resourceinstanceidfrom = models.ForeignKey('Resourceinstances', db_column='resourceinstanceidfrom', blank=True, null=True, related_name='resxres_resource_instance_ids_from')
    resourceinstanceidto = models.ForeignKey('Resourceinstances', db_column='resourceinstanceidto', blank=True, null=True, related_name='resxres_resource_instance_ids_to')
    notes = models.TextField(blank=True, null=True)
    relationshiptype = models.ForeignKey('Values', db_column='relationshiptype')
    datestarted = models.DateField(blank=True, null=True)
    dateended = models.DateField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'resource_x_resource'


class ResourceclassesXForms(models.Model):
    resourceclassid = models.ForeignKey(Nodes, db_column='resourceclassid', blank=True, null=True)
    formid = models.ForeignKey(Forms, db_column='formid')

    class Meta:
        managed = True
        db_table = 'resourceclasses_x_forms'
        unique_together = (('resourceclassid', 'formid'),)


class Resourceinstances(models.Model):
    resourceinstanceid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    col1 = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'resourceinstances'


class Tileinstances(models.Model):
    tileinstanceid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    resourceinstanceid = models.ForeignKey(Resourceinstances, db_column='resourceinstanceid')
    resourceclassid = models.ForeignKey(Nodes, db_column='resourceclassid')
    cardid = models.ForeignKey('Cards', db_column='cardid')
    parenttileinstanceid = models.ForeignKey('self', db_column='parenttileinstanceid', blank=True, null=True)
    tilegroupid = models.TextField()  # This field type is a guess.
    tileinstancedata = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = True
        db_table = 'tileinstances'


class Values(models.Model):
    valueid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    conceptid = models.ForeignKey('Concepts', db_column='conceptid')
    valuetype = models.ForeignKey(DValuetypes, db_column='valuetype')
    value = models.TextField()
    languageid = models.ForeignKey(DLanguages, db_column='languageid', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'values'


class Widgets(models.Model):
    widgetid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    name = models.TextField()
    defaultlabel = models.TextField(blank=True, null=True)
    defaultmask = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'widgets'
