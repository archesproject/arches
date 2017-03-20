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
import json
import uuid
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models import Q, Max
from django.core.files.storage import FileSystemStorage
from django.dispatch import receiver
from django.utils.translation import ugettext as _
from datetime import datetime
from arches.app.search.search_engine_factory import SearchEngineFactory
from django.forms.models import model_to_dict


def get_ontology_storage_system():
    return FileSystemStorage(location=os.path.join(settings.ROOT_DIR, 'db', 'ontologies'))


class CardModel(models.Model):
    cardid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)
    helpenabled = models.BooleanField(default=False)
    helptitle = models.TextField(blank=True, null=True)
    helptext = models.TextField(blank=True, null=True)
    nodegroup = models.ForeignKey('NodeGroup', db_column='nodegroupid')
    graph = models.ForeignKey('GraphModel', db_column='graphid')
    active = models.BooleanField(default=True)
    visible = models.BooleanField(default=True)
    sortorder = models.IntegerField(blank=True, null=True, default=None)

    class Meta:
        managed = True
        db_table = 'cards'


class CardXNodeXWidget(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1)
    node = models.ForeignKey('Node', db_column='nodeid')
    card = models.ForeignKey('CardModel', db_column='cardid')
    widget = models.ForeignKey('Widget', db_column='widgetid')
    config = JSONField(blank=True, null=True, db_column='config')
    label = models.TextField(blank=True, null=True)
    sortorder = models.IntegerField(blank=True, null=True, default=None)

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
    modulename = models.TextField(blank=True, null=True)
    classname = models.TextField(blank=True, null=True)
    defaultwidget = models.ForeignKey(db_column='defaultwidget', to='models.Widget', null=True)
    defaultconfig = JSONField(blank=True, null=True, db_column='defaultconfig')
    configcomponent = models.TextField(blank=True, null=True)
    configname = models.TextField(blank=True, null=True)
    isgeometric = models.BooleanField()

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
    graph = models.ForeignKey('GraphModel', db_column='graphid', blank=True, null=True)

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


class File(models.Model):
    fileid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    path = models.FileField(upload_to='uploadedfiles')

    class Meta:
        managed = True
        db_table = 'files'


# These two event listeners auto-delete files from filesystem when they are unneeded:
# from http://stackoverflow.com/questions/16041232/django-delete-filefield
@receiver(models.signals.post_delete, sender=File)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `File` object is deleted.
    """
    if instance.path:
        try:
            if os.path.isfile(instance.path.path):
                os.remove(instance.path.path)
        ## except block added to deal with S3 file deletion
        ## see comments on 2nd answer below
        ## http://stackoverflow.com/questions/5372934/how-do-i-get-django-admin-to-delete-files-when-i-remove-an-object-from-the-datab
        except:
            storage, name = instance.path.storage, instance.path.name
            storage.delete(name)

@receiver(models.signals.pre_save, sender=File)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `File` object is changed.
    """

    if not instance.pk:
        return False

    try:
        old_file = File.objects.get(pk=instance.pk).path
    except File.DoesNotExist:
        return False

    new_file = instance.path
    if not old_file == new_file:
        try:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
        except Exception:
            return False


class Form(models.Model):
    formid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    title = models.TextField(blank=True, null=True)
    subtitle = models.TextField(blank=True, null=True)
    iconclass = models.TextField(blank=True, null=True)
    visible = models.BooleanField(default=True)
    sortorder = models.IntegerField(blank=True, null=True, default=None)
    graph = models.ForeignKey('GraphModel', db_column='graphid', blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'forms'


class FormXCard(models.Model):
    id = models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid1)
    card = models.ForeignKey('CardModel', db_column='cardid')
    form = models.ForeignKey('Form', db_column='formid')
    sortorder = models.IntegerField(blank=True, null=True, default=None)

    class Meta:
        managed = True
        db_table = 'forms_x_cards'


class Function(models.Model):
    functionid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    name = models.TextField(blank=True, null=True)
    functiontype = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    defaultconfig = JSONField(blank=True, null=True)
    modulename = models.TextField(blank=True, null=True)
    classname = models.TextField(blank=True, null=True)
    component = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'functions'

    @property
    def defaultconfig_json(self):
        json_string = json.dumps(self.defaultconfig)
        return json_string

class FunctionXGraph(models.Model):
    id = models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid1)
    function = models.ForeignKey('Function', on_delete=models.CASCADE, db_column='functionid')
    graph = models.ForeignKey('GraphModel', on_delete=models.CASCADE, db_column='graphid')
    config = JSONField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'functions_x_graphs'
        unique_together = ('function', 'graph',)

