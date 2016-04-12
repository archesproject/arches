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
    branchmetadataid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    deploymentfile = models.TextField(blank=True, null=True)
    author = models.TextField(blank=True, null=True)
    deploymentdate = models.DateTimeField(blank=True, null=True)
    version = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'branch_metadata'


class Card(models.Model):
    cardid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    name = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    subtitle = models.TextField(blank=True, null=True)
    helptext = models.TextField(blank=True, null=True)
    nodegroup = models.ForeignKey('NodeGroup', db_column='nodegroupid', blank=True, null=True)
    parentcard = models.ForeignKey('self', db_column='parentcardid', blank=True, null=True) #Allows for cards within cards (ie cardgroups)

    class Meta:
        managed = True
        db_table = 'cards'


class CardXNodeXWidget(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1)
    node = models.ForeignKey('Node', db_column='nodeid')
    card = models.ForeignKey(Card, db_column='cardid')
    widget = models.ForeignKey('Widget', db_column='widgetid')
    inputmask = models.TextField(blank=True, null=True)
    inputlabel = models.TextField(blank=True, null=True)


    class Meta:
        managed = True
        db_table = 'cards_x_nodes_x_widgets'
        unique_together = (('node', 'card', 'widget'),)


class Concept(models.Model):
    conceptid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    nodetype = models.ForeignKey('DNodeType', db_column='nodetype')
    legacyoid = models.TextField(unique=True)

    class Meta:
        managed = True
        db_table = 'concepts'

class DDataType(models.Model):
    datatype = models.TextField(primary_key=True)
    iconclass = models.TextField()

    class Meta:
        managed = True
        db_table = 'd_data_types'

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
        db_table = 'd_node_types'


class DRelationType(models.Model):
    relationtype = models.TextField(primary_key=True)
    category = models.TextField()
    namespace = models.TextField()

    class Meta:
        managed = True
        db_table = 'd_relation_types'


class DValueType(models.Model):
    valuetype = models.TextField(primary_key=True)
    category = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    namespace = models.TextField()
    datatype = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'd_value_types'


class Edge(models.Model):
    edgeid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    ontologyproperty = models.TextField(blank=True, null=True)
    domainnode = models.ForeignKey('Node', db_column='domainnodeid', related_name='edge_domains')
    rangenode = models.ForeignKey('Node', db_column='rangenodeid', related_name='edge_ranges')
    branchmetadata = models.ForeignKey(BranchMetadata, db_column='branchmetadataid', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'edges'
        unique_together = (('rangenode', 'domainnode'),)


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
    title = models.TextField(blank=True, null=True)
    subtitle = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'forms'


class FormXCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1)
    form = models.ForeignKey(Form, db_column='formid')
    card = models.ForeignKey(Card, db_column='cardid')

    class Meta:
        managed = True
        db_table = 'forms_x_card'
        unique_together = (('form', 'card'),)


class NodeGroup(models.Model):
    nodegroupid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    cardinality = models.TextField(blank=True, default='n')
    legacygroupid = models.TextField(blank=True, null=True)
    parentnodegroup = models.ForeignKey('self', db_column='parentnodegroupid', blank=True, null=True)  #Allows nodegroups within nodegroups

    class Meta:
        managed = True
        db_table = 'node_groups'


class Node(models.Model):
    """
    Name is unique across all resources because it ties a node to values within tiles. Recommend prepending resource class to node name.

    """

    nodeid = models.UUIDField(primary_key=True, default=uuid.uuid1)
    name = models.TextField()
    description = models.TextField(blank=True, null=True)
    istopnode = models.BooleanField()
    ontologyclass = models.TextField()
    datatype = models.TextField()
    nodegroup = models.ForeignKey(NodeGroup, db_column='nodegroupid', blank=True, null=True)
    branchmetadata = models.ForeignKey(BranchMetadata, db_column='branchmetadataid', blank=True, null=True)

    def get_child_nodes_and_edges(self):
        nodes = []
        edges = []
        for edge in Edge.objects.filter(domainnode=self):
            nodes.append(edge.rangenode)
            edges.append(edge)

            child_nodes, child_edges = edge.rangenode.get_child_nodes_and_edges()
            nodes.extend(child_nodes)
            edges.extend(child_edges)
        return (nodes, edges)

    def is_collector(self):
        return self.nodeid == self.nodegroup_id

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
    conceptfrom = models.ForeignKey(Concept, db_column='conceptidfrom', related_name='relation_concepts_from')
    conceptto = models.ForeignKey(Concept, db_column='conceptidto', related_name='relation_concepts_to')
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
        db_table = 'resource_2_resource_constraints'


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
    id = models.UUIDField(primary_key=True, default=uuid.uuid1)
    resourceclass = models.ForeignKey(Node, db_column='resourceclassid', blank=True, null=True)
    form = models.ForeignKey(Form, db_column='formid')
    status = models.TextField(blank=True, null=True) #This hides forms that may be deployed by an implementor for testing purposes. Once the switch is flipped to "prod" then regular permissions (defined at the nodegroup level) come into play.

    class Meta:
        managed = True
        db_table = 'resource_classes_x_forms'
        unique_together = (('resourceclass', 'form'),)


class ResourceInstance(models.Model):
    resourceinstanceid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    resourceclass = models.ForeignKey(Node, db_column='resourceclassid')
    resourceinstancesecurity = models.TextField(blank=True, null=True) #Intended to support flagging individual resources as unavailable to given user roles.

    class Meta:
        managed = True
        db_table = 'resource_instances'


class Tile(models.Model): #Tile
    tileid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    resourceinstance = models.ForeignKey(ResourceInstance, db_column='resourceinstanceid')
    parenttile = models.ForeignKey('self', db_column='parenttileid', blank=True, null=True)
    data = JSONField(blank=True, null=True, db_column='tiledata')  # This field type is a guess.
    nodegroup = models.ForeignKey(NodeGroup, db_column='nodegroupid')

    class Meta:
        managed = True
        db_table = 'tiles'


class Validation(models.Model):
    validationid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    validation = models.TextField(blank=True, null=True)
    validationtype = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'validations'


class ValidationXNode(models.Model):
    validationid = models.ForeignKey(Validation, db_column='validationid')
    nodeid = models.ForeignKey(Node, db_column='nodeid')

    class Meta:
        managed = True
        db_table = 'validations_x_nodes'


class Value(models.Model):
    valueid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    concept = models.ForeignKey('Concept', db_column='conceptid')
    valuetype = models.ForeignKey(DValueType, db_column='valuetype')
    value = models.TextField()
    language = models.ForeignKey(DLanguage, db_column='languageid', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'values'


class Widget(models.Model):
    widgetid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    name = models.TextField()
    template = models.FileField(storage=widget_storage_location)
    defaultlabel = models.TextField(blank=True, null=True)
    defaultmask = models.TextField(blank=True, null=True)
    helptext = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'widgets'


class WidgetXDataType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    widget = models.ForeignKey(db_column='widgetid', to='models.Widget')
    datatype = models.ForeignKey(db_column='datatypeid', to='models.DDataType')

    class Meta:
        managed = True
        db_table = 'widgets_x_datatypes'
