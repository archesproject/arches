# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import uuid
import codecs
import django.contrib.gis.db.models.fields
from django.core import management
from django.conf import settings
from django.db import migrations, models
from django.contrib.postgres.fields import JSONField
from arches.app.models.models import get_ontology_storage_system
from arches.db.migration_operations.extras import CreateExtension, CreateAutoPopulateUUIDField, CreateFunction

def get_sql_string_from_file(pathtofile):
    ret = []
    with codecs.open(pathtofile, encoding='utf-8') as f:
        ret = f.read()
        #print sqlparse.split(sqlparse.format(ret,strip_comments=True))
        # for stmt in sqlparse.split(sqlparse.format(f.read(),strip_comments=True)):
        #     if stmt.strip() != '':
        #         ret.append(stmt)
    return ret

def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version

    path_to_ontologies = os.path.join(settings.ROOT_DIR, 'db', 'ontologies', 'cidoc_crm')
    extensions = [
        os.path.join(path_to_ontologies, 'CRMsci_v1.2.3.rdfs.xml'),
        os.path.join(path_to_ontologies, 'CRMarchaeo_v1.4.rdfs.xml'),
        os.path.join(path_to_ontologies, 'CRMgeo_v1.2.rdfs.xml'),
        os.path.join(path_to_ontologies, 'CRMdig_v3.2.1.rdfs.xml'),
        os.path.join(path_to_ontologies, 'CRMinf_v0.7.rdfs.xml')
    ]
    management.call_command('load_ontology', source=os.path.join(path_to_ontologies, 'cidoc_crm_v6.2.xml'),
        version='6.2', ontology_name='CIDOC CRM v6.2', id='e6e8db47-2ccf-11e6-927e-b8f6b115d7dd', extensions=','.join(extensions))

def reverse_func(apps, schema_editor):
    Ontology = apps.get_model("models", "Ontology")
    Ontology.objects.filter(version='6.2').delete()

# a work around for not being able to create permissions during an initial migration
# from https://code.djangoproject.com/ticket/23422#comment:6
def make_permissions(apps, schema_editor, with_create_permissions=True):
    db_alias = schema_editor.connection.alias
    Group = apps.get_model("auth", "Group")
    User = apps.get_model("auth", "User")
    Permission = apps.get_model("auth", "Permission")
    try:
        read_perm = Permission.objects.get(codename='read_nodegroup', content_type__app_label='models', content_type__model='nodegroup')
        write_perm = Permission.objects.using(db_alias).get(codename='write_nodegroup', content_type__app_label='models', content_type__model='nodegroup')
        delete_perm = Permission.objects.using(db_alias).get(codename='delete_nodegroup', content_type__app_label='models', content_type__model='nodegroup')
    except Permission.DoesNotExist:
        if with_create_permissions:
            # Manually run create_permissions
            from django.contrib.auth.management import create_permissions
            assert not getattr(apps, 'models_module', None)
            apps.models_module = True
            create_permissions(apps, verbosity=0)
            apps.models_module = None
            return make_permissions(
                apps, schema_editor, with_create_permissions=False)
        else:
            raise

    edit_group = Group.objects.using(db_alias).create(name='edit')
    edit_group.permissions.add(read_perm, write_perm, delete_perm)

    read_group = Group.objects.using(db_alias).create(name='read')
    read_group.permissions.add(read_perm)

    admin_user = User.objects.using(db_alias).get(username='admin')
    admin_user.groups.add(edit_group)
    admin_user.groups.add(read_group)

    anonymous_user = User.objects.using(db_alias).get(username='anonymous')
    anonymous_user.groups.add(read_group)