class GraphModel(models.Model):
    graphid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    deploymentfile = models.TextField(blank=True, null=True)
    author = models.TextField(blank=True, null=True)
    deploymentdate = models.DateTimeField(blank=True, null=True)
    version = models.TextField(blank=True, null=True)
    isresource = models.BooleanField()
    isactive = models.BooleanField()
    iconclass = models.TextField(blank=True, null=True)
    mapfeaturecolor = models.TextField(blank=True, null=True)
    mappointsize = models.IntegerField(blank=True, null=True)
    maplinewidth = models.IntegerField(blank=True, null=True)
    subtitle = models.TextField(blank=True, null=True)
    ontology = models.ForeignKey('Ontology', db_column='ontologyid', related_name='graphs', null=True, blank=True)
    functions = models.ManyToManyField(to='Function', through='FunctionXGraph')

    @property
    def disable_instance_creation(self):
        if not self.isresource:
            return _('Only resource models may be edited - branches are not editable')
        msg = []
        forms = Form.objects.filter(graph_id=self.pk)
        if not self.isactive:
            msg.append(_('change resource model status in graph manager'))
        if forms.count() == 0:
            msg.append(_('add form(s)'))
        else:
            if FormXCard.objects.filter(form__in=forms).count() == 0:
                msg.append(_('add card(s) to form(s)'))
            if forms.filter(visible=True).count() == 0:
                msg.append(_('make form(s) visible'))
        if len(msg) == 0:
            return False
        return _('To make this resource editable: ') + ', '.join(msg)

    class Meta:
        managed = True
        db_table = 'graphs'


