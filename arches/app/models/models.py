# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.


import sys
import json
import uuid
import datetime
import logging
import traceback
import django.utils.timezone

from arches.app.const import ExtensionType
from arches.app.utils.module_importer import get_class_from_modulename
from arches.app.utils.thumbnail_factory import ThumbnailGeneratorInstance
from arches.app.models.fields.i18n import I18n_TextField, I18n_JSONField
from arches.app.models.utils import add_to_update_fields
from arches.app.utils.betterJSONSerializer import JSONSerializer
from arches.app.utils import import_class_from_string
from django.contrib.auth.models import Group, User
from django.contrib.gis.db import models
from django.core import checks
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.db.models import JSONField
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import RegexValidator, validate_slug
from django.db.models import JSONField, Max, Q
from django.db.models.constraints import UniqueConstraint
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.core.validators import validate_slug
from django.core.exceptions import ValidationError

# can't use "arches.app.models.system_settings.SystemSettings" because of circular refernce issue
# so make sure the only settings we use in this file are ones that are static (fixed at run time)
from django.conf import settings


logger = logging.getLogger(__name__)


class BulkIndexQueue(models.Model):
    resourceinstanceid = models.UUIDField(primary_key=True, unique=True)
    createddate = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        managed = True
        db_table = "bulk_index_queue"


