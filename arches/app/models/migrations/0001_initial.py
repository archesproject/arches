# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.conf import settings
from django.db import migrations, models
from django.contrib.postgres.fields import JSONField
import uuid
import django.contrib.gis.db.models.fields
from arches.db.migration_operations.extras import CreateExtension, CreateAutoPopulateUUIDField, CreateFunction

def get_sql_string_from_file(pathtofile):
    ret = []
    with open(pathtofile) as f:
        ret = f.read()
        #print sqlparse.split(sqlparse.format(ret,strip_comments=True))
        # for stmt in sqlparse.split(sqlparse.format(f.read(),strip_comments=True)):
        #     if stmt.strip() != '':
        #         ret.append(stmt)
    return ret

def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version

    Group = apps.get_model("auth", "Group")
    User = apps.get_model("auth", "User")
    db_alias = schema_editor.connection.alias

    edit_group = Group.objects.using(db_alias).create(name='edit')
    read_group = Group.objects.using(db_alias).create(name='read')

    admin_user = User.objects.using(db_alias).get(username='admin')
    admin_user.groups.add(edit_group)
    admin_user.groups.add(read_group)

    anonymous_user = User.objects.using(db_alias).get(username='anonymous')
    anonymous_user.groups.add(read_group)

def reverse_func(apps, schema_editor):
    # forwards_func() creates two Country instances,
    # so reverse_func() should delete them.
    pass
    # Country = apps.get_model("myapp", "Country")
    # db_alias = schema_editor.connection.alias
    # Country.objects.using(db_alias).filter(name="USA", code="us").delete()
    # Country.objects.using(db_alias).filter(name="France", code="fr").delete()

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
            name='GraphMetadata',
            fields=[
                ('graphmetadataid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('name', models.TextField(null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('deploymentfile', models.TextField(null=True, blank=True)),
                ('author', models.TextField(null=True, blank=True)),
                ('deploymentdate', models.DateTimeField(null=True, blank=True)),
                ('version', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'graph_metadata',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('cardid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('name', models.TextField()),
                ('title', models.TextField()),
                ('subtitle', models.TextField(null=True, blank=True)),
                ('helptext', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'cards',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='CardXNodeXWidget',
            fields=[
                ('card', models.ForeignKey(to='models.Card', db_column='cardid')),
                ('id', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('inputmask', models.TextField(blank=True, null=True)),
                ('inputlabel', models.TextField(blank=True, null=True)),
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
                ('graphmetadata', models.ForeignKey(blank=True, db_column='graphmetadataid', null=True, to='models.GraphMetadata')),
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
            ],
            options={
                'db_table': 'forms',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='FormXCard',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('card', models.ForeignKey(db_column='cardid', to='models.Card')),
                ('form', models.ForeignKey(db_column='formid', to='models.Form')),
            ],
            options={
                'db_table': 'forms_x_card',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Function',
            fields=[
                ('functionid', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('functiontype', models.TextField(blank=True, null=True)),
                ('function', models.TextField()),
                ('name', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'functions',
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
                ('isresource', models.BooleanField()),
                ('isactive', models.BooleanField()),
                ('ontologyclass', models.TextField()),
                ('datatype', models.TextField()),
                ('graphmetadata', models.ForeignKey(blank=True, db_column='graphmetadataid', null=True, to='models.GraphMetadata')),
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
                ('cardinality', models.TextField(blank=True, default='n')),
                ('legacygroupid', models.TextField(blank=True, null=True)),
                ('parentnodegroup', models.ForeignKey(blank=True, db_column='parentnodegroupid', null=True, to='models.NodeGroup')),
            ],
            options={
                'db_table': 'node_groups',
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
            name='Resource2ResourceConstraint',
            fields=[
                ('resource2resourceid', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('cardinality', models.TextField(blank=True, null=True)),
                ('resourceclassfrom', models.ForeignKey(blank=True, db_column='resourceclassfrom', null=True, related_name='resxres_contstraint_classes_from', to='models.Node')),
                ('resourceclassto', models.ForeignKey(blank=True, db_column='resourceclassto', null=True, related_name='resxres_contstraint_classes_to', to='models.Node')),
            ],
            options={
                'db_table': 'resource_2_resource_constraints',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ResourceClassXForm',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('status', models.TextField(blank=True, null=True)),
                ('form', models.ForeignKey(db_column='formid', to='models.Form')),
                ('resourceclass', models.ForeignKey(blank=True, db_column='resourceclassid', null=True, to='models.Node')),
            ],
            options={
                'db_table': 'resource_classes_x_forms',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ResourceInstance',
            fields=[
                ('resourceinstanceid', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('resourceinstancesecurity', models.TextField(blank=True, null=True)),
                ('resourceclass', models.ForeignKey(db_column='resourceclassid', to='models.Node')),
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
            name='Validation',
            fields=[
                ('validationid', models.UUIDField(primary_key=True, default=uuid.uuid1, serialize=False)),
                ('validation', models.TextField(blank=True, null=True)),
                ('validationtype', models.TextField(blank=True, null=True)),
                ('name', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'validations',
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
                ('template', models.FileField(storage=django.core.files.storage.FileSystemStorage(location='app/templates/views/forms/widgets/'), upload_to=b'')),
                ('defaultlabel', models.TextField(blank=True, null=True)),
                ('defaultmask', models.TextField(blank=True, null=True)),
                ('helptext', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'widgets',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='WidgetXDataType',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False)),
                ('widget', models.ForeignKey(db_column='widgetid', to='models.Widget')),
                ('datatype', models.ForeignKey(db_column='datatypeid', to='models.DDataType')),
            ],
            options={
                'db_table': 'widgets_x_datatypes',
                'managed': True,
            },
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
            name='function',
            field=models.ForeignKey(db_column='functionid', to='models.Function'),
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
            model_name='card',
            name='nodegroup',
            field=models.ForeignKey(blank=True, db_column='nodegroupid', null=True, to='models.NodeGroup'),
        ),
        migrations.AddField(
            model_name='card',
            name='parentcard',
            field=models.ForeignKey(blank=True, db_column='parentcardid', null=True, to='models.Card'),
        ),
        migrations.AddField(
            model_name='node',
            name='validations',
            field=models.ManyToManyField(to='models.Validation', db_table='validations_x_nodes'),
        ),
        migrations.AlterUniqueTogether(
            name='resourceclassxform',
            unique_together=set([('resourceclass', 'form')]),
        ),
        migrations.AlterUniqueTogether(
            name='formxcard',
            unique_together=set([('form', 'card')]),
        ),
        migrations.AlterUniqueTogether(
            name='edge',
            unique_together=set([('rangenode', 'domainnode')]),
        ),
        migrations.AlterUniqueTogether(
            name='cardxnodexwidget',
            unique_together=set([('node', 'card', 'widget')]),
        ),

        CreateAutoPopulateUUIDField('graph_metadata', ['graphmetadataid']),
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

        migrations.RunSQL(get_sql_string_from_file(os.path.join(settings.ROOT_DIR, 'db', 'dml', 'db_data.sql')), ''),
        migrations.RunPython(forwards_func, reverse_func),
    ]
