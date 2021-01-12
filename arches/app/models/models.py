# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.


import os
import json
import uuid
import datetime
import logging
from datetime import timedelta
from arches.app.utils.module_importer import get_class_from_modulename
from django.forms.models import model_to_dict
from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import get_template, render_to_string
from django.core.validators import RegexValidator
from django.db.models import Q, Max
from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.validators import validate_slug
from guardian.models import GroupObjectPermission
from guardian.shortcuts import assign_perm

# can't use "arches.app.models.system_settings.SystemSettings" because of circular refernce issue
# so make sure the only settings we use in this file are ones that are static (fixed at run time)
from django.conf import settings


class CardModel(models.Model):
    cardid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)
    cssclass = models.TextField(blank=True, null=True)
    helpenabled = models.BooleanField(default=False)
    helptitle = models.TextField(blank=True, null=True)
    helptext = models.TextField(blank=True, null=True)
    nodegroup = models.ForeignKey("NodeGroup", db_column="nodegroupid", on_delete=models.CASCADE)
    graph = models.ForeignKey("GraphModel", db_column="graphid", on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    visible = models.BooleanField(default=True)
    sortorder = models.IntegerField(blank=True, null=True, default=None)
    component = models.ForeignKey(
        "CardComponent", db_column="componentid", default=uuid.UUID("f05e4d3a-53c1-11e8-b0ea-784f435179ea"), on_delete=models.SET_DEFAULT
    )
    config = JSONField(blank=True, null=True, db_column="config")

    def is_editable(self):
        if settings.OVERRIDE_RESOURCE_MODEL_LOCK is True:
            return True
        else:
            return not TileModel.objects.filter(nodegroup=self.nodegroup).exists()

    class Meta:
        managed = True
        db_table = "cards"


class ConstraintModel(models.Model):
    constraintid = models.UUIDField(primary_key=True, default=uuid.uuid1)
    uniquetoallinstances = models.BooleanField(default=False)
    card = models.ForeignKey("CardModel", db_column="cardid", on_delete=models.CASCADE)
    nodes = models.ManyToManyField(to="Node", through="ConstraintXNode")

    class Meta:
        managed = True
        db_table = "card_constraints"


class ConstraintXNode(models.Model):
    id = models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid1)
    constraint = models.ForeignKey("ConstraintModel", on_delete=models.CASCADE, db_column="constraintid")
    node = models.ForeignKey("Node", on_delete=models.CASCADE, db_column="nodeid")

    class Meta:
        managed = True
        db_table = "constraints_x_nodes"


class CardComponent(models.Model):
    componentid = models.UUIDField(primary_key=True, default=uuid.uuid1)
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    component = models.TextField()
    componentname = models.TextField()
    defaultconfig = JSONField(blank=True, null=True, db_column="defaultconfig")

    @property
    def defaultconfig_json(self):
        json_string = json.dumps(self.defaultconfig)
        return json_string

    class Meta:
        managed = True
        db_table = "card_components"


class CardXNodeXWidget(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1)
    node = models.ForeignKey("Node", db_column="nodeid", on_delete=models.CASCADE)
    card = models.ForeignKey("CardModel", db_column="cardid", on_delete=models.CASCADE)
    widget = models.ForeignKey("Widget", db_column="widgetid", on_delete=models.CASCADE)
    config = JSONField(blank=True, null=True, db_column="config")
    label = models.TextField(blank=True, null=True)
    visible = models.BooleanField(default=True)
    sortorder = models.IntegerField(blank=True, null=True, default=None)

    class Meta:
        managed = True
        db_table = "cards_x_nodes_x_widgets"
        unique_together = (("node", "card", "widget"),)


class Concept(models.Model):
    conceptid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    nodetype = models.ForeignKey("DNodeType", db_column="nodetype", on_delete=models.CASCADE)
    legacyoid = models.TextField(unique=True)

    class Meta:
        managed = True
        db_table = "concepts"


class DDataType(models.Model):
    datatype = models.TextField(primary_key=True)
    iconclass = models.TextField()
    modulename = models.TextField(blank=True, null=True)
    classname = models.TextField(blank=True, null=True)
    defaultwidget = models.ForeignKey(db_column="defaultwidget", to="models.Widget", null=True, on_delete=models.SET_NULL)
    defaultconfig = JSONField(blank=True, null=True, db_column="defaultconfig")
    configcomponent = models.TextField(blank=True, null=True)
    configname = models.TextField(blank=True, null=True)
    issearchable = models.NullBooleanField(default=False)
    isgeometric = models.BooleanField()

    def __str__(self):
        return self.datatype

    class Meta:
        managed = True
        db_table = "d_data_types"