class Icon(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    cssclass = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'icons'


class NodeGroup(models.Model):
    nodegroupid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    legacygroupid = models.TextField(blank=True, null=True)
    cardinality = models.TextField(blank=True, default='1')
    parentnodegroup = models.ForeignKey('self', db_column='parentnodegroupid', blank=True, null=True)  #Allows nodegroups within nodegroups

    class Meta:
        managed = True
        db_table = 'node_groups'

        default_permissions = ()
        permissions = (
            ('read_nodegroup', 'Read'),
            ('write_nodegroup', 'Create/Update'),
            ('delete_nodegroup', 'Delete'),
            ('no_access_to_nodegroup', 'No Access'),
        )


class Node(models.Model):
    """
    Name is unique across all resources because it ties a node to values within tiles. Recommend prepending resource class to node name.

    """

    nodeid = models.UUIDField(primary_key=True, default=uuid.uuid1)
    name = models.TextField()
    description = models.TextField(blank=True, null=True)
    istopnode = models.BooleanField()
    ontologyclass = models.TextField(blank=True, null=True)
    datatype = models.TextField()
    nodegroup = models.ForeignKey(NodeGroup, db_column='nodegroupid', blank=True, null=True)
    graph = models.ForeignKey(GraphModel, db_column='graphid', blank=True, null=True)
    config = JSONField(blank=True, null=True, db_column='config')

    def get_child_nodes_and_edges(self):
        """
        gather up the child nodes and edges of this node

        returns a tuple of nodes and edges

        """
        nodes = []
        edges = []
        for edge in Edge.objects.filter(domainnode=self):
            nodes.append(edge.rangenode)
            edges.append(edge)

            child_nodes, child_edges = edge.rangenode.get_child_nodes_and_edges()
            nodes.extend(child_nodes)
            edges.extend(child_edges)
        return (nodes, edges)

    @property
    def is_collector(self):
        return str(self.nodeid) == str(self.nodegroup_id) and self.nodegroup is not None

    def get_relatable_resources(self):
        relatable_resource_ids = [r2r.resourceclassfrom for r2r in Resource2ResourceConstraint.objects.filter(resourceclassto_id=self.nodeid)]
        relatable_resource_ids = relatable_resource_ids + [r2r.resourceclassto for r2r in Resource2ResourceConstraint.objects.filter(resourceclassfrom_id=self.nodeid)]
        return relatable_resource_ids

    def set_relatable_resources(self, new_ids):
        old_ids = [res.nodeid for res in self.get_relatable_resources()]
        for old_id in old_ids:
            if old_id not in new_ids:
                Resource2ResourceConstraint.objects.filter(Q(resourceclassto_id=self.nodeid) | Q(resourceclassfrom_id=self.nodeid), Q(resourceclassto_id=old_id) | Q(resourceclassfrom_id=old_id)).delete()
        for new_id in new_ids:
            if new_id not in old_ids:
                new_r2r = Resource2ResourceConstraint.objects.create(resourceclassfrom_id=self.nodeid, resourceclassto_id=new_id)
                new_r2r.save()

    class Meta:
        managed = True
        db_table = 'nodes'


class Ontology(models.Model):
    ontologyid = models.UUIDField(default=uuid.uuid1, primary_key=True)
    name = models.TextField()
    version = models.TextField()
    path = models.FileField(storage=get_ontology_storage_system())
    parentontology = models.ForeignKey('Ontology', db_column='parentontologyid', related_name='extensions', null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'ontologies'


class OntologyClass(models.Model):
    """
    the target JSONField has this schema:

    values are dictionaries with 2 properties, 'down' and 'up' and within each of those another 2 properties,
    'ontology_property' and 'ontology_classes'

    "down" assumes a known domain class, while "up" assumes a known range class

    .. code-block:: python

        "down":[
            {
                "ontology_property": "P1_is_identified_by",
                "ontology_classes": [
                    "E51_Contact_Point",
                    "E75_Conceptual_Object_Appellation",
                    "E42_Identifier",
                    "E45_Address",
                    "E41_Appellation",
                    ....
                ]
            }
        ]
        "up":[
                "ontology_property": "P1i_identifies",
                "ontology_classes": [
                    "E51_Contact_Point",
                    "E75_Conceptual_Object_Appellation",
                    "E42_Identifier"
                    ....
                ]
            }
        ]

    """

    ontologyclassid = models.UUIDField(default=uuid.uuid1, primary_key=True)
    source = models.TextField()
    target = JSONField(null=True)
    ontology = models.ForeignKey('Ontology', db_column='ontologyid', related_name='ontologyclasses')

    class Meta:
        managed = True
        db_table = 'ontologyclasses'
        unique_together=(('source', 'ontology'),)


class Relation(models.Model):
    conceptfrom = models.ForeignKey(Concept, db_column='conceptidfrom', related_name='relation_concepts_from')
    conceptto = models.ForeignKey(Concept, db_column='conceptidto', related_name='relation_concepts_to')
    relationtype = models.ForeignKey(DRelationType, db_column='relationtype')
    relationid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.

    class Meta:
        managed = True
        db_table = 'relations'
        unique_together = (('conceptfrom', 'conceptto', 'relationtype'),)


class ReportTemplate(models.Model):
    templateid = models.UUIDField(primary_key=True, default=uuid.uuid1)
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    component = models.TextField()
    componentname = models.TextField()
    defaultconfig = JSONField(blank=True, null=True, db_column='defaultconfig')

    @property
    def defaultconfig_json(self):
        json_string = json.dumps(self.defaultconfig)
        return json_string

    class Meta:
        managed = True
        db_table = 'report_templates'


class Report(models.Model):
    reportid = models.UUIDField(primary_key=True, default=uuid.uuid1)
    name = models.TextField(blank=True, null=True)
    template = models.ForeignKey(ReportTemplate, db_column='templateid')
    graph = models.ForeignKey(GraphModel, db_column='graphid')
    config = JSONField(blank=True, null=True, db_column='config')
    formsconfig = JSONField(blank=True, null=True, db_column='formsconfig')
    active = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'reports'


class Resource2ResourceConstraint(models.Model):
    resource2resourceid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    resourceclassfrom = models.ForeignKey(Node, db_column='resourceclassfrom', blank=True, null=True, related_name='resxres_contstraint_classes_from')
    resourceclassto = models.ForeignKey(Node, db_column='resourceclassto', blank=True, null=True, related_name='resxres_contstraint_classes_to')

    class Meta:
        managed = True
        db_table = 'resource_2_resource_constraints'


class ResourceXResource(models.Model):
    resourcexid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    resourceinstanceidfrom = models.ForeignKey('ResourceInstance', db_column='resourceinstanceidfrom', blank=True, null=True, related_name='resxres_resource_instance_ids_from')
    resourceinstanceidto = models.ForeignKey('ResourceInstance', db_column='resourceinstanceidto', blank=True, null=True, related_name='resxres_resource_instance_ids_to')
    notes = models.TextField(blank=True, null=True)
    relationshiptype = models.ForeignKey('Value', db_column='relationshiptype')
    datestarted = models.DateField(blank=True, null=True)
    dateended = models.DateField(blank=True, null=True)

    def delete(self):
        se = SearchEngineFactory().create()
        se.delete(index='resource_relations', doc_type='all', id=self.resourcexid)
        super(ResourceXResource, self).delete()

    def save(self):
        se = SearchEngineFactory().create()
        document = model_to_dict(self)
        se.index_data(index='resource_relations', doc_type='all', body=document, idfield='resourcexid')
        super(ResourceXResource, self).save()

    class Meta:
        managed = True
        db_table = 'resource_x_resource'


class ResourceInstance(models.Model):
    resourceinstanceid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    graph = models.ForeignKey(GraphModel, db_column='graphid')
    legacyid = models.TextField(blank=True, unique=True, null=True)
    createdtime = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'resource_instances'


class TileModel(models.Model): #Tile
    """
    the data JSONField has this schema:

    values are dictionaries with n number of keys that represent nodeid's and values the value of that node instance

    .. code-block:: python

        {
            nodeid: node value,
            nodeid: node value,
            ...
        }

        {
            "20000000-0000-0000-0000-000000000002": "John",
            "20000000-0000-0000-0000-000000000003": "Smith",
            "20000000-0000-0000-0000-000000000004": "Primary"
        }

    """

    tileid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    resourceinstance = models.ForeignKey(ResourceInstance, db_column='resourceinstanceid')
    parenttile = models.ForeignKey('self', db_column='parenttileid', blank=True, null=True)
    data = JSONField(blank=True, null=True, db_column='tiledata')  # This field type is a guess.
    nodegroup = models.ForeignKey(NodeGroup, db_column='nodegroupid')
    sortorder = models.IntegerField(blank=True, null=True, default=0)

    class Meta:
        managed = True
        db_table = 'tiles'

    def save(self, *args, **kwargs):
        if(self.sortorder is None):
            sortorder_max = TileModel.objects.filter(nodegroup_id=self.nodegroup_id, resourceinstance_id=self.resourceinstance_id).aggregate(Max('sortorder'))['sortorder__max']
            self.sortorder = sortorder_max + 1 if sortorder_max is not None else 0
        super(TileModel, self).save(*args, **kwargs) # Call the "real" save() method.


class Value(models.Model):
    valueid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    concept = models.ForeignKey('Concept', db_column='conceptid')
    valuetype = models.ForeignKey(DValueType, db_column='valuetype')
    value = models.TextField()
    language = models.ForeignKey(DLanguage, db_column='languageid', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'values'

class FileValue(models.Model):
    valueid = models.UUIDField(primary_key=True, default=uuid.uuid1) # This field type is a guess.
    concept = models.ForeignKey('Concept', db_column='conceptid')
    valuetype = models.ForeignKey('DValueType', db_column='valuetype')
    value = models.FileField(upload_to='concepts')
    language = models.ForeignKey('DLanguage', db_column='languageid', blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'values'

    def geturl(self):
        if self.value != None:
            return self.value.url
        return ''

    def getname(self):
        if self.value != None:
            return self.value.name
        return ''

class Widget(models.Model):
    widgetid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    name = models.TextField()
    component = models.TextField()
    defaultconfig = JSONField(blank=True, null=True, db_column='defaultconfig')
    helptext = models.TextField(blank=True, null=True)
    datatype = models.TextField()

    @property
    def defaultconfig_json(self):
        json_string = json.dumps(self.defaultconfig)
        return json_string

    class Meta:
        managed = True
        db_table = 'widgets'


class MapSources(models.Model):
    name = models.TextField(unique=True)
    source = JSONField(blank=True, null=True, db_column='source')

    @property
    def source_json(self):
        json_string = json.dumps(self.source)
        return json_string

    class Meta:
        managed = True
        db_table = 'map_sources'


class MapLayers(models.Model):
    maplayerid = models.UUIDField(primary_key=True, default=uuid.uuid1)
    name = models.TextField(unique=True)
    layerdefinitions = JSONField(blank=True, null=True, db_column='layerdefinitions')
    isoverlay = models.BooleanField(default=False)
    activated = models.BooleanField(default=True)
    icon = models.TextField(default=None)
    addtomap = models.BooleanField(default=False)

    @property
    def layer_json(self):
        json_string = json.dumps(self.layerdefinitions)
        return json_string

    class Meta:
        managed = True
        db_table = 'map_layers'


class TileserverLayers(models.Model):
    name = models.TextField(unique=True)
    path = models.TextField()
    config = JSONField()
    map_layer = models.ForeignKey('MapLayers', db_column='map_layerid')
    map_source = models.ForeignKey('MapSources', db_column='map_sourceid')

    class Meta:
        managed = True
        db_table = 'tileserver_layers'

class GraphXMapping(models.Model):
    id = models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid1)
    graph = models.ForeignKey('GraphModel', db_column='graphid')
    mapping = JSONField(blank=True, null=False)

    class Meta:
        managed = True
        db_table = 'graphs_x_mapping_file'