class Migration(migrations.Migration):

    dependencies = []

    initial = True

    operations = [
        CreateExtension(name='uuid-ossp'),

        migrations.RunSQL(get_sql_string_from_file(os.path.join(settings.ROOT_DIR, 'db', 'install', 'dependencies', 'postgis_backward_compatibility.sql')), ''),

        CreateFunction(
           name='insert_relation',
           arguments=[
               'p_label text',
               'p_relationtype text',
               'p_legacyid2 text'
           ],
           declarations=[
               'v_conceptidfrom uuid = null;',
               'v_conceptidto uuid = null;'
           ],
           language='plpgsql',
           body='''
               v_conceptidfrom =
                    (select conceptid from concepts c
                    where trim(legacyoid) = trim(p_legacyid1));

                v_conceptidto = (select conceptid from concepts c
                    where trim(legacyoid) = trim(p_legacyid2));

                IF v_conceptidfrom is not null and v_conceptidto is not null and
                   v_conceptidto <> v_conceptidfrom and
                   v_conceptidfrom::text||v_conceptidto::text NOT IN (SELECT conceptidfrom::text||conceptidto::text FROM relations) then
                            INSERT INTO relations(relationid, conceptidfrom, conceptidto, relationtype) VALUES (uuid_generate_v1mc(), v_conceptidfrom, v_conceptidto, p_relationtype);
                            return 'success!';

                ELSE return 'fail! no relation inserted.';

                END IF;
           ''',
           returntype='text'
       ),

        CreateFunction(
           name='get_conceptid',
           arguments=[
               'p_label text'
           ],
           declarations=[
               'v_return text;',
           ],
           language='plpgsql',
           body='''
               v_return =
                    (select a.conceptid from concepts a, values b
                    where 1=1 and
                    b.valuetype = 'prefLabel' and
                    b.value = p_label and
                    b.conceptid = a.conceptid LIMIT 1);

                    return v_return;
           ''',
           returntype='uuid'
       ),

        CreateFunction(
           name='insert_concept',
           arguments=[
               'p_label text',
               'p_note text',
               'p_languageid text',
               'p_legacyid text',
               'p_nodetype text'
           ],
           declarations=[
               'v_conceptid uuid = public.uuid_generate_v1mc();',
               'v_valueid uuid = public.uuid_generate_v1mc();',
               'v_languageid text = p_languageid;',
           ],
           language='plpgsql',
           body='''
               INSERT INTO concepts(conceptid, nodetype, legacyoid) VALUES (v_conceptid, p_nodetype, p_legacyid);

               IF trim(p_label) is not null and p_label<>'' then
                 INSERT INTO values (valueid, conceptid, valuetype, value, languageid)
                 VALUES (v_valueid, v_conceptid, 'prefLabel', trim(initcap(p_label)), v_languageid);
               END IF;

               IF trim(p_note) is not null and p_note <> '' then
                 INSERT INTO values (valueid, conceptid, valuetype, value, languageid)
                 VALUES (v_valueid, v_conceptid, 'scopeNote', p_note, v_languageid);
               END IF;

               return v_conceptid;
           ''',
           returntype='uuid'
       ),

        migrations.CreateModel(
            name='Address',
            fields=[
                ('addressnum', models.TextField(null=True, blank=True)),
                ('addressstreet', models.TextField(null=True, blank=True)),
                ('vintage', models.TextField(null=True, blank=True)),
                ('city', models.TextField(null=True, blank=True)),
                ('postalcode', models.TextField(null=True, blank=True)),
                ('addressesid', models.AutoField(serialize=False, primary_key=True)),
                ('geometry', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
            ],
            options={
                'db_table': 'addresses',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='GraphModel',
            fields=[
                ('graphid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('name', models.TextField(null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('deploymentfile', models.TextField(null=True, blank=True)),
                ('author', models.TextField(null=True, blank=True)),
                ('deploymentdate', models.DateTimeField(null=True, blank=True)),
                ('version', models.TextField(null=True, blank=True)),
                ('isresource', models.BooleanField()),
                ('isactive', models.BooleanField()),
                ('iconclass', models.TextField(null=True, blank=True)),
                ('mapfeaturecolor', models.TextField(blank=True, null=True)),
                ('maplinewidth', models.IntegerField(blank=True, null=True)),
                ('mappointsize', models.IntegerField(blank=True, null=True)),
                ('subtitle', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'graphs',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Graph',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('models.GraphModel',),
        ),
        migrations.CreateModel(
            name='CardModel',
            fields=[
                ('cardid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('name', models.TextField(null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('instructions', models.TextField(null=True, blank=True)),
                ('helpenabled', models.BooleanField(default=False)),
                ('helptitle', models.TextField(null=True, blank=True)),
                ('helptext', models.TextField(null=True, blank=True)),
                ('active', models.BooleanField(default=True)),
                ('visible', models.BooleanField(default=True)),
                ('sortorder', models.IntegerField(blank=True, null=True, default=None)),
                ('itemtext', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'cards',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('models.CardModel',),
        ),
        migrations.CreateModel(
            name='CardXNodeXWidget',
            fields=[
                ('card', models.ForeignKey(to='models.CardModel', db_column='cardid')),
                ('id', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('config', django.contrib.postgres.fields.jsonb.JSONField(blank=True, db_column='config', null=True)),
                ('label', models.TextField(blank=True, null=True)),
                ('sortorder', models.IntegerField(blank=True, null=True, default=None)),
            ],
            options={
                'db_table': 'cards_x_nodes_x_widgets',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Concept',
            fields=[
                ('conceptid', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('legacyoid', models.TextField(unique=True)),
            ],
            options={
                'db_table': 'concepts',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DDataType',
            fields=[
                ('datatype', models.TextField(primary_key=True, serialize=False)),
                ('iconclass', models.TextField()),
                ('defaultconfig', django.contrib.postgres.fields.jsonb.JSONField(blank=True, db_column='defaultconfig', null=True)),
                ('configcomponent', models.TextField(blank=True, null=True)),
                ('configname', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'd_data_types',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DLanguage',
            fields=[
                ('languageid', models.TextField(primary_key=True, serialize=False)),
                ('languagename', models.TextField()),
                ('isdefault', models.BooleanField()),
            ],
            options={
                'db_table': 'd_languages',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DNodeType',
            fields=[
                ('nodetype', models.TextField(primary_key=True, serialize=False)),
                ('namespace', models.TextField()),
            ],
            options={
                'db_table': 'd_node_types',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DRelationType',
            fields=[
                ('relationtype', models.TextField(primary_key=True, serialize=False)),
                ('category', models.TextField()),
                ('namespace', models.TextField()),
            ],
            options={
                'db_table': 'd_relation_types',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DValueType',
            fields=[
                ('valuetype', models.TextField(primary_key=True, serialize=False)),
                ('category', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('namespace', models.TextField()),
                ('datatype', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'd_value_types',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Edge',
            fields=[
                ('edgeid', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('ontologyproperty', models.TextField(blank=True, null=True)),
                ('graph', models.ForeignKey(blank=False, db_column='graphid', null=False, to='models.GraphModel')),
            ],
            options={
                'db_table': 'edges',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='EditLog',
            fields=[
                ('editlogid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('resourceclassid', models.TextField(null=True, blank=True)),
                ('resourceinstanceid', models.TextField(null=True, blank=True)),
                ('attributenodeid', models.TextField(null=True, blank=True)),
                ('tileinstanceid', models.TextField(null=True, blank=True)),
                ('edittype', models.TextField(null=True, blank=True)),
                ('newvalue', models.TextField(null=True, blank=True)),
                ('oldvalue', models.TextField(null=True, blank=True)),
                ('timestamp', models.DateTimeField(null=True, blank=True)),
                ('userid', models.TextField(null=True, blank=True)),
                ('user_firstname', models.TextField(null=True, blank=True)),
                ('user_lastname', models.TextField(null=True, blank=True)),
                ('user_email', models.TextField(null=True, blank=True)),
                ('note', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'edit_log',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Form',
            fields=[
                ('formid', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('title', models.TextField(blank=True, null=True)),
                ('subtitle', models.TextField(blank=True, null=True)),
                ('iconclass', models.TextField(blank=True, null=True)),
                ('status', models.BooleanField(default=True)),
                ('visible', models.BooleanField(default=True)),
                ('sortorder', models.IntegerField(blank=True, null=True, default=None)),
            ],
            options={
                'db_table': 'forms',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='FormXCard',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=True)),
                ('card', models.ForeignKey(to='models.CardModel', db_column='cardid')),
                ('form', models.ForeignKey(to='models.Form', db_column='formid')),
                ('sortorder', models.IntegerField(blank=True, null=True, default=None)),
            ],
            options={
                'db_table': 'forms_x_cards',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Function',
            fields=[
                ('functionid', models.UUIDField(primary_key=True, default=uuid.uuid1, serialize=False)),
                ('function', models.TextField(blank=True, null=True)),
                ('functiontype', models.TextField(blank=True, null=True)),
                ('name', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),

                ],
            options={
                'db_table': 'functions',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Icon',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=True)),
                ('name', models.TextField(blank=True, null=True)),
                ('cssclass', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'icons',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('nodeid', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('description', models.TextField(blank=True, null=True)),
                ('istopnode', models.BooleanField()),
                ('ontologyclass', models.TextField(blank=True, null=True)),
                ('datatype', models.TextField()),
                ('graph', models.ForeignKey(blank=False, db_column='graphid', null=False, to='models.GraphModel')),
                ('config', django.contrib.postgres.fields.jsonb.JSONField(blank=True, db_column='config', null=True)),
            ],
            options={
                'db_table': 'nodes',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='NodeGroup',
            fields=[
                ('nodegroupid', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('legacygroupid', models.TextField(blank=True, null=True)),
                ('cardinality', models.TextField(blank=True, default='1')),
                ('parentnodegroup', models.ForeignKey(blank=True, db_column='parentnodegroupid', null=True, to='models.NodeGroup')),
            ],
            options={
                'db_table': 'node_groups',
                'managed': True,
                'default_permissions': (),
                'permissions': (
                    ('read_nodegroup', 'Read'),
                    ('write_nodegroup', 'Create/Update'),
                    ('delete_nodegroup', 'Delete'),
                    ('no_access_to_nodegroup', 'No Access'),
                )
            },
        ),
        migrations.CreateModel(
            name='Ontology',
            fields=[
                ('ontologyid', models.UUIDField(default=uuid.uuid1, primary_key=True)),
                ('name', models.TextField()),
                ('version', models.TextField()),
                ('path', models.FileField(storage=get_ontology_storage_system())),
                ('parentontology', models.ForeignKey(to='models.Ontology', db_column='parentontologyid', related_name='extensions', null=True, blank=True)),
            ],
            options={
                'db_table': 'ontologies',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='OntologyClass',
            fields=[
                ('ontologyclassid', models.UUIDField(default=uuid.uuid1, primary_key=True)),
                ('source', models.TextField()),
                ('target', JSONField(null=True)),
                ('ontology', models.ForeignKey(to='models.Ontology', db_column='ontologyid', related_name='ontologyclasses')),
            ],
            options={
                'db_table': 'ontologyclasses',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Overlay',
            fields=[
                ('overlaytyp', models.TextField(null=True, blank=True)),
                ('overlayval', models.TextField(null=True, blank=True)),
                ('overlayid', models.AutoField(serialize=False, primary_key=True)),
                ('geometry', django.contrib.gis.db.models.fields.PolygonField(srid=4326, null=True, blank=True)),
            ],
            options={
                'db_table': 'overlays',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Parcel',
            fields=[
                ('parcelapn', models.TextField(null=True, blank=True)),
                ('vintage', models.TextField(null=True, blank=True)),
                ('parcelsid', models.AutoField(serialize=False, primary_key=True)),
                ('geometry', django.contrib.gis.db.models.fields.PolygonField(srid=4326, null=True, blank=True)),
            ],
            options={
                'db_table': 'parcels',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('relationid', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('conceptfrom', models.ForeignKey(db_column='conceptidfrom', related_name='relation_concepts_from', to='models.Concept')),
                ('conceptto', models.ForeignKey(db_column='conceptidto', related_name='relation_concepts_to', to='models.Concept')),
                ('relationtype', models.ForeignKey(db_column='relationtype', to='models.DRelationType')),
            ],
            options={
                'db_table': 'relations',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ReportTemplate',
            fields=[
                ('templateid', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('name', models.TextField(null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('component', models.TextField()),
                ('componentname', models.TextField()),
                ('defaultconfig', django.contrib.postgres.fields.jsonb.JSONField(blank=True, db_column='defaultconfig', null=True)),
            ],
            options={
                'db_table': 'report_templates',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('reportid', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('name', models.TextField(null=True, blank=True)),
                ('template', models.ForeignKey(db_column='templateid', to='models.ReportTemplate')),
                ('graph', models.ForeignKey(db_column='graphid', to='models.GraphModel')),
                ('config', django.contrib.postgres.fields.jsonb.JSONField(blank=True, db_column='config', null=True)),
                ('formsconfig', django.contrib.postgres.fields.jsonb.JSONField(blank=True, db_column='formsconfig', null=True)),
                ('active', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'reports',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Resource2ResourceConstraint',
            fields=[
                ('resource2resourceid', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('resourceclassfrom', models.ForeignKey(blank=True, db_column='resourceclassfrom', null=True, related_name='resxres_contstraint_classes_from', to='models.Node')),
                ('resourceclassto', models.ForeignKey(blank=True, db_column='resourceclassto', null=True, related_name='resxres_contstraint_classes_to', to='models.Node')),
            ],
            options={
                'db_table': 'resource_2_resource_constraints',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ResourceInstance',
            fields=[
                ('resourceinstanceid', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('resourceinstancesecurity', models.TextField(blank=True, null=True)),
                ('graph', models.ForeignKey(db_column='graphid', to='models.GraphModel')),
            ],
            options={
                'db_table': 'resource_instances',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ResourceXResource',
            fields=[
                ('resourcexid', models.AutoField(primary_key=True, serialize=False)),
                ('notes', models.TextField(blank=True, null=True)),
                ('datestarted', models.DateField(blank=True, null=True)),
                ('dateended', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'resource_x_resource',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Tile',
            fields=[
                ('tileid', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, db_column='tiledata', null=True)),
                ('nodegroup', models.ForeignKey(db_column='nodegroupid', to='models.NodeGroup')),
                ('parenttile', models.ForeignKey(blank=True, db_column='parenttileid', null=True, to='models.Tile')),
                ('resourceinstance', models.ForeignKey(db_column='resourceinstanceid', to='models.ResourceInstance')),
            ],
            options={
                'db_table': 'tiles',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Value',
            fields=[
                ('valueid', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('value', models.TextField()),
                ('concept', models.ForeignKey(db_column='conceptid', to='models.Concept')),
                ('language', models.ForeignKey(blank=True, db_column='languageid', null=True, to='models.DLanguage')),
                ('valuetype', models.ForeignKey(db_column='valuetype', to='models.DValueType')),
            ],
            options={
                'db_table': 'values',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Widget',
            fields=[
                ('widgetid', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('component', models.TextField()),
                ('defaultconfig', django.contrib.postgres.fields.jsonb.JSONField(blank=True, db_column='defaultconfig', null=True)),
                ('helptext', models.TextField(blank=True, null=True)),
                ('datatype', models.TextField()),
            ],
            options={
                'db_table': 'widgets',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='MapLayers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('layerdefinitions', django.contrib.postgres.fields.jsonb.JSONField(blank=True, db_column='layerdefinitions', null=True)),
                ('isoverlay', models.BooleanField(default=False)),
                ('sortorder', models.IntegerField(default=1)),
                ('icon', models.TextField(default=None)),
            ],
            options={
                'db_table': 'map_layers',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='MapSources',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('source', django.contrib.postgres.fields.jsonb.JSONField(blank=True, db_column='source', null=True)),
            ],
            options={
                'db_table': 'map_sources',
                'managed': True,
            },
        ),
        # migrations.AlterField(
        #     model_name='edge',
        #     name='graph',
        #     field=models.ForeignKey(blank=True, db_column='graphid', null=True, on_delete=django.db.models.deletion.CASCADE, to='models.GraphModel'),
        # ),
        # migrations.AlterField(
        #     model_name='form',
        #     name='graph',
        #     field=models.ForeignKey(db_column='graphid', on_delete=django.db.models.deletion.CASCADE, to='models.GraphModel'),
        # ),
        # migrations.AlterField(
        #     model_name='node',
        #     name='graph',
        #     field=models.ForeignKey(blank=True, db_column='graphid', null=True, on_delete=django.db.models.deletion.CASCADE, to='models.GraphModel'),
        # ),
        migrations.AddField(
            model_name='ddatatype',
            name='defaultwidget',
            field=models.ForeignKey(db_column='defaultwidget', to='models.Widget', null=True),
        ),
        migrations.AddField(
            model_name='resourcexresource',
            name='relationshiptype',
            field=models.ForeignKey(db_column='relationshiptype', to='models.Value'),
        ),
        migrations.AddField(
            model_name='resourcexresource',
            name='resourceinstanceidfrom',
            field=models.ForeignKey(blank=True, db_column='resourceinstanceidfrom', null=True, related_name='resxres_resource_instance_ids_from', to='models.ResourceInstance'),
        ),
        migrations.AddField(
            model_name='resourcexresource',
            name='resourceinstanceidto',
            field=models.ForeignKey(blank=True, db_column='resourceinstanceidto', null=True, related_name='resxres_resource_instance_ids_to', to='models.ResourceInstance'),
        ),
        migrations.AddField(
            model_name='node',
            name='nodegroup',
            field=models.ForeignKey(blank=True, db_column='nodegroupid', null=True, to='models.NodeGroup'),
        ),
        migrations.AddField(
            model_name='edge',
            name='domainnode',
            field=models.ForeignKey(db_column='domainnodeid', related_name='edge_domains', to='models.Node'),
        ),
        migrations.AddField(
            model_name='edge',
            name='rangenode',
            field=models.ForeignKey(db_column='rangenodeid', related_name='edge_ranges', to='models.Node'),
        ),
        migrations.AddField(
            model_name='concept',
            name='nodetype',
            field=models.ForeignKey(db_column='nodetype', to='models.DNodeType'),
        ),
        migrations.AddField(
            model_name='cardxnodexwidget',
            name='node',
            field=models.ForeignKey(db_column='nodeid', to='models.Node'),
        ),
        migrations.AddField(
            model_name='cardxnodexwidget',
            name='widget',
            field=models.ForeignKey(db_column='widgetid', to='models.Widget'),
        ),
        migrations.AddField(
            model_name='cardmodel',
            name='nodegroup',
            field=models.ForeignKey(db_column='nodegroupid', to='models.NodeGroup'),
        ),
        migrations.AddField(
            model_name='cardmodel',
            name='graph',
            field=models.ForeignKey(db_column='graphid', to='models.GraphModel'),
        ),
        migrations.AddField(
            model_name='node',
            name='functions',
            field=models.ManyToManyField(to='models.Function', db_table='functions_x_nodes'),
        ),
        migrations.AddField(
            model_name='ddatatype',
            name='functions',
            field=models.ManyToManyField(to='models.Function', db_table='functions_x_datatypes'),
        ),
        migrations.AddField(
            model_name='cardmodel',
            name='functions',
            field=models.ManyToManyField(to='models.Function', db_table='functions_x_cards'),
        ),
        migrations.AddField(
            model_name='cardxnodexwidget',
            name='functions',
            field=models.ManyToManyField(to='models.Function', db_table='functions_x_widgets'),
        ),
        migrations.AddField(
            model_name='form',
            name='graph',
            field=models.ForeignKey(to='models.GraphModel', db_column='graphid', related_name='forms', null=False, blank=False),
        ),
        migrations.AddField(
            model_name='graphmodel',
            name='ontology',
            field=models.ForeignKey(to='models.Ontology', db_column='ontologyid', related_name='graphs', null=True, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='edge',
            unique_together=set([('rangenode', 'domainnode')]),
        ),
        migrations.AlterUniqueTogether(
            name='cardxnodexwidget',
            unique_together=set([('node', 'card', 'widget')]),
        ),
        migrations.AlterUniqueTogether(
            name='ontologyclass',
            unique_together=set([('source', 'ontology')]),
        ),

        CreateAutoPopulateUUIDField('graphs', ['graphid']),
        CreateAutoPopulateUUIDField('cards', ['cardid']),
        CreateAutoPopulateUUIDField('concepts', ['conceptid']),
        CreateAutoPopulateUUIDField('edges', ['edgeid']),
        CreateAutoPopulateUUIDField('edit_log', ['editlogid']),
        CreateAutoPopulateUUIDField('forms', ['formid']),
        CreateAutoPopulateUUIDField('node_groups', ['nodegroupid']),
        CreateAutoPopulateUUIDField('nodes', ['nodeid']),
        CreateAutoPopulateUUIDField('relations', ['relationid']),
        CreateAutoPopulateUUIDField('resource_2_resource_constraints', ['resource2resourceid']),
        CreateAutoPopulateUUIDField('resource_instances', ['resourceinstanceid']),
        CreateAutoPopulateUUIDField('tiles', ['tileid']),
        CreateAutoPopulateUUIDField('values', ['valueid']),
        CreateAutoPopulateUUIDField('widgets', ['widgetid']),

        migrations.RunSQL(
                """
                ALTER TABLE nodes ADD CONSTRAINT nodes_ddatatypes_fk FOREIGN KEY (datatype)
                REFERENCES public.d_data_types (datatype) MATCH SIMPLE
                """
                ),
        migrations.RunSQL(get_sql_string_from_file(os.path.join(settings.ROOT_DIR, 'db', 'dml', 'db_data.sql')), ''),
        migrations.RunPython(forwards_func, reverse_func),
        migrations.RunPython(make_permissions,reverse_code=lambda *args,**kwargs: True),
    ]