class DLanguage(models.Model):
    languageid = models.TextField(primary_key=True)
    languagename = models.TextField()
    isdefault = models.BooleanField()

    class Meta:
        managed = True
        db_table = "d_languages"

    def __str__(self):
        return f"{self.languageid} ({self.languagename})"

class DNodeType(models.Model):
    nodetype = models.TextField(primary_key=True)
    namespace = models.TextField()

    class Meta:
        managed = True
        db_table = "d_node_types"


class DRelationType(models.Model):
    relationtype = models.TextField(primary_key=True)
    category = models.TextField()
    namespace = models.TextField()

    class Meta:
        managed = True
        db_table = "d_relation_types"


class DValueType(models.Model):
    valuetype = models.TextField(primary_key=True)
    category = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    namespace = models.TextField()
    datatype = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "d_value_types"


class Edge(models.Model):
    edgeid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    ontologyproperty = models.TextField(blank=True, null=True)
    domainnode = models.ForeignKey("Node", db_column="domainnodeid", related_name="edge_domains", on_delete=models.CASCADE)
    rangenode = models.ForeignKey("Node", db_column="rangenodeid", related_name="edge_ranges", on_delete=models.CASCADE)
    graph = models.ForeignKey("GraphModel", db_column="graphid", blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = "edges"
        unique_together = (("rangenode", "domainnode"),)


class EditLog(models.Model):
    editlogid = models.UUIDField(primary_key=True, default=uuid.uuid1)
    resourcedisplayname = models.TextField(blank=True, null=True)
    resourceclassid = models.TextField(blank=True, null=True)
    resourceinstanceid = models.TextField(blank=True, null=True)
    nodegroupid = models.TextField(blank=True, null=True)
    tileinstanceid = models.TextField(blank=True, null=True)
    edittype = models.TextField(blank=True, null=True)
    newvalue = JSONField(blank=True, null=True, db_column="newvalue")
    oldvalue = JSONField(blank=True, null=True, db_column="oldvalue")
    newprovisionalvalue = JSONField(blank=True, null=True, db_column="newprovisionalvalue")
    oldprovisionalvalue = JSONField(blank=True, null=True, db_column="oldprovisionalvalue")
    timestamp = models.DateTimeField(blank=True, null=True)
    userid = models.TextField(blank=True, null=True)
    user_firstname = models.TextField(blank=True, null=True)
    user_lastname = models.TextField(blank=True, null=True)
    user_email = models.TextField(blank=True, null=True)
    user_username = models.TextField(blank=True, null=True)
    provisional_userid = models.TextField(blank=True, null=True)
    provisional_user_username = models.TextField(blank=True, null=True)
    provisional_edittype = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "edit_log"


class MobileSyncLog(models.Model):
    logid = models.UUIDField(primary_key=True, default=uuid.uuid1)
    survey = models.ForeignKey("MobileSurveyModel", on_delete=models.CASCADE, related_name="surveyid")
    userid = models.IntegerField(null=True)  # not a ForeignKey so we can track deletions
    started = models.DateTimeField(auto_now_add=True, null=True)
    finished = models.DateTimeField(auto_now=True, null=True)
    message = models.TextField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "mobile_sync_log"


class ResourceRevisionLog(models.Model):
    logid = models.UUIDField(primary_key=True, default=uuid.uuid1)
    resourceid = models.UUIDField(default=uuid.uuid1)
    revisionid = models.TextField(null=False)  # not a ForeignKey so we can track deletions
    survey = models.ForeignKey("MobileSurveyModel", on_delete=models.CASCADE, related_name="mobile_survey_id")
    synclog = models.ForeignKey("MobileSyncLog", on_delete=models.CASCADE, related_name="sync_log")
    synctimestamp = models.DateTimeField(auto_now_add=True, null=False)
    action = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "resource_revision_log"


class TileRevisionLog(models.Model):
    logid = models.UUIDField(primary_key=True, default=uuid.uuid1)
    tileid = models.UUIDField(default=uuid.uuid1)  # not a ForeignKey so we can track deletions
    resourceid = models.UUIDField(default=uuid.uuid1)
    revisionid = models.TextField(null=False)  # not a ForeignKey so we can track deletions
    survey = models.ForeignKey("MobileSurveyModel", on_delete=models.CASCADE, related_name="survey_id")
    synclog = models.ForeignKey("MobileSyncLog", on_delete=models.CASCADE, related_name="mobile_sync_log")
    synctimestamp = models.DateTimeField(auto_now_add=True, null=False)
    action = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "tile_revision_log"


class File(models.Model):
    fileid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    path = models.FileField(upload_to="uploadedfiles")
    tile = models.ForeignKey("TileModel", db_column="tileid", null=True, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = "files"


# These two event listeners auto-delete files from filesystem when they are unneeded:
# from http://stackoverflow.com/questions/16041232/django-delete-filefield
@receiver(post_delete, sender=File)
def delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `File` object is deleted.
    """

    if instance.path:
        try:
            if os.path.isfile(instance.path.path):
                os.remove(instance.path.path)
        # except block added to deal with S3 file deletion
        # see comments on 2nd answer below
        # http://stackoverflow.com/questions/5372934/how-do-i-get-django-admin-to-delete-files-when-i-remove-an-object-from-the-datab
        except Exception as e:
            storage, name = instance.path.storage, instance.path.name
            storage.delete(name)


@receiver(pre_save, sender=File)
def delete_file_on_change(sender, instance, **kwargs):
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
        db_table = "functions"

    @property
    def defaultconfig_json(self):
        json_string = json.dumps(self.defaultconfig)
        return json_string

    def get_class_module(self):
        return get_class_from_modulename(self.modulename, self.classname, settings.FUNCTION_LOCATIONS)


class FunctionXGraph(models.Model):
    id = models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid1)
    function = models.ForeignKey("Function", on_delete=models.CASCADE, db_column="functionid")
    graph = models.ForeignKey("GraphModel", on_delete=models.CASCADE, db_column="graphid")
    config = JSONField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "functions_x_graphs"
        unique_together = ("function", "graph")


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
    color = models.TextField(blank=True, null=True)
    subtitle = models.TextField(blank=True, null=True)
    ontology = models.ForeignKey(
        "Ontology", db_column="ontologyid", related_name="graphs", null=True, blank=True, on_delete=models.SET_NULL
    )
    functions = models.ManyToManyField(to="Function", through="FunctionXGraph")
    jsonldcontext = models.TextField(blank=True, null=True)
    template = models.ForeignKey(
        "ReportTemplate", db_column="templateid", default="50000000-0000-0000-0000-000000000001", on_delete=models.SET_DEFAULT
    )
    config = JSONField(db_column="config", default=dict)
    slug = models.TextField(validators=[validate_slug], unique=True, null=True)

    @property
    def disable_instance_creation(self):
        if not self.isresource:
            return _("Only resource models may be edited - branches are not editable")
        if not self.isactive:
            return _("This Model is Inactive and not available for editing")
        return False

    def is_editable(self):
        if settings.OVERRIDE_RESOURCE_MODEL_LOCK == True:
            return True
        elif self.isresource:
            return not ResourceInstance.objects.filter(graph_id=self.graphid).exists()
        else:
            return True

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = "graphs"


class Icon(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    cssclass = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "icons"


class NodeGroup(models.Model):
    nodegroupid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    legacygroupid = models.TextField(blank=True, null=True)
    cardinality = models.TextField(blank=True, default="1")
    parentnodegroup = models.ForeignKey(
        "self", db_column="parentnodegroupid", blank=True, null=True, on_delete=models.CASCADE
    )  # Allows nodegroups within nodegroups

    class Meta:
        managed = True
        db_table = "node_groups"

        default_permissions = ()
        permissions = (
            ("read_nodegroup", "Read"),
            ("write_nodegroup", "Create/Update"),
            ("delete_nodegroup", "Delete"),
            ("no_access_to_nodegroup", "No Access"),
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
    nodegroup = models.ForeignKey(NodeGroup, db_column="nodegroupid", blank=True, null=True, on_delete=models.CASCADE)
    graph = models.ForeignKey(GraphModel, db_column="graphid", blank=True, null=True, on_delete=models.CASCADE)
    config = JSONField(blank=True, null=True, db_column="config")
    issearchable = models.BooleanField(default=True)
    isrequired = models.BooleanField(default=False)
    sortorder = models.IntegerField(blank=True, null=True, default=0)
    fieldname = models.TextField(blank=True, null=True)
    exportable = models.BooleanField(default=False, null=True)

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

    def get_direct_child_nodes(self):
        """
        gets all child nodes exactly one level lower in graph

        returns a list of nodes
        """
        return [edge.rangenode for edge in Edge.objects.filter(domainnode=self)]

    @property
    def is_collector(self):
        return str(self.nodeid) == str(self.nodegroup_id) and self.nodegroup is not None

    def is_editable(self):
        if settings.OVERRIDE_RESOURCE_MODEL_LOCK is True:
            return True
        else:
            return not TileModel.objects.filter(nodegroup=self.nodegroup).exists()

    def get_relatable_resources(self):
        relatable_resource_ids = [
            r2r.resourceclassfrom
            for r2r in Resource2ResourceConstraint.objects.filter(resourceclassto_id=self.nodeid)
            if r2r.resourceclassfrom is not None
        ]
        relatable_resource_ids = relatable_resource_ids + [
            r2r.resourceclassto
            for r2r in Resource2ResourceConstraint.objects.filter(resourceclassfrom_id=self.nodeid)
            if r2r.resourceclassto is not None
        ]
        return relatable_resource_ids

    def set_relatable_resources(self, new_ids):
        old_ids = [res.nodeid for res in self.get_relatable_resources()]
        for old_id in old_ids:
            if old_id not in new_ids:
                Resource2ResourceConstraint.objects.filter(
                    Q(resourceclassto_id=self.nodeid) | Q(resourceclassfrom_id=self.nodeid),
                    Q(resourceclassto_id=old_id) | Q(resourceclassfrom_id=old_id),
                ).delete()
        for new_id in new_ids:
            if new_id not in old_ids:
                new_r2r = Resource2ResourceConstraint.objects.create(resourceclassfrom_id=self.nodeid, resourceclassto_id=new_id)
                new_r2r.save()

    class Meta:
        managed = True
        db_table = "nodes"
        constraints = [
            models.UniqueConstraint(fields=["name", "nodegroupid"], name="unique_nodename_nodegroup"),
        ]


class Ontology(models.Model):
    ontologyid = models.UUIDField(default=uuid.uuid1, primary_key=True)
    name = models.TextField()
    version = models.TextField()
    path = models.TextField(null=True, blank=True)
    namespaces = JSONField(null=True, blank=True)
    parentontology = models.ForeignKey(
        "Ontology", db_column="parentontologyid", related_name="extensions", null=True, blank=True, on_delete=models.CASCADE
    )

    class Meta:
        managed = True
        db_table = "ontologies"


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
    ontology = models.ForeignKey("Ontology", db_column="ontologyid", related_name="ontologyclasses", on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = "ontologyclasses"
        unique_together = (("source", "ontology"),)


class Relation(models.Model):
    conceptfrom = models.ForeignKey(Concept, db_column="conceptidfrom", related_name="relation_concepts_from", on_delete=models.CASCADE)
    conceptto = models.ForeignKey(Concept, db_column="conceptidto", related_name="relation_concepts_to", on_delete=models.CASCADE)
    relationtype = models.ForeignKey(DRelationType, db_column="relationtype", on_delete=models.CASCADE)
    relationid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.

    class Meta:
        managed = True
        db_table = "relations"
        unique_together = (("conceptfrom", "conceptto", "relationtype"),)


class ReportTemplate(models.Model):
    templateid = models.UUIDField(primary_key=True, default=uuid.uuid1)
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    component = models.TextField()
    componentname = models.TextField()
    defaultconfig = JSONField(blank=True, null=True, db_column="defaultconfig")

    @property
    def defaultconfig_json(self):
        json_string = json.dumps(self.defaultconfig)
        return json_string

    class Meta:
        managed = True
        db_table = "report_templates"


class Resource2ResourceConstraint(models.Model):
    resource2resourceid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    resourceclassfrom = models.ForeignKey(
        Node,
        db_column="resourceclassfrom",
        blank=True,
        null=True,
        related_name="resxres_contstraint_classes_from",
        on_delete=models.SET_NULL,
    )
    resourceclassto = models.ForeignKey(
        Node, db_column="resourceclassto", blank=True, null=True, related_name="resxres_contstraint_classes_to", on_delete=models.SET_NULL
    )

    class Meta:
        managed = True
        db_table = "resource_2_resource_constraints"


class ResourceXResource(models.Model):
    resourcexid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    resourceinstanceidfrom = models.ForeignKey(
        "ResourceInstance",
        db_column="resourceinstanceidfrom",
        blank=True,
        null=True,
        related_name="resxres_resource_instance_ids_from",
        on_delete=models.CASCADE,
        db_constraint=False,
    )
    resourceinstancefrom_graphid = models.ForeignKey(
        "GraphModel",
        db_column="resourceinstancefrom_graphid",
        blank=True,
        null=True,
        related_name="resxres_resource_instance_fom_graph_id",
        on_delete=models.CASCADE,
        db_constraint=False,
    )
    resourceinstanceidto = models.ForeignKey(
        "ResourceInstance",
        db_column="resourceinstanceidto",
        blank=True,
        null=True,
        related_name="resxres_resource_instance_ids_to",
        on_delete=models.CASCADE,
        db_constraint=False,
    )
    resourceinstanceto_graphid = models.ForeignKey(
        "GraphModel",
        db_column="resourceinstanceto_graphid",
        blank=True,
        null=True,
        related_name="resxres_resource_instance_to_graph_id",
        on_delete=models.CASCADE,
        db_constraint=False,
    )

    notes = models.TextField(blank=True, null=True)
    relationshiptype = models.TextField(blank=True, null=True)
    inverserelationshiptype = models.TextField(blank=True, null=True)
    tileid = models.ForeignKey(
        "TileModel",
        db_column="tileid",
        blank=True,
        null=True,
        related_name="resxres_tile_id",
        on_delete=models.CASCADE,
    )
    nodeid = models.ForeignKey(
        "Node",
        db_column="nodeid",
        blank=True,
        null=True,
        related_name="resxres_node_id",
        on_delete=models.CASCADE,
    )
    datestarted = models.DateField(blank=True, null=True)
    dateended = models.DateField(blank=True, null=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()

    def delete(self, index=True, *args, **kwargs):
        if index:
            from arches.app.search.search_engine_factory import SearchEngineInstance as se
            from arches.app.search.mappings import RESOURCE_RELATIONS_INDEX
            se.delete(index=RESOURCE_RELATIONS_INDEX, id=self.resourcexid)

        # update the resource-instance tile by removing any references to a deleted resource
        deletedResourceId = kwargs.pop("deletedResourceId", None)
        if deletedResourceId and self.tileid and self.nodeid:
            newTileData = []
            data = self.tileid.data[str(self.nodeid_id)]
            if type(data) != list:
                data = [data]
            for relatedresourceItem in data:
                if relatedresourceItem["resourceId"] != str(deletedResourceId):
                    newTileData.append(relatedresourceItem)
            self.tileid.data[str(self.nodeid_id)] = newTileData
            self.tileid.save()

        super(ResourceXResource, self).delete()

    def save(self):
        from arches.app.search.search_engine_factory import SearchEngineInstance as se
        from arches.app.search.mappings import RESOURCE_RELATIONS_INDEX

        # during package/csv load the ResourceInstance models are not always available
        try:
            self.resourceinstancefrom_graphid = self.resourceinstanceidfrom.graph
        except:
            pass

        try:
            self.resourceinstanceto_graphid = self.resourceinstanceidto.graph
        except:
            pass

        if not self.created:
            self.created = datetime.datetime.now()

        self.modified = datetime.datetime.now()

        document = model_to_dict(self)

        se.index_data(index=RESOURCE_RELATIONS_INDEX, body=document, idfield="resourcexid")
        super(ResourceXResource, self).save()

    class Meta:
        managed = True
        db_table = "resource_x_resource"


class ResourceInstance(models.Model):
    resourceinstanceid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    graph = models.ForeignKey(GraphModel, db_column="graphid", on_delete=models.CASCADE)
    legacyid = models.TextField(blank=True, unique=True, null=True)
    createdtime = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "resource_instances"
        permissions = (("no_access_to_resourceinstance", "No Access"),)


class SearchComponent(models.Model):
    searchcomponentid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    name = models.TextField()
    icon = models.TextField(default=None)
    modulename = models.TextField(blank=True, null=True)
    classname = models.TextField(blank=True, null=True)
    type = models.TextField()
    componentpath = models.TextField(unique=True)
    componentname = models.TextField(unique=True)
    sortorder = models.IntegerField(blank=True, null=True, default=None)
    enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = "search_component"

    def get_class_module(self):
        return get_class_from_modulename(self.modulename, self.classname, settings.SEARCH_COMPONENT_LOCATIONS)

    def toJSON(self):
        from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

        return JSONSerializer().serialize(self)


class SearchExportHistory(models.Model):
    searchexportid = models.UUIDField(primary_key=True, default=uuid.uuid1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exporttime = models.DateTimeField(auto_now_add=True)
    numberofinstances = models.IntegerField()
    url = models.TextField()
    downloadfile = models.FileField(upload_to="export_deliverables", blank=True, null=True)

    class Meta:
        managed = True
        db_table = "search_export_history"


class TileModel(models.Model):  # Tile
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

    the provisionaledits JSONField has this schema:

    values are dictionaries with n number of keys that represent nodeid's and values the value of that node instance

    .. code-block:: python

        {
            userid: {
                value: node value,
                status: "review", "approved", or "rejected"
                action: "create", "update", or "delete"
                reviewer: reviewer's user id,
                timestamp: time of last provisional change,
                reviewtimestamp: time of review
                }
            ...
        }

        {
            1: {
                "value": {
                        "20000000-0000-0000-0000-000000000002": "Jack",
                        "20000000-0000-0000-0000-000000000003": "Smith",
                        "20000000-0000-0000-0000-000000000004": "Primary"
                      },
                "status": "rejected",
                "action": "update",
                "reviewer": 8,
                "timestamp": "20180101T1500",
                "reviewtimestamp": "20180102T0800",
                },
            15: {
                "value": {
                        "20000000-0000-0000-0000-000000000002": "John",
                        "20000000-0000-0000-0000-000000000003": "Smith",
                        "20000000-0000-0000-0000-000000000004": "Secondary"
                      },
                "status": "review",
                "action": "update",
        }

    """

    tileid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    resourceinstance = models.ForeignKey(ResourceInstance, db_column="resourceinstanceid", on_delete=models.CASCADE)
    parenttile = models.ForeignKey("self", db_column="parenttileid", blank=True, null=True, on_delete=models.CASCADE)
    data = JSONField(blank=True, null=True, db_column="tiledata")  # This field type is a guess.
    nodegroup = models.ForeignKey(NodeGroup, db_column="nodegroupid", on_delete=models.CASCADE)
    sortorder = models.IntegerField(blank=True, null=True, default=0)
    provisionaledits = JSONField(blank=True, null=True, db_column="provisionaledits")  # This field type is a guess.

    class Meta:
        managed = True
        db_table = "tiles"

    def save(self, *args, **kwargs):
        if self.sortorder is None or (self.provisionaledits is not None and self.data == {}):
            sortorder_max = TileModel.objects.filter(
                nodegroup_id=self.nodegroup_id, resourceinstance_id=self.resourceinstance_id
            ).aggregate(Max("sortorder"))["sortorder__max"]
            self.sortorder = sortorder_max + 1 if sortorder_max is not None else 0
        super(TileModel, self).save(*args, **kwargs)  # Call the "real" save() method.


class Value(models.Model):
    valueid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    concept = models.ForeignKey("Concept", db_column="conceptid", on_delete=models.CASCADE)
    valuetype = models.ForeignKey(DValueType, db_column="valuetype", on_delete=models.CASCADE)
    value = models.TextField()
    language = models.ForeignKey(DLanguage, db_column="languageid", blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = "values"


class FileValue(models.Model):
    valueid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    concept = models.ForeignKey("Concept", db_column="conceptid", on_delete=models.CASCADE)
    valuetype = models.ForeignKey("DValueType", db_column="valuetype", on_delete=models.CASCADE)
    value = models.FileField(upload_to="concepts")
    language = models.ForeignKey("DLanguage", db_column="languageid", blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = "values"

    def geturl(self):
        if self.value is not None:
            return self.value.url
        return ""

    def getname(self):
        if self.value is not None:
            return self.value.name
        return ""


# These two event listeners auto-delete files from filesystem when they are unneeded:
# from http://stackoverflow.com/questions/16041232/django-delete-filefield
@receiver(post_delete, sender=FileValue)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `FileValue` object is deleted.
    """
    if instance.value.path:
        try:
            if os.path.isfile(instance.value.path):
                os.remove(instance.value.path)
        # except block added to deal with S3 file deletion
        # see comments on 2nd answer below
        # http://stackoverflow.com/questions/5372934/how-do-i-get-django-admin-to-delete-files-when-i-remove-an-object-from-the-datab
        except Exception as e:
            storage, name = instance.value.storage, instance.value.name
            storage.delete(name)


@receiver(pre_save, sender=FileValue)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `FileValue` object is changed.
    """
    if not instance.pk:
        return False

    try:
        old_file = FileValue.objects.get(pk=instance.pk).value
    except FileValue.DoesNotExist:
        return False

    new_file = instance.value
    if not old_file == new_file:
        try:
            if os.path.isfile(old_file.value):
                os.remove(old_file.value)
        except Exception:
            return False


class Widget(models.Model):
    widgetid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    name = models.TextField(unique=True)
    component = models.TextField(unique=True)
    defaultconfig = JSONField(blank=True, null=True, db_column="defaultconfig")
    helptext = models.TextField(blank=True, null=True)
    datatype = models.TextField()

    @property
    def defaultconfig_json(self):
        json_string = json.dumps(self.defaultconfig)
        return json_string

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = "widgets"


class Geocoder(models.Model):
    geocoderid = models.UUIDField(primary_key=True, default=uuid.uuid1)
    name = models.TextField(unique=True)
    component = models.TextField(unique=True)
    api_key = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = "geocoders"


class MapSource(models.Model):
    name = models.TextField(unique=True)
    source = JSONField(blank=True, null=True, db_column="source")

    def __str__(self):
        return self.name

    @property
    def source_json(self):
        json_string = json.dumps(self.source)
        return json_string

    class Meta:
        managed = True
        db_table = "map_sources"


class MapLayer(models.Model):
    maplayerid = models.UUIDField(primary_key=True, default=uuid.uuid1)
    name = models.TextField(unique=True)
    layerdefinitions = JSONField(blank=True, null=True, db_column="layerdefinitions")
    isoverlay = models.BooleanField(default=False)
    activated = models.BooleanField(default=True)
    icon = models.TextField(default=None)
    addtomap = models.BooleanField(default=False)
    centerx = models.FloatField(blank=True, null=True)
    centery = models.FloatField(blank=True, null=True)
    zoom = models.FloatField(blank=True, null=True)
    legend = models.TextField(blank=True, null=True)
    searchonly = models.BooleanField(default=False)

    @property
    def layer_json(self):
        json_string = json.dumps(self.layerdefinitions)
        return json_string

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = "map_layers"


class GraphXMapping(models.Model):
    id = models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid1)
    graph = models.ForeignKey("GraphModel", db_column="graphid", on_delete=models.CASCADE)
    mapping = JSONField(blank=True, null=False)

    class Meta:
        managed = True
        db_table = "graphs_x_mapping_file"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=16, blank=True)

    def is_reviewer(self):
        """ DEPRECATED Use new pattern:

            from arches.app.utils.permission_backend import user_is_resource_reviewer
            is_reviewer = user_is_resource_reviewer(user)
        """
        pass

    @property
    def viewable_nodegroups(self):
        from arches.app.utils.permission_backend import get_nodegroups_by_perm

        return set(str(nodegroup.pk) for nodegroup in get_nodegroups_by_perm(self.user, ["models.read_nodegroup"], any_perm=True))

    @property
    def editable_nodegroups(self):
        from arches.app.utils.permission_backend import get_nodegroups_by_perm

        return set(str(nodegroup.pk) for nodegroup in get_nodegroups_by_perm(self.user, ["models.write_nodegroup"], any_perm=True))

    @property
    def deletable_nodegroups(self):
        from arches.app.utils.permission_backend import get_nodegroups_by_perm

        return set(str(nodegroup.pk) for nodegroup in get_nodegroups_by_perm(self.user, ["models.delete_nodegroup"], any_perm=True))

    class Meta:
        managed = True
        db_table = "user_profile"


@receiver(post_save, sender=User)
def create_permissions_for_new_users(sender, instance, created, **kwargs):
    from arches.app.models.resource import Resource

    if created:
        ct = ContentType.objects.get(app_label="models", model="resourceinstance")
        resourceInstanceIds = list(GroupObjectPermission.objects.filter(content_type=ct).values_list("object_pk", flat=True).distinct())
        for resourceInstanceId in resourceInstanceIds:
            resourceInstanceId = uuid.UUID(resourceInstanceId)
        resources = ResourceInstance.objects.filter(pk__in=resourceInstanceIds)
        assign_perm("no_access_to_resourceinstance", instance, resources)
        for resource in resources:
            Resource(resource.resourceinstanceid).index()


class UserXTask(models.Model):
    id = models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid1)
    taskid = models.UUIDField(serialize=False, blank=True, null=True)
    status = models.TextField(null=True, default="PENDING")
    datestart = models.DateTimeField(blank=True, null=True)
    datedone = models.DateTimeField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = "user_x_tasks"


class NotificationType(models.Model):
    """
    Creates a 'type' of notification that would be associated with a specific trigger, e.g. Search Export Complete or Package Load Complete
    Must be created manually using Django ORM or SQL.
    """

    typeid = models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid1)
    name = models.TextField(blank=True, null=True)
    emailtemplate = models.TextField(blank=True, null=True)
    emailnotify = models.BooleanField(default=False)
    webnotify = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = "notification_types"