class CardModel(models.Model):
    cardid = models.UUIDField(primary_key=True)
    name = I18n_TextField(blank=True, null=True)
    description = I18n_TextField(blank=True, null=True)
    instructions = I18n_TextField(blank=True, null=True)
    cssclass = models.TextField(blank=True, null=True)
    helpenabled = models.BooleanField(default=False)
    helptitle = I18n_TextField(blank=True, null=True)
    helptext = I18n_TextField(blank=True, null=True)
    nodegroup = models.ForeignKey(
        "NodeGroup", db_column="nodegroupid", on_delete=models.CASCADE
    )
    graph = models.ForeignKey(
        "GraphModel", db_column="graphid", on_delete=models.CASCADE
    )
    active = models.BooleanField(default=True)
    visible = models.BooleanField(default=True)
    sortorder = models.IntegerField(blank=True, null=True, default=None)
    component = models.ForeignKey(
        "CardComponent",
        db_column="componentid",
        default=uuid.UUID("f05e4d3a-53c1-11e8-b0ea-784f435179ea"),
        on_delete=models.SET_DEFAULT,
    )
    config = JSONField(blank=True, null=True, db_column="config")
    source_identifier = models.ForeignKey(
        "self",
        db_column="source_identifier",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    def __init__(self, *args, **kwargs):
        super(CardModel, self).__init__(*args, **kwargs)
        if not self.cardid:
            self.cardid = uuid.uuid4()
        if isinstance(self.cardid, str):
            self.cardid = uuid.UUID(self.cardid)

    def save(self, *args, **kwargs):
        if self.pk == self.source_identifier_id:
            self.source_identifier_id = None
            add_to_update_fields(kwargs, "source_identifier_id")
        super(CardModel, self).save()

    class Meta:
        managed = True
        db_table = "cards"


class ConstraintModel(models.Model):
    constraintid = models.UUIDField(primary_key=True)
    uniquetoallinstances = models.BooleanField(default=False)
    card = models.ForeignKey("CardModel", db_column="cardid", on_delete=models.CASCADE)
    nodes = models.ManyToManyField(to="Node", through="ConstraintXNode")

    def __init__(self, *args, **kwargs):
        super(ConstraintModel, self).__init__(*args, **kwargs)
        if not self.constraintid:
            self.constraintid = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "card_constraints"


class ConstraintXNode(models.Model):
    id = models.UUIDField(primary_key=True, serialize=False)
    constraint = models.ForeignKey(
        "ConstraintModel", on_delete=models.CASCADE, db_column="constraintid"
    )
    node = models.ForeignKey("Node", on_delete=models.CASCADE, db_column="nodeid")

    def __init__(self, *args, **kwargs):
        super(ConstraintXNode, self).__init__(*args, **kwargs)
        if not self.id:
            self.id = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "constraints_x_nodes"


class CardComponent(models.Model):
    componentid = models.UUIDField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    component = models.TextField()
    componentname = models.TextField()
    defaultconfig = JSONField(blank=True, null=True, db_column="defaultconfig")

    @property
    def defaultconfig_json(self):
        json_string = json.dumps(self.defaultconfig)
        return json_string

    def __init__(self, *args, **kwargs):
        super(CardComponent, self).__init__(*args, **kwargs)
        if not self.componentid:
            self.componentid = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "card_components"


class CardXNodeXWidget(models.Model):
    id = models.UUIDField(primary_key=True)
    node = models.ForeignKey("Node", db_column="nodeid", on_delete=models.CASCADE)
    card = models.ForeignKey("CardModel", db_column="cardid", on_delete=models.CASCADE)
    widget = models.ForeignKey("Widget", db_column="widgetid", on_delete=models.CASCADE)
    config = I18n_JSONField(blank=True, null=True, db_column="config")
    label = I18n_TextField(blank=True, null=True)
    visible = models.BooleanField(default=True)
    sortorder = models.IntegerField(blank=True, null=True, default=None)
    source_identifier = models.ForeignKey(
        "self",
        db_column="source_identifier",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    def __init__(self, *args, **kwargs):
        super(CardXNodeXWidget, self).__init__(*args, **kwargs)
        if not self.id:
            self.id = uuid.uuid4()

    def save(self, *args, **kwargs):
        if self.pk == self.source_identifier_id:
            self.source_identifier_id = None
            add_to_update_fields(kwargs, "source_identifier_id")
        super(CardXNodeXWidget, self).save()

    class Meta:
        managed = True
        db_table = "cards_x_nodes_x_widgets"
        unique_together = (("node", "card", "widget"),)


class Concept(models.Model):
    conceptid = models.UUIDField(primary_key=True)
    nodetype = models.ForeignKey(
        "DNodeType", db_column="nodetype", on_delete=models.CASCADE
    )
    legacyoid = models.TextField(unique=True)

    def __init__(self, *args, **kwargs):
        super(Concept, self).__init__(*args, **kwargs)
        if not self.conceptid:
            self.conceptid = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "concepts"


class DDataType(models.Model):
    datatype = models.TextField(primary_key=True)
    iconclass = models.TextField()
    modulename = models.TextField(blank=True, null=True)
    classname = models.TextField(blank=True, null=True)
    defaultwidget = models.ForeignKey(
        db_column="defaultwidget",
        to="models.Widget",
        null=True,
        on_delete=models.SET_NULL,
    )
    defaultconfig = I18n_JSONField(blank=True, null=True, db_column="defaultconfig")
    configcomponent = models.TextField(blank=True, null=True)
    configname = models.TextField(blank=True, null=True)
    issearchable = models.BooleanField(default=False, null=True)
    isgeometric = models.BooleanField()

    def __str__(self):
        return self.datatype

    class Meta:
        managed = True
        db_table = "d_data_types"


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
    edgeid = models.UUIDField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    ontologyproperty = models.TextField(blank=True, null=True)
    domainnode = models.ForeignKey(
        "Node",
        db_column="domainnodeid",
        related_name="edge_domains",
        on_delete=models.CASCADE,
    )
    rangenode = models.ForeignKey(
        "Node",
        db_column="rangenodeid",
        related_name="edge_ranges",
        on_delete=models.CASCADE,
    )
    graph = models.ForeignKey(
        "GraphModel",
        db_column="graphid",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    source_identifier = models.ForeignKey(
        "self",
        db_column="source_identifier",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    def __init__(self, *args, **kwargs):
        super(Edge, self).__init__(*args, **kwargs)
        if not self.edgeid:
            self.edgeid = uuid.uuid4()
        if isinstance(self.edgeid, str):
            self.edgeid = uuid.UUID(self.edgeid)

    def save(self, *args, **kwargs):
        if self.pk == self.source_identifier_id:
            self.source_identifier_id = None
            add_to_update_fields(kwargs, "source_identifier_id")
        super(Edge, self).save()

    class Meta:
        managed = True
        db_table = "edges"
        unique_together = (("rangenode", "domainnode"),)


class EditLog(models.Model):
    editlogid = models.UUIDField(primary_key=True)
    transactionid = models.UUIDField(default=uuid.uuid1)
    resourcedisplayname = models.TextField(blank=True, null=True)
    resourceclassid = models.TextField(blank=True, null=True)
    resourceinstanceid = models.TextField(blank=True, null=True)
    nodegroupid = models.TextField(blank=True, null=True)
    tileinstanceid = models.TextField(blank=True, null=True)
    edittype = models.TextField(blank=True, null=True)
    newvalue = JSONField(blank=True, null=True, db_column="newvalue")
    oldvalue = JSONField(blank=True, null=True, db_column="oldvalue")
    newprovisionalvalue = JSONField(
        blank=True, null=True, db_column="newprovisionalvalue"
    )
    oldprovisionalvalue = JSONField(
        blank=True, null=True, db_column="oldprovisionalvalue"
    )
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

    def __init__(self, *args, **kwargs):
        super(EditLog, self).__init__(*args, **kwargs)
        if not self.editlogid:
            self.editlogid = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "edit_log"
        indexes = [
            models.Index(fields=["transactionid"]),
            models.Index(fields=["resourceinstanceid"]),
        ]


class ExternalOauthToken(models.Model):
    token_id = models.UUIDField(primary_key=True, serialize=False, unique=True)
    user = models.ForeignKey(
        db_column="userid",
        null=False,
        on_delete=models.CASCADE,
        to=settings.AUTH_USER_MODEL,
    )
    id_token = models.TextField()
    access_token_expiration = models.DateTimeField()
    access_token = models.TextField()
    refresh_token = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs):
        super(ExternalOauthToken, self).__init__(*args, **kwargs)
        if not self.token_id:
            self.token_id = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "external_oauth_tokens"


class ResourceRevisionLog(models.Model):
    logid = models.UUIDField(primary_key=True)
    resourceid = models.UUIDField(default=uuid.uuid1)
    revisionid = models.TextField(
        null=False
    )  # not a ForeignKey so we can track deletions
    synctimestamp = models.DateTimeField(auto_now_add=True, null=False)
    action = models.TextField(blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super(ResourceRevisionLog, self).__init__(*args, **kwargs)
        if not self.logid:
            self.logid = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "resource_revision_log"


class File(models.Model):
    fileid = models.UUIDField(primary_key=True)
    path = models.FileField(
        upload_to=import_class_from_string(settings.FILENAME_GENERATOR)
    )
    tile = models.ForeignKey(
        "TileModel", db_column="tileid", null=True, on_delete=models.CASCADE
    )
    thumbnail_data = models.BinaryField(null=True)

    def __init__(self, *args, **kwargs):
        super(File, self).__init__(*args, **kwargs)
        if not self.fileid:
            self.fileid = uuid.uuid4()

    def save(self, *args, **kwargs):
        self.make_thumbnail(kwargs)
        super(File, self).save(*args, **kwargs)

    def make_thumbnail(self, kwargs_from_save_call, force=False):
        try:
            if ThumbnailGeneratorInstance and (force or self.thumbnail_data is None):
                self.thumbnail_data = ThumbnailGeneratorInstance.get_thumbnail_data(
                    self.path.file
                )
                add_to_update_fields(kwargs_from_save_call, "thumbnail_data")
        except Exception as e:
            logger.error(f"Thumbnail not generated for {self.path}: {e}")
            traceback.print_exc(file=sys.stdout)

    class Meta:
        managed = True
        db_table = "files"


class TempFile(models.Model):
    fileid = models.UUIDField(primary_key=True)
    path = models.FileField(upload_to="archestemp")
    created = models.DateTimeField(auto_now_add=True)
    source = models.TextField()

    def __init__(self, *args, **kwargs):
        super(TempFile, self).__init__(*args, **kwargs)
        if not self.fileid:
            self.fileid = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "files_temporary"


class Function(models.Model):
    functionid = models.UUIDField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    functiontype = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    defaultconfig = JSONField(blank=True, null=True)
    modulename = models.TextField(blank=True, null=True)
    classname = models.TextField(blank=True, null=True)
    component = models.TextField(blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super(Function, self).__init__(*args, **kwargs)
        if not self.functionid:
            self.functionid = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "functions"

    @property
    def defaultconfig_json(self):
        json_string = json.dumps(self.defaultconfig)
        return json_string

    def get_class_module(self):
        return get_class_from_modulename(
            self.modulename, self.classname, ExtensionType.FUNCTIONS
        )


class FunctionXGraph(models.Model):
    id = models.UUIDField(primary_key=True, serialize=False)
    function = models.ForeignKey(
        "Function", on_delete=models.CASCADE, db_column="functionid"
    )
    graph = models.ForeignKey(
        "GraphModel", on_delete=models.CASCADE, db_column="graphid"
    )
    config = JSONField(blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super(FunctionXGraph, self).__init__(*args, **kwargs)
        if not self.id:
            self.id = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "functions_x_graphs"
        unique_together = ("function", "graph")


class GraphModel(models.Model):
    graphid = models.UUIDField(primary_key=True)
    name = I18n_TextField(blank=True, null=True)
    description = I18n_TextField(blank=True, null=True)
    deploymentfile = models.TextField(blank=True, null=True)
    author = models.TextField(blank=True, null=True)
    deploymentdate = models.DateTimeField(blank=True, null=True)
    version = models.TextField(blank=True, null=True)
    isresource = models.BooleanField()
    is_active = models.BooleanField(default=False)
    is_copy_immutable = models.BooleanField(default=False)
    iconclass = models.TextField(blank=True, null=True)
    color = models.TextField(blank=True, null=True)
    subtitle = I18n_TextField(blank=True, null=True)
    ontology = models.ForeignKey(
        "Ontology",
        db_column="ontologyid",
        related_name="graphs",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    functions = models.ManyToManyField(to="Function", through="FunctionXGraph")
    jsonldcontext = models.TextField(blank=True, null=True)
    template = models.ForeignKey(
        "ReportTemplate",
        db_column="templateid",
        default="50000000-0000-0000-0000-000000000001",
        on_delete=models.SET_DEFAULT,
    )
    config = JSONField(db_column="config", default=dict)
    slug = models.TextField(validators=[validate_slug], null=True)
    publication = models.ForeignKey(
        "GraphXPublishedGraph",
        db_column="publicationid",
        null=True,
        on_delete=models.SET_NULL,
    )
    source_identifier = models.ForeignKey(
        blank=True,
        db_column="source_identifier",
        null=True,
        on_delete=models.CASCADE,
        to="models.graphmodel",
    )
    has_unpublished_changes = models.BooleanField(default=False)
    resource_instance_lifecycle = models.ForeignKey(
        null=True,
        on_delete=models.PROTECT,
        to="models.ResourceInstanceLifecycle",
        related_name="graphs",
    )

    @property
    def disable_instance_creation(self):
        if not self.isresource:
            return _("Only resource models may be edited - branches are not editable")
        if not self.is_active:
            return _(
                "This Model is not active, and is not available for instance creation."
            )
        if self.has_unpublished_changes:
            return _(
                "This Model has unpublished changes, and is not available for instance creation."
            )
        return False

    def is_editable(self):
        if self.isresource:
            return not ResourceInstance.objects.filter(graph_id=self.graphid).exists()
        else:
            return True

    def get_published_graph(self, language=None, raise_if_missing=False):
        if not language:
            language = translation.get_language()

        try:
            graph = PublishedGraph.objects.get(
                publication=self.publication, language=language
            )
        except PublishedGraph.DoesNotExist:
            if raise_if_missing:
                raise
            graph = None

        return graph

    def save(self, *args, **kwargs):
        if (
            self.isresource
            and not self.source_identifier
            and not self.resource_instance_lifecycle
        ):
            self.resource_instance_lifecycle_id = (
                settings.DEFAULT_RESOURCE_INSTANCE_LIFECYCLE_ID
            )
            add_to_update_fields(kwargs, "resource_instance_lifecycle_id")

        super(GraphModel, self).save(*args, **kwargs)

    @classmethod
    def check(cls, **kwargs):
        errors = super().check(**kwargs)
        errors.extend(cls._check_publication_in_every_language())
        return errors

    @classmethod
    def _check_publication_in_every_language(cls):
        errors = []
        system_languages = {lang[0] for lang in settings.LANGUAGES}

        for graph in (
            cls.objects.filter(publication__isnull=False)
            .select_related("publication")
            .prefetch_related("publication__publishedgraph_set")
        ):
            languages_with_a_publication = {
                published_graph.language_id
                for published_graph in graph.publication.publishedgraph_set.all()
            }
            missing_languages = system_languages - languages_with_a_publication
            if missing_languages:
                errors.append(
                    checks.Error(
                        "This graph is not published in all enabled languages.",
                        hint="Run python manage.py graph publish --update",
                        obj=graph,
                        id="arches.E004",  # TODO: enum in arches 8
                    )
                )

        return errors

    def __str__(self):
        return str(self.name)

    def __init__(self, *args, **kwargs):
        super(GraphModel, self).__init__(*args, **kwargs)
        if not self.graphid:
            self.graphid = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "graphs"

        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(isresource=False, resource_instance_lifecycle__isnull=True)
                    | Q(
                        isresource=True,
                        source_identifier__isnull=False,
                        resource_instance_lifecycle__isnull=True,
                    )
                    | Q(
                        isresource=True,
                        source_identifier__isnull=True,
                        resource_instance_lifecycle__isnull=False,
                    )
                ),
                name="resource_instance_lifecycle_conditional_null",
            )
        ]


class GraphXPublishedGraph(models.Model):
    publicationid = models.UUIDField(
        primary_key=True, serialize=False, default=uuid.uuid1
    )
    notes = models.TextField(blank=True, null=True)
    graph = models.ForeignKey(GraphModel, db_column="graphid", on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, db_column="userid", null=True, on_delete=models.DO_NOTHING
    )
    published_time = models.DateTimeField(default=datetime.datetime.now, null=False)
    most_recent_edit = models.ForeignKey(
        "PublishedGraphEdit",
        db_column="edit_id",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
    )

    class Meta:
        managed = True
        db_table = "graphs_x_published_graphs"


class Icon(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    cssclass = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "icons"


class Language(models.Model):
    LEFT_TO_RIGHT = "ltr"
    RIGHT_TO_LEFT = "rtl"
    LANGUAGE_DIRECTION_CHOICES = [
        (LEFT_TO_RIGHT, "Left to Right"),
        (RIGHT_TO_LEFT, "Right to Left"),
    ]

    SYSTEM_SCOPE = "system"
    DATA_SCOPE = "data"
    SCOPE_CHOICES = [(SYSTEM_SCOPE, "System Scope"), (DATA_SCOPE, "Data Scope")]
    id = models.AutoField(primary_key=True)
    code = models.TextField(unique=True)  # ISO639 code
    name = models.TextField()
    default_direction = models.TextField(
        choices=LANGUAGE_DIRECTION_CHOICES, default=LEFT_TO_RIGHT
    )
    scope = models.TextField(choices=SCOPE_CHOICES, default=SYSTEM_SCOPE)
    isdefault = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = "languages"


class NodeGroup(models.Model):
    nodegroupid = models.UUIDField(primary_key=True)
    legacygroupid = models.TextField(blank=True, null=True)
    cardinality = models.TextField(blank=True, default="1")
    parentnodegroup = models.ForeignKey(
        "self",
        db_column="parentnodegroupid",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )  # Allows nodegroups within nodegroups

    def __init__(self, *args, **kwargs):
        super(NodeGroup, self).__init__(*args, **kwargs)
        if not self.nodegroupid:
            self.nodegroupid = uuid.uuid4()

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

    def __init__(self, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)
        if not self.id:
            self.id = uuid.uuid4()
        if isinstance(self.id, str):
            self.id = uuid.UUID(self.id)

    nodeid = models.UUIDField(primary_key=True)
    name = models.TextField()
    description = models.TextField(blank=True, null=True)
    istopnode = models.BooleanField()
    ontologyclass = models.TextField(blank=True, null=True)
    datatype = models.TextField()
    nodegroup = models.ForeignKey(
        NodeGroup,
        db_column="nodegroupid",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    graph = models.ForeignKey(
        GraphModel, db_column="graphid", blank=True, null=True, on_delete=models.CASCADE
    )
    config = I18n_JSONField(blank=True, null=True, db_column="config")
    issearchable = models.BooleanField(default=True)
    isrequired = models.BooleanField(default=False)
    is_immutable = models.BooleanField(default=False)
    sortorder = models.IntegerField(blank=True, null=True, default=0)
    fieldname = models.TextField(blank=True, null=True)
    exportable = models.BooleanField(default=False, null=True)
    alias = models.TextField(blank=True, null=True)
    hascustomalias = models.BooleanField(default=False)
    source_identifier = models.ForeignKey(
        "self",
        db_column="source_identifier",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    sourcebranchpublication = models.ForeignKey(
        GraphXPublishedGraph,
        db_column="sourcebranchpublicationid",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

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
        return (
            str(self.nodeid) == str(self.nodegroup_id) and self.nodegroup_id is not None
        )

    def get_relatable_resources(self):
        relatable_resource_ids = [
            r2r.resourceclassfrom
            for r2r in Resource2ResourceConstraint.objects.filter(
                resourceclassto_id=self.nodeid
            )
            if r2r.resourceclassfrom is not None
        ]
        relatable_resource_ids = relatable_resource_ids + [
            r2r.resourceclassto
            for r2r in Resource2ResourceConstraint.objects.filter(
                resourceclassfrom_id=self.nodeid
            )
            if r2r.resourceclassto is not None
        ]
        return relatable_resource_ids

    def set_relatable_resources(self, new_ids):
        old_ids = [res.nodeid for res in self.get_relatable_resources()]
        for old_id in old_ids:
            if old_id not in new_ids:
                Resource2ResourceConstraint.objects.filter(
                    Q(resourceclassto_id=self.nodeid)
                    | Q(resourceclassfrom_id=self.nodeid),
                    Q(resourceclassto_id=old_id) | Q(resourceclassfrom_id=old_id),
                ).delete()
        for new_id in new_ids:
            if new_id not in old_ids:
                new_r2r = Resource2ResourceConstraint.objects.create(
                    resourceclassfrom_id=self.nodeid, resourceclassto_id=new_id
                )
                new_r2r.save()

    def serialize(self, fields=None, exclude=None, **kwargs):
        ret = JSONSerializer().handle_model(
            self, fields=fields, exclude=exclude, **kwargs
        )

        if ret["config"] and ret["config"].get("options"):
            ret["config"]["options"] = sorted(
                ret["config"]["options"], key=lambda k: k["id"]
            )

        return ret

    def __init__(self, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)
        if not self.nodeid:
            self.nodeid = uuid.uuid4()

    def save(self, *args, **kwargs):
        if self.pk == self.source_identifier_id:
            self.source_identifier_id = None
            add_to_update_fields(kwargs, "source_identifier_id")
        super(Node, self).save()

    class Meta:
        managed = True
        db_table = "nodes"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "nodegroup"], name="unique_nodename_nodegroup"
            ),
            models.UniqueConstraint(
                fields=["alias", "graph"], name="unique_alias_graph"
            ),
        ]


class Ontology(models.Model):
    ontologyid = models.UUIDField(primary_key=True)
    name = models.TextField()
    version = models.TextField()
    path = models.TextField(null=True, blank=True)
    namespaces = JSONField(null=True, blank=True)
    parentontology = models.ForeignKey(
        "Ontology",
        db_column="parentontologyid",
        related_name="extensions",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    def __init__(self, *args, **kwargs):
        super(Ontology, self).__init__(*args, **kwargs)
        if not self.ontologyid:
            self.ontologyid = uuid.uuid4()

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

    ontologyclassid = models.UUIDField(primary_key=True)
    source = models.TextField()
    target = JSONField(null=True)
    ontology = models.ForeignKey(
        "Ontology",
        db_column="ontologyid",
        related_name="ontologyclasses",
        on_delete=models.CASCADE,
    )

    def __init__(self, *args, **kwargs):
        super(OntologyClass, self).__init__(*args, **kwargs)
        if not self.ontologyclassid:
            self.ontologyclassid = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "ontologyclasses"
        unique_together = (("source", "ontology"),)


class PublishedGraph(models.Model):
    language = models.ForeignKey(
        Language,
        db_column="languageid",
        to_field="code",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    publication = models.ForeignKey(
        GraphXPublishedGraph, db_column="publicationid", on_delete=models.CASCADE
    )
    serialized_graph = models.JSONField(
        blank=True, null=True, db_column="serialized_graph"
    )

    class Meta:
        managed = True
        db_table = "published_graphs"


class PublishedGraphEdit(models.Model):
    edit_id = models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid1)
    edit_time = models.DateTimeField(default=datetime.datetime.now, null=False)
    publication = models.ForeignKey(
        GraphXPublishedGraph, db_column="publicationid", on_delete=models.CASCADE
    )
    notes = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = "published_graph_edits"


class Relation(models.Model):
    conceptfrom = models.ForeignKey(
        Concept,
        db_column="conceptidfrom",
        related_name="relation_concepts_from",
        on_delete=models.CASCADE,
    )
    conceptto = models.ForeignKey(
        Concept,
        db_column="conceptidto",
        related_name="relation_concepts_to",
        on_delete=models.CASCADE,
    )
    relationtype = models.ForeignKey(
        DRelationType, db_column="relationtype", on_delete=models.CASCADE
    )
    relationid = models.UUIDField(primary_key=True)

    def __init__(self, *args, **kwargs):
        super(Relation, self).__init__(*args, **kwargs)
        if not self.relationid:
            self.relationid = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "relations"
        unique_together = (("conceptfrom", "conceptto", "relationtype"),)


class ReportTemplate(models.Model):
    templateid = models.UUIDField(primary_key=True)
    preload_resource_data = models.BooleanField(default=True)
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    component = models.TextField()
    componentname = models.TextField()
    defaultconfig = JSONField(blank=True, null=True, db_column="defaultconfig")

    @property
    def defaultconfig_json(self):
        json_string = json.dumps(self.defaultconfig)
        return json_string

    def __init__(self, *args, **kwargs):
        super(ReportTemplate, self).__init__(*args, **kwargs)
        if not self.templateid:
            self.templateid = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "report_templates"


class Resource2ResourceConstraint(models.Model):
    resource2resourceid = models.UUIDField(primary_key=True)
    resourceclassfrom = models.ForeignKey(
        Node,
        db_column="resourceclassfrom",
        blank=True,
        null=True,
        related_name="resxres_contstraint_classes_from",
        on_delete=models.SET_NULL,
    )
    resourceclassto = models.ForeignKey(
        Node,
        db_column="resourceclassto",
        blank=True,
        null=True,
        related_name="resxres_contstraint_classes_to",
        on_delete=models.SET_NULL,
    )

    def __init__(self, *args, **kwargs):
        super(Resource2ResourceConstraint, self).__init__(*args, **kwargs)
        if not self.resource2resourceid:
            self.resource2resourceid = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "resource_2_resource_constraints"


class ResourceXResource(models.Model):
    resourcexid = models.UUIDField(primary_key=True)
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

    def delete(self, *args, **kwargs):
        # update the resource-instance tile by removing any references to a deleted resource
        deletedResourceId = kwargs.pop("deletedResourceId", None)
        if deletedResourceId and self.tileid and self.nodeid:
            newTileData = []
            data = self.tileid.data[str(self.nodeid_id)]
            if type(data) != list:
                data = [data]
            for relatedresourceItem in data:
                if relatedresourceItem:
                    if relatedresourceItem["resourceId"] != str(deletedResourceId):
                        newTileData.append(relatedresourceItem)
            self.tileid.data[str(self.nodeid_id)] = newTileData
            self.tileid.save()

        super(ResourceXResource, self).delete()

    def save(self, *args, **kwargs):
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
            add_to_update_fields(kwargs, "created")
        self.modified = datetime.datetime.now()
        add_to_update_fields(kwargs, "modified")

        super(ResourceXResource, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(ResourceXResource, self).__init__(*args, **kwargs)
        if not self.resourcexid:
            self.resourcexid = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "resource_x_resource"


class ResourceInstance(models.Model):
    resourceinstanceid = models.UUIDField(primary_key=True)
    graph = models.ForeignKey(GraphModel, db_column="graphid", on_delete=models.CASCADE)
    graph_publication = models.ForeignKey(
        GraphXPublishedGraph,
        null=True,
        db_column="graphpublicationid",
        on_delete=models.PROTECT,
    )
    name = I18n_TextField(blank=True, null=True)
    descriptors = models.JSONField(blank=True, null=True)
    legacyid = models.TextField(blank=True, unique=True, null=True)
    createdtime = models.DateTimeField(auto_now_add=True)
    resource_instance_lifecycle_state = models.ForeignKey(
        on_delete=models.PROTECT,
        to="models.ResourceInstanceLifecycleState",
        related_name="resource_instances",
    )

    def get_initial_resource_instance_lifecycle_state(self, *args, **kwargs):
        try:
            return (
                self.graph.resource_instance_lifecycle.get_initial_resource_instance_lifecycle_state()
            )
        except (ObjectDoesNotExist, AttributeError):
            return None

    # This could be used as a lock, but primarily addresses the issue that a creating user
    # may not yet match the criteria to edit a ResourceInstance (via Set/LogicalSet) simply
    # because the details may not yet be complete. Only one user can create, as it is an
    # action, not a state, so we do not need an array here. That may be desirable depending on
    # future use of this field (e.g. locking to a group).
    # Note that this is intended to bypass normal permissions logic, so a resource type must
    # prevent a user who created the resource from editing it, by updating principaluserid logic.
    principaluser = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True
    )

    def get_instance_creator_and_edit_permissions(self, user=None):
        creatorid = None
        can_edit = None

        creatorid = self.get_instance_creator()

        if user:
            can_edit = user.id == creatorid or user.is_superuser
        return {"creatorid": creatorid, "user_can_edit_instance_permissions": can_edit}

    def get_instance_creator(self) -> int:
        create_record = EditLog.objects.filter(
            resourceinstanceid=self.resourceinstanceid, edittype="create"
        ).first()
        creatorid = None

        if create_record:
            try:
                creatorid = int(create_record.userid)
            except (ValueError, TypeError):
                pass

        if creatorid is None:
            creatorid = settings.DEFAULT_RESOURCE_IMPORT_USER["userid"]

        return creatorid

    def save(self, *args, **kwargs):
        try:
            self.graph_publication = self.graph.publication
        except ResourceInstance.graph.RelatedObjectDoesNotExist:
            pass

        if not hasattr(self, "resource_instance_lifecycle_state"):
            self.resource_instance_lifecycle_state = (
                self.get_initial_resource_instance_lifecycle_state()
            )

        add_to_update_fields(kwargs, "resource_instance_lifecycle_state")
        add_to_update_fields(kwargs, "graph_publication")
        super(ResourceInstance, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(ResourceInstance, self).__init__(*args, **kwargs)
        if not self.resourceinstanceid:
            self.resourceinstanceid = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "resource_instances"
        permissions = (("no_access_to_resourceinstance", "No Access"),)


class ResourceInstanceLifecycle(models.Model):
    id = models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid4)
    name = I18n_TextField()

    def get_initial_resource_instance_lifecycle_state(self):
        return self.resource_instance_lifecycle_states.get(is_initial_state=True)

    def serialize(self, fields=None, exclude=None, **kwargs):
        ret = JSONSerializer().handle_model(
            self, fields=fields, exclude=exclude, **kwargs
        )

        ret["resource_instance_lifecycle_states"] = [
            JSONSerializer().handle_model(resource_instance_lifecycle_state)
            for resource_instance_lifecycle_state in self.resource_instance_lifecycle_states.all()
        ]

        return ret

    class Meta:
        db_table = "resource_instance_lifecycles"
        managed = True


class ResourceInstanceLifecycleState(models.Model):
    id = models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid4)
    name = I18n_TextField()
    action_label = I18n_TextField()
    is_initial_state = models.BooleanField(default=False)
    can_delete_resource_instances = models.BooleanField(default=False)
    can_edit_resource_instances = models.BooleanField(default=False)
    resource_instance_lifecycle = models.ForeignKey(
        on_delete=models.CASCADE,
        to="models.ResourceInstanceLifecycle",
        related_name="resource_instance_lifecycle_states",
    )
    previous_resource_instance_lifecycle_states = models.ManyToManyField(
        "self",
        through="ResourceInstanceLifecycleStateFromXRef",
        symmetrical=False,
        related_name="next_lifecycle_states",
    )
    next_resource_instance_lifecycle_states = models.ManyToManyField(
        "self",
        through="ResourceInstanceLifecycleStateToXRef",
        symmetrical=False,
        related_name="previous_lifecycle_states",
    )

    def serialize(self, fields=None, exclude=None, **kwargs):
        ret = JSONSerializer().handle_model(
            self, fields=fields, exclude=exclude, **kwargs
        )

        # for serialization we shouldn't need to recurse, 1 level down is enough
        ret["next_resource_instance_lifecycle_states"] = [
            JSONSerializer().handle_model(resource_instance_lifecycle_state)
            for resource_instance_lifecycle_state in self.next_resource_instance_lifecycle_states.all()
        ]
        ret["previous_resource_instance_lifecycle_states"] = [
            JSONSerializer().handle_model(resource_instance_lifecycle_state)
            for resource_instance_lifecycle_state in self.previous_resource_instance_lifecycle_states.all()
        ]

        return ret

    class Meta:
        db_table = "resource_instance_lifecycle_states"
        managed = True
        permissions = (
            (
                "can_edit_all_resource_instance_lifecycle_states",
                "Can edit all resource instance lifecycle states",
            ),
            (
                "can_delete_all_resource_instance_lifecycle_states",
                "Can delete all resource instance lifecycle states",
            ),
        )
        constraints = [
            UniqueConstraint(
                fields=["resource_instance_lifecycle"],
                condition=Q(is_initial_state=True),
                name="unique_initial_state_per_lifecycle",
            ),
        ]


class ResourceInstanceLifecycleStateFromXRef(models.Model):
    resource_instance_lifecycle_state_from = models.ForeignKey(
        ResourceInstanceLifecycleState,
        related_name="from_xref_next_lifecycle_states",
        on_delete=models.CASCADE,
    )
    resource_instance_lifecycle_state_to = models.ForeignKey(
        ResourceInstanceLifecycleState,
        related_name="from_xref_previous_lifecycle_states",
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "resource_instance_lifecycle_states_from_xref"
        managed = True


class ResourceInstanceLifecycleStateToXRef(models.Model):
    resource_instance_lifecycle_state_from = models.ForeignKey(
        ResourceInstanceLifecycleState,
        related_name="to_xref_next_lifecycle_states",
        on_delete=models.CASCADE,
    )
    resource_instance_lifecycle_state_to = models.ForeignKey(
        ResourceInstanceLifecycleState,
        related_name="to_xref_previous_lifecycle_states",
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "resource_instance_lifecycle_states_to_xref"
        managed = True


class SearchComponent(models.Model):
    searchcomponentid = models.UUIDField(primary_key=True)
    name = models.TextField()
    icon = models.TextField(default=None)
    modulename = models.TextField(blank=True, null=True)
    classname = models.TextField(blank=True, null=True)
    type = models.TextField()
    componentpath = models.TextField(unique=True, null=True)
    componentname = models.TextField(unique=True)
    config = models.JSONField(default=dict)

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(SearchComponent, self).__init__(*args, **kwargs)
        if not self.searchcomponentid:
            self.searchcomponentid = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "search_component"

    def get_class_module(self):
        return get_class_from_modulename(
            self.modulename, self.classname, ExtensionType.SEARCH_COMPONENTS
        )

    def toJSON(self):
        return JSONSerializer().serialize(self)


class SearchExportHistory(models.Model):
    searchexportid = models.UUIDField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exporttime = models.DateTimeField(auto_now_add=True)
    numberofinstances = models.IntegerField()
    url = models.TextField()
    downloadfile = models.FileField(
        upload_to="export_deliverables", blank=True, null=True
    )

    def __init__(self, *args, **kwargs):
        super(SearchExportHistory, self).__init__(*args, **kwargs)
        if not self.searchexportid:
            self.searchexportid = uuid.uuid4()

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

    tileid = models.UUIDField(primary_key=True)
    resourceinstance = models.ForeignKey(
        ResourceInstance, db_column="resourceinstanceid", on_delete=models.CASCADE
    )
    parenttile = models.ForeignKey(
        "self",
        db_column="parenttileid",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    data = JSONField(blank=True, null=True, db_column="tiledata")
    nodegroup_id = models.UUIDField(db_column="nodegroupid", null=True)
    sortorder = models.IntegerField(blank=True, null=True, default=0)
    provisionaledits = JSONField(blank=True, null=True, db_column="provisionaledits")

    class Meta:
        managed = True
        db_table = "tiles"

    def __init__(self, *args, **kwargs):
        super(TileModel, self).__init__(*args, **kwargs)
        if not self.tileid:
            self.tileid = uuid.uuid4()

    @property
    def nodegroup(self):
        return NodeGroup.objects.filter(pk=self.nodegroup_id).first()

    def is_fully_provisional(self):
        return bool(self.provisionaledits and not any(self.data.values()))

    def save(self, *args, **kwargs):
        if self.sortorder is None or self.is_fully_provisional():
            for node in Node.objects.filter(nodegroup_id=self.nodegroup_id).exclude(
                datatype="semantic"
            ):
                if not str(node.pk) in self.data:
                    self.data[str(node.pk)] = None

            sortorder_max = TileModel.objects.filter(
                nodegroup_id=self.nodegroup_id,
                resourceinstance_id=self.resourceinstance_id,
            ).aggregate(Max("sortorder"))["sortorder__max"]
            self.sortorder = sortorder_max + 1 if sortorder_max is not None else 0
            add_to_update_fields(kwargs, "sortorder")
        if not self.tileid:
            self.tileid = uuid.uuid4()
            add_to_update_fields(kwargs, "tileid")
        super(TileModel, self).save(*args, **kwargs)  # Call the "real" save() method.

    def serialize(self, fields=None, exclude=["nodegroup"], **kwargs):
        return JSONSerializer().handle_model(
            self, fields=fields, exclude=exclude, **kwargs
        )


class Value(models.Model):
    valueid = models.UUIDField(primary_key=True)
    concept = models.ForeignKey(
        "Concept", db_column="conceptid", on_delete=models.CASCADE
    )
    valuetype = models.ForeignKey(
        DValueType, db_column="valuetype", on_delete=models.CASCADE
    )
    value = models.TextField()
    language = models.ForeignKey(
        Language,
        db_column="languageid",
        to_field="code",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    def __init__(self, *args, **kwargs):
        super(Value, self).__init__(*args, **kwargs)
        if not self.valueid:
            self.valueid = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "values"


class FileValue(models.Model):
    valueid = models.UUIDField(primary_key=True)
    concept = models.ForeignKey(
        "Concept", db_column="conceptid", on_delete=models.CASCADE
    )
    valuetype = models.ForeignKey(
        "DValueType", db_column="valuetype", on_delete=models.CASCADE
    )
    value = models.FileField(upload_to="concepts")
    language = models.ForeignKey(
        Language,
        db_column="languageid",
        to_field="code",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    def __init__(self, *args, **kwargs):
        super(FileValue, self).__init__(*args, **kwargs)
        if not self.valueid:
            self.valueid = uuid.uuid4()

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


class Widget(models.Model):
    widgetid = models.UUIDField(primary_key=True)
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

    def __init__(self, *args, **kwargs):
        super(Widget, self).__init__(*args, **kwargs)
        if not self.widgetid:
            self.widgetid = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "widgets"


class Geocoder(models.Model):
    geocoderid = models.UUIDField(primary_key=True)
    name = models.TextField(unique=True)
    component = models.TextField(unique=True)
    api_key = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(Geocoder, self).__init__(*args, **kwargs)
        if not self.geocoderid:
            self.geocoderid = uuid.uuid4()

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
    maplayerid = models.UUIDField(primary_key=True)
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
    sortorder = models.IntegerField(default=0)
    ispublic = models.BooleanField(default=True)

    @property
    def layer_json(self):
        json_string = json.dumps(self.layerdefinitions)
        return json_string

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(MapLayer, self).__init__(*args, **kwargs)
        if not self.maplayerid:
            self.maplayerid = uuid.uuid4()

    class Meta:
        managed = True
        ordering = ("sortorder", "name")
        db_table = "map_layers"
        default_permissions = ()
        permissions = (
            ("no_access_to_maplayer", "No Access"),
            ("read_maplayer", "Read"),
            ("write_maplayer", "Create/Update"),
            ("delete_maplayer", "Delete"),
        )


class GraphXMapping(models.Model):
    id = models.UUIDField(primary_key=True, serialize=False)
    graph = models.ForeignKey(
        "GraphModel", db_column="graphid", on_delete=models.CASCADE
    )
    mapping = JSONField(blank=True, null=False)

    def __init__(self, *args, **kwargs):
        super(GraphXMapping, self).__init__(*args, **kwargs)
        if not self.id:
            self.id = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "graphs_x_mapping_file"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=16, blank=True)
    encrypted_mfa_hash = models.CharField(max_length=128, null=True, blank=True)

    def is_reviewer(self):
        """DEPRECATED Use new pattern:

        from arches.app.utils.permission_backend import user_is_resource_reviewer
        is_reviewer = user_is_resource_reviewer(user)
        """
        pass

    @property
    def viewable_nodegroups(self):
        from arches.app.utils.permission_backend import get_nodegroups_by_perm

        return set(
            str(nodegroup_pk)
            for nodegroup_pk in get_nodegroups_by_perm(
                self.user, ["models.read_nodegroup"], any_perm=True
            )
        )

    @property
    def editable_nodegroups(self):
        from arches.app.utils.permission_backend import get_nodegroups_by_perm

        return set(
            str(nodegroup_pk)
            for nodegroup_pk in get_nodegroups_by_perm(
                self.user, ["models.write_nodegroup"], any_perm=True
            )
        )

    @property
    def deletable_nodegroups(self):
        from arches.app.utils.permission_backend import get_nodegroups_by_perm

        return set(
            str(nodegroup_pk)
            for nodegroup_pk in get_nodegroups_by_perm(
                self.user, ["models.delete_nodegroup"], any_perm=True
            )
        )

    class Meta:
        managed = True
        db_table = "user_profile"


class UserXTask(models.Model):
    id = models.UUIDField(primary_key=True, serialize=False)
    taskid = models.UUIDField(serialize=False, blank=True, null=True)
    status = models.TextField(null=True, default="PENDING")
    datestart = models.DateTimeField(blank=True, null=True)
    datedone = models.DateTimeField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        super(UserXTask, self).__init__(*args, **kwargs)
        if not self.id:
            self.id = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "user_x_tasks"


class NotificationType(models.Model):
    """
    Creates a 'type' of notification that would be associated with a specific trigger, e.g. Search Export Complete or Package Load Complete
    Must be created manually using Django ORM or SQL.
    """

    typeid = models.UUIDField(primary_key=True, serialize=False)
    name = models.TextField(blank=True, null=True)
    emailtemplate = models.TextField(blank=True, null=True)
    emailnotify = models.BooleanField(default=False)
    webnotify = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(NotificationType, self).__init__(*args, **kwargs)
        if not self.typeid:
            self.typeid = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "notification_types"


class Notification(models.Model):
    """
    A Notification instance that may optionally have a NotificationType. Can spawn N UserXNotification instances
    Must be created manually using Django ORM.
    """

    id = models.UUIDField(primary_key=True, serialize=False)
    created = models.DateTimeField(auto_now_add=True)
    # created.editable = True
    message = models.TextField(blank=True, null=True)
    context = JSONField(blank=True, null=True, default=dict, encoder=DjangoJSONEncoder)
    # TODO: Ideally validate context against a list of keys from NotificationType
    notiftype = models.ForeignKey(NotificationType, on_delete=models.CASCADE, null=True)

    def __init__(self, *args, **kwargs):
        super(Notification, self).__init__(*args, **kwargs)
        if not self.id:
            self.id = uuid.uuid4()

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

    id = models.UUIDField(primary_key=True, serialize=False)
    notif = models.ForeignKey(Notification, on_delete=models.CASCADE)
    isread = models.BooleanField(default=False)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        super(UserXNotification, self).__init__(*args, **kwargs)
        if not self.id:
            self.id = uuid.uuid4()

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

    id = models.UUIDField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notiftype = models.ForeignKey(NotificationType, on_delete=models.CASCADE)
    emailnotify = models.BooleanField(default=False)
    webnotify = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(UserXNotificationType, self).__init__(*args, **kwargs)
        if not self.id:
            self.id = uuid.uuid4()

    class Meta:
        managed = True
        db_table = "user_x_notification_types"


def getDataDownloadConfigDefaults():
    return dict(download=False, count=100, resources=[], custom=None)


class MapMarker(models.Model):
    name = models.TextField(unique=True)
    url = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = "map_markers"


class Plugin(models.Model):
    pluginid = models.UUIDField(primary_key=True)
    name = I18n_TextField(null=True, blank=True)
    icon = models.TextField(default=None)
    component = models.TextField()
    componentname = models.TextField()
    config = I18n_JSONField(blank=True, null=True, db_column="config")
    slug = models.TextField(validators=[validate_slug], unique=True, null=True)
    sortorder = models.IntegerField(blank=True, null=True, default=None)
    helptemplate = models.TextField(blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super(Plugin, self).__init__(*args, **kwargs)
        if not self.pluginid:
            self.pluginid = uuid.uuid4()

    def __str__(self):
        return str(self.name)

    class Meta:
        managed = True
        db_table = "plugins"


class WorkflowHistory(models.Model):
    workflowid = models.UUIDField(primary_key=True)
    workflowname = models.CharField(null=True, max_length=255)
    stepdata = JSONField(null=False, default=dict)
    componentdata = JSONField(null=False, default=dict)
    # `auto_now_add` marks the field as non-editable, which prevents the field from being serialized, so updating to use `default` instead
    created = models.DateTimeField(default=django.utils.timezone.now, null=False)
    user = models.ForeignKey(
        db_column="userid",
        null=True,
        on_delete=models.SET_NULL,
        to=settings.AUTH_USER_MODEL,
    )
    completed = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = "workflow_history"


class IIIFManifestValidationError(Exception):
    def __init__(self, message, code=None):
        self.title = _("Image Service Validation Error")
        self.message = message
        self.code = code

    def __str__(self):
        return repr(self)


class IIIFManifest(models.Model):
    label = models.TextField()
    url = models.TextField()
    description = models.TextField(blank=True, null=True)
    manifest = JSONField(blank=True, null=True)
    globalid = models.UUIDField(default=uuid.uuid4, unique=True)
    transactionid = models.UUIDField(default=uuid.uuid4, null=True)

    def __str__(self):
        return self.label

    class Meta:
        managed = True
        db_table = "iiif_manifests"

    def delete(self, *args, **kwargs):
        all_canvases = {annotation.canvas for annotation in VwAnnotation.objects.all()}
        canvases_in_manifest = self.manifest["sequences"][0]["canvases"]
        canvas_ids = [
            canvas["images"][0]["resource"]["service"]["@id"]
            for canvas in canvases_in_manifest
        ]
        canvases_in_use = []
        for canvas_id in canvas_ids:
            if canvas_id in all_canvases:
                canvases_in_use.append(canvas_id)
        if len(canvases_in_use) > 0:
            canvas_labels_in_use = [
                item["label"]
                for item in canvases_in_manifest
                if item["images"][0]["resource"]["service"]["@id"] in canvases_in_use
            ]
            message = _(
                "This image service cannot be deleted because the following canvases have resource annotations: {}"
            ).format(", ".join(canvas_labels_in_use))
            raise IIIFManifestValidationError(message)

        super(IIIFManifest, self).delete()


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


class VwAnnotation(models.Model):
    feature_id = models.UUIDField(primary_key=True)
    tile = models.ForeignKey(TileModel, on_delete=models.DO_NOTHING, db_column="tileid")
    tiledata = JSONField()
    resourceinstance = models.ForeignKey(
        ResourceInstance, on_delete=models.DO_NOTHING, db_column="resourceinstanceid"
    )
    nodegroup = models.ForeignKey(
        NodeGroup, on_delete=models.DO_NOTHING, db_column="nodegroupid"
    )
    node = models.ForeignKey(Node, on_delete=models.DO_NOTHING, db_column="nodeid")
    feature = JSONField()
    canvas = models.TextField()

    def __init__(self, *args, **kwargs):
        super(VwAnnotation, self).__init__(*args, **kwargs)
        if not self.feature_id:
            self.feature_id = uuid.uuid4()

    class Meta:
        managed = False
        db_table = "vw_annotations"


class GeoJSONGeometry(models.Model):
    tile = models.ForeignKey(TileModel, on_delete=models.CASCADE, db_column="tileid")
    resourceinstance = models.ForeignKey(
        ResourceInstance, on_delete=models.CASCADE, db_column="resourceinstanceid"
    )
    node = models.ForeignKey(Node, on_delete=models.CASCADE, db_column="nodeid")
    geom = models.GeometryField(srid=3857)
    featureid = models.UUIDField(serialize=False, blank=True, null=True)

    class Meta:
        managed = True
        db_table = "geojson_geometries"


class ETLModule(models.Model):
    etlmoduleid = models.UUIDField(primary_key=True, default=uuid.uuid1)
    name = models.TextField()
    icon = models.TextField()
    etl_type = models.TextField()
    component = models.TextField()
    componentname = models.TextField()
    modulename = models.TextField(blank=True, null=True)
    classname = models.TextField(blank=True, null=True)
    config = JSONField(blank=True, null=True, db_column="config")
    reversible = models.BooleanField(default=True)
    slug = models.TextField(validators=[validate_slug], unique=True, null=True)
    description = models.TextField(blank=True, null=True)
    helptemplate = models.TextField(blank=True, null=True)
    helpsortorder = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = True
        db_table = "etl_modules"

    def get_class_module(self):
        return get_class_from_modulename(
            self.modulename, self.classname, ExtensionType.ETL_MODULES
        )


class LoadEvent(models.Model):
    loadid = models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    complete = models.BooleanField(default=False)
    successful = models.BooleanField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    etl_module = models.ForeignKey(ETLModule, on_delete=models.CASCADE)
    load_description = models.TextField(blank=True, null=True)
    load_details = JSONField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    load_start_time = models.DateTimeField(blank=True, null=True)
    load_end_time = models.DateTimeField(blank=True, null=True)
    indexed_time = models.DateTimeField(blank=True, null=True)
    taskid = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "load_event"


class LoadStaging(models.Model):
    nodegroup = models.ForeignKey(
        NodeGroup, db_column="nodegroupid", on_delete=models.CASCADE
    )
    load_event = models.ForeignKey(
        LoadEvent, db_column="loadid", on_delete=models.CASCADE
    )
    value = JSONField(blank=True, null=True, db_column="value")
    legacyid = models.TextField(blank=True, null=True)
    resourceid = models.UUIDField(serialize=False, blank=True, null=True)
    tileid = models.UUIDField(serialize=False, blank=True, null=True)
    parenttileid = models.UUIDField(serialize=False, blank=True, null=True)
    passes_validation = models.BooleanField(blank=True, null=True)
    nodegroup_depth = models.IntegerField(default=1)
    source_description = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    operation = models.TextField(default="insert")

    class Meta:
        managed = True
        db_table = "load_staging"


class LoadErrors(models.Model):
    load_event = models.ForeignKey(
        LoadEvent, db_column="loadid", on_delete=models.CASCADE
    )
    nodegroup = models.ForeignKey(
        "NodeGroup",
        db_column="nodegroupid",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    node = models.ForeignKey(
        "Node", db_column="nodeid", null=True, blank=True, on_delete=models.CASCADE
    )
    type = models.TextField(blank=True, null=True)
    error = models.TextField(blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    value = models.TextField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    datatype = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "load_errors"


class SpatialView(models.Model):
    spatialviewid = models.UUIDField(primary_key=True, default=uuid.uuid1)
    schema = models.TextField(default="public")
    slug = models.TextField(
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Z_]([a-zA-Z0-9_]+)$",
                message="Slug must contain only letters, numbers and hyphens, but not begin with a number.",
                code="nomatch",
            )
        ],
        unique=True,
        null=False,
    )
    description = models.TextField(
        default="arches spatial view"
    )  # provide a description of the spatial view
    geometrynode = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        db_column="geometrynodeid",
        limit_choices_to={"datatype": "geojson-feature-collection"},
        null=False,
    )
    ismixedgeometrytypes = models.BooleanField(default=False)
    language = models.ForeignKey(
        Language,
        db_column="languageid",
        to_field="code",
        on_delete=models.PROTECT,
        null=False,
    )
    attributenodes = JSONField(blank=False, null=False, db_column="attributenodes")
    isactive = models.BooleanField(
        default=True
    )  # the view is not created in the DB until set to active.

    def __str__(self):
        return f"{self.schema}.{self.slug}"

    class Meta:
        managed = True
        db_table = "spatial_views"

    def clean(self):
        """
        Validate the spatial view before saving it to the database as the database triggers have proved hard to test.
        """
        graph = self.geometrynode.graph
        try:
            node_ids = set(node["nodeid"] for node in self.attributenodes)
        except (KeyError, TypeError):
            raise ValidationError("attributenodes must be a list of node objects")

        found_graph_nodes = Node.objects.filter(pk__in=node_ids, graph=graph)
        if len(node_ids) != found_graph_nodes.count():
            raise ValidationError(
                "One or more attributenodes do not belong to the graph of the geometry node"
            )

        # language must be be a valid language code belonging to the current publication
        published_graphs = graph.publication.publishedgraph_set.all()
        if self.language_id not in [
            published_graph.language_id for published_graph in published_graphs
        ]:
            raise ValidationError(
                "Language must belong to a published graph for the graph of the geometry node"
            )

        # validate the schema is a valid schema in the database
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s",
                [self.schema],
            )
            if cursor.rowcount == 0:
                raise ValidationError("Schema does not exist in the database")

    def to_json(self):
        """
        Returns a JSON object representing the spatialview
        """
        return {
            "spatialviewid": str(self.spatialviewid),
            "schema": self.schema,
            "slug": self.slug,
            "description": self.description,
            "geometrynodeid": str(self.geometrynode.pk),
            "ismixedgeometrytypes": self.ismixedgeometrytypes,
            "language": self.language.code,
            "attributenodes": self.attributenodes,
            "isactive": self.isactive,
        }


# Import proxy models to ensure they are always discovered.
# For example, if the urls.py module is not imported because a management command
# skips system checks, the coincidental importing of the Graph(Proxy)Model
# by certain views will not happen, and Django will never find the proxy models.
# Long term, we want the module in INSTALLED_APPS (arches.app.models)
# to contain all the models, usually done by creating arches.app.models.__init__,
# but there's a circular import between the model and proxy model that subclasses it.
# The circular import is the same reason these imports are at the bottom of this file.
# Or can we replace the proxy models by moving functionality to plain model methods?
from .card import *
from .graph import *
from .resource import *
from .tile import *