class Notification(models.Model):
    """
    A Notification instance that may optionally have a NotificationType. Can spawn N UserXNotification instances
    Must be created manually using Django ORM.
    """

    id = models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid1)
    created = models.DateTimeField(auto_now_add=True)
    # created.editable = True
    message = models.TextField(blank=True, null=True)
    context = JSONField(blank=True, null=True, default=dict)
    # TODO: Ideally validate context against a list of keys from NotificationType
    notiftype = models.ForeignKey(NotificationType, on_delete=models.CASCADE, null=True)

    class Meta:
        managed = True
        db_table = "notifications"


class UserXNotification(models.Model):
    """
    A UserXNotification instance depends on an existing Notification instance and a User.
    If its Notification instance has a NotificationType, this Type can be overriden for this particular User with a UserXNotificationType.
    Must be created manually using Django ORM.
    Only one UserXNotification created per medium of notification (e.g. emailnotify, webnotify).
    Property 'isread' refers to either webnotify or emailnotify, not both, behaves differently.
    """

    id = models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid1)
    notif = models.ForeignKey(Notification, on_delete=models.CASCADE)
    isread = models.BooleanField(default=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = "user_x_notifications"


class UserXNotificationType(models.Model):
    """
    A UserXNotificationType instance only exists as an override of an existing NotificationType and is user-specific and
    notification-settings-specific (e.g. emailnotify, webnotify, etc.)
    Can be created in UI: see arches user profile editor to create a UserXNotificationType instance against an existing NotificationTypes
    Else to create manually check 'notification_types' table in db for reference.
    UserXNotificationTypes are automatically queried and applied as filters in get() requests for UserXNotifications in views/notifications
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notiftype = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    emailnotify = models.BooleanField(default=False)
    webnotify = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = "user_x_notification_types"


@receiver(post_save, sender=UserXNotification)
def send_email_on_save(sender, instance, **kwargs):
    """Checks if a notification type needs to send an email, does so if email server exists
    """

    if instance.notif.notiftype is not None and instance.isread is False:
        if UserXNotificationType.objects.filter(user=instance.recipient, notiftype=instance.notif.notiftype, emailnotify=False).exists():
            return False

        try:
            context = instance.notif.context.copy()
            text_content = render_to_string(instance.notif.notiftype.emailtemplate, context)
            html_template = get_template(instance.notif.notiftype.emailtemplate)
            html_content = html_template.render(context)
            if context["email"] == instance.recipient.email:
                email_to = instance.recipient.email
            else:
                email_to = context["email"]
            subject, from_email, to = instance.notif.notiftype.name, settings.DEFAULT_FROM_EMAIL, email_to
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            if instance.notif.notiftype.webnotify is not True:
                instance.isread = True
                instance.save()
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warn("Email Server not correctly set up. See settings to configure.")

    return False


def getDataDownloadConfigDefaults():
    return dict(download=False, count=100, resources=[], custom=None)


class MobileSurveyModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid1)
    name = models.TextField(null=True)
    active = models.BooleanField(default=False)
    createdby = models.ForeignKey(User, related_name="createdby", on_delete=models.CASCADE)
    lasteditedby = models.ForeignKey(User, related_name="lasteditedby", on_delete=models.CASCADE)
    users = models.ManyToManyField(to=User, through="MobileSurveyXUser")
    groups = models.ManyToManyField(to=Group, through="MobileSurveyXGroup")
    cards = models.ManyToManyField(to=CardModel, through="MobileSurveyXCard")
    startdate = models.DateField(blank=True, null=True)
    enddate = models.DateField(blank=True, null=True)
    description = models.TextField(null=True)
    bounds = models.MultiPolygonField(null=True)
    tilecache = models.TextField(null=True)
    onlinebasemaps = JSONField(blank=True, null=True, db_column="onlinebasemaps")
    datadownloadconfig = JSONField(blank=True, null=True, default=getDataDownloadConfigDefaults)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = "mobile_surveys"

    @property
    def expired(self):
        result = False
        if self.enddate is not None:
            enddate = datetime.datetime.strftime(self.enddate, "%Y-%m-%d")
            result = (datetime.datetime.strptime(enddate, "%Y-%m-%d") - datetime.datetime.now() + timedelta(hours=24)).days < 0
        return result

    def deactivate_expired_survey(self):
        if self.expired:
            self.active = False
            self.save()


class MobileSurveyXUser(models.Model):
    mobile_survey_x_user_id = models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mobile_survey = models.ForeignKey(MobileSurveyModel, on_delete=models.CASCADE, null=True)

    class Meta:
        managed = True
        db_table = "mobile_surveys_x_users"
        unique_together = ("mobile_survey", "user")


class MobileSurveyXGroup(models.Model):
    mobile_survey_x_group_id = models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid1)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    mobile_survey = models.ForeignKey(MobileSurveyModel, on_delete=models.CASCADE, null=True)

    class Meta:
        managed = True
        db_table = "mobile_surveys_x_groups"
        unique_together = ("mobile_survey", "group")


class MobileSurveyXCard(models.Model):
    mobile_survey_x_card_id = models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid1)
    card = models.ForeignKey(CardModel, on_delete=models.CASCADE)
    mobile_survey = models.ForeignKey(MobileSurveyModel, on_delete=models.CASCADE, null=True)
    sortorder = models.IntegerField(default=0)

    class Meta:
        managed = True
        db_table = "mobile_surveys_x_cards"
        unique_together = ("mobile_survey", "card")


class MapMarker(models.Model):
    name = models.TextField(unique=True)
    url = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = "map_markers"


class Plugin(models.Model):
    pluginid = models.UUIDField(primary_key=True, default=uuid.uuid1)  # This field type is a guess.
    name = models.TextField()
    icon = models.TextField(default=None)
    component = models.TextField()
    componentname = models.TextField()
    config = JSONField(blank=True, null=True, db_column="config")
    slug = models.TextField(validators=[validate_slug], unique=True, null=True)
    sortorder = models.IntegerField(blank=True, null=True, default=None)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = "plugins"


class IIIFManifest(models.Model):
    label = models.TextField()
    url = models.TextField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.label

    class Meta:
        managed = True
        db_table = "iiif_manifests"


class GroupMapSettings(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    min_zoom = models.IntegerField(default=0)
    max_zoom = models.IntegerField(default=20)
    default_zoom = models.IntegerField(default=0)

    def __str__(self):
        return self.group.name

    class Meta:
        managed = True
        db_table = "group_map_settings"
