# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.conf import settings
from django.db import migrations, models
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
            name='Addresses',
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
            name='Branchmetadata',
            fields=[
                ('branchmetadataid', models.UUIDField(default=uuid.uuid1, serialize=False, editable=False, primary_key=True)),
                ('name', models.BigIntegerField(null=True, blank=True)),
                ('deploymentfile', models.TextField(null=True, blank=True)),
                ('author', models.TextField(null=True, blank=True)),
                ('deploymentdate', models.DateTimeField(null=True, blank=True)),
                ('version', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'branchmetadata',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Cardgroups',
            fields=[
                ('cardgroupid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('name', models.TextField()),
                ('title', models.TextField()),
                ('subtitle', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'cardgroups',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Cards',
            fields=[
                ('cardid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('name', models.TextField()),
                ('htmltemplate', models.TextField()),
                ('title', models.TextField()),
                ('subtitle', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'cards',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='CardsXCardgroups',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cardgroupid', models.ForeignKey(to='models.Cardgroups', db_column='cardgroupid')),
                ('cardid', models.ForeignKey(to='models.Cards', db_column='cardid')),
            ],
            options={
                'db_table': 'cards_x_cardgroups',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='CardsXNodesXWidgets',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cardid', models.ForeignKey(to='models.Cards', db_column='cardid')),
            ],
            options={
                'db_table': 'cards_x_nodes_x_widgets',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Classes',
            fields=[
                ('classid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('classname', models.TextField()),
                ('isactive', models.BooleanField()),
            ],
            options={
                'db_table': 'classes',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Concepts',
            fields=[
                ('conceptid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('legacyoid', models.TextField(unique=True)),
            ],
            options={
                'db_table': 'concepts',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DLanguages',
            fields=[
                ('languageid', models.TextField(serialize=False, primary_key=True)),
                ('languagename', models.TextField()),
                ('isdefault', models.BooleanField()),
            ],
            options={
                'db_table': 'd_languages',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DNodetypes',
            fields=[
                ('nodetype', models.TextField(serialize=False, primary_key=True)),
                ('namespace', models.TextField()),
            ],
            options={
                'db_table': 'd_nodetypes',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DRelationtypes',
            fields=[
                ('relationtype', models.TextField(serialize=False, primary_key=True)),
                ('category', models.TextField()),
                ('namespace', models.TextField()),
            ],
            options={
                'db_table': 'd_relationtypes',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='DValuetypes',
            fields=[
                ('valuetype', models.TextField(serialize=False, primary_key=True)),
                ('category', models.TextField(null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('namespace', models.TextField()),
                ('datatype', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'd_valuetypes',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Edges',
            fields=[
                ('edgeid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('name', models.TextField()),
                ('description', models.TextField()),
                ('crmproperty', models.TextField()),
                ('branchmetadataid', models.ForeignKey(db_column='branchmetadataid', blank=True, to='models.Branchmetadata', null=True)),
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
            name='Forms',
            fields=[
                ('formid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('name', models.TextField()),
                ('title', models.TextField(null=True, blank=True)),
                ('subtitle', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'forms',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='FormsXCardGroups',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cardgroupid', models.ForeignKey(to='models.Cardgroups', db_column='cardgroupid')),
                ('formid', models.ForeignKey(to='models.Forms', db_column='formid')),
            ],
            options={
                'db_table': 'forms_x_card_groups',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Nodegroups',
            fields=[
                ('nodegroupid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('cardinality', models.TextField()),
                ('legacygroupid', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'nodegroups',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Nodes',
            fields=[
                ('nodeid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('name', models.TextField()),
                ('description', models.TextField()),
                ('istopnode', models.BooleanField()),
                ('crmclass', models.TextField()),
                ('datatype', models.TextField()),
                ('validation', models.TextField(null=True, blank=True)),
                ('inputlabel', models.TextField(null=True, blank=True)),
                ('inputmask', models.TextField(null=True, blank=True)),
                ('status', models.BigIntegerField(null=True, blank=True)),
                ('branchmetadataid', models.ForeignKey(db_column='branchmetadataid', blank=True, to='models.Branchmetadata', null=True)),
                ('nodegroupid', models.ForeignKey(db_column='nodegroupid', blank=True, to='models.Nodegroups', null=True)),
            ],
            options={
                'db_table': 'nodes',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Overlays',
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
            name='Parcels',
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
            name='Properties',
            fields=[
                ('propertyid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('propertydisplay', models.TextField(null=True, blank=True)),
                ('classdomain', models.ForeignKey(related_name='property_classdomains', db_column='classdomain', to='models.Classes')),
                ('classrange', models.ForeignKey(related_name='property_classranges', db_column='classrange', to='models.Classes')),
            ],
            options={
                'db_table': 'properties',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Relations',
            fields=[
                ('relationid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('conceptidfrom', models.ForeignKey(related_name='relation_concepts_from', db_column='conceptidfrom', to='models.Concepts')),
                ('conceptidto', models.ForeignKey(related_name='relation_concepts_to', db_column='conceptidto', to='models.Concepts')),
                ('relationtype', models.ForeignKey(to='models.DRelationtypes', db_column='relationtype')),
            ],
            options={
                'db_table': 'relations',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Resource2ResourceConstraints',
            fields=[
                ('resource2resourceid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('cardinality', models.TextField(null=True, blank=True)),
                ('resourceclassfrom', models.ForeignKey(related_name='resxres_contstraint_classes_from', db_column='resourceclassfrom', blank=True, to='models.Nodes', null=True)),
                ('resourceclassto', models.ForeignKey(related_name='resxres_contstraint_classes_to', db_column='resourceclassto', blank=True, to='models.Nodes', null=True)),
            ],
            options={
                'db_table': 'resource2resource_constraints',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ResourceclassesXForms',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('formid', models.ForeignKey(to='models.Forms', db_column='formid')),
                ('resourceclassid', models.ForeignKey(db_column='resourceclassid', blank=True, to='models.Nodes', null=True)),
            ],
            options={
                'db_table': 'resourceclasses_x_forms',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Resourceinstances',
            fields=[
                ('resourceinstanceid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('col1', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'resourceinstances',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ResourceXResource',
            fields=[
                ('resourcexid', models.AutoField(serialize=False, primary_key=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('datestarted', models.DateField(null=True, blank=True)),
                ('dateended', models.DateField(null=True, blank=True)),
            ],
            options={
                'db_table': 'resource_x_resource',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Tileinstances',
            fields=[
                ('tileinstanceid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('tilegroupid', models.TextField()),
                ('tileinstancedata', models.TextField(null=True, blank=True)),
                ('cardid', models.ForeignKey(to='models.Cards', db_column='cardid')),
                ('parenttileinstanceid', models.ForeignKey(db_column='parenttileinstanceid', blank=True, to='models.Tileinstances', null=True)),
                ('resourceclassid', models.ForeignKey(to='models.Nodes', db_column='resourceclassid')),
                ('resourceinstanceid', models.ForeignKey(to='models.Resourceinstances', db_column='resourceinstanceid')),
            ],
            options={
                'db_table': 'tileinstances',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Values',
            fields=[
                ('valueid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('value', models.TextField()),
                ('conceptid', models.ForeignKey(to='models.Concepts', db_column='conceptid')),
                ('languageid', models.ForeignKey(db_column='languageid', blank=True, to='models.DLanguages', null=True)),
                ('valuetype', models.ForeignKey(to='models.DValuetypes', db_column='valuetype')),
            ],
            options={
                'db_table': 'values',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Widgets',
            fields=[
                ('widgetid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('name', models.TextField()),
                ('defaultlabel', models.TextField(null=True, blank=True)),
                ('defaultmask', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'widgets',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='resourcexresource',
            name='relationshiptype',
            field=models.ForeignKey(to='models.Values', db_column='relationshiptype'),
        ),
        migrations.AddField(
            model_name='resourcexresource',
            name='resourceinstanceidfrom',
            field=models.ForeignKey(related_name='resxres_resource_instance_ids_from', db_column='resourceinstanceidfrom', blank=True, to='models.Resourceinstances', null=True),
        ),
        migrations.AddField(
            model_name='resourcexresource',
            name='resourceinstanceidto',
            field=models.ForeignKey(related_name='resxres_resource_instance_ids_to', db_column='resourceinstanceidto', blank=True, to='models.Resourceinstances', null=True),
        ),
        migrations.AddField(
            model_name='edges',
            name='domainnodeid',
            field=models.ForeignKey(related_name='edge_domains', db_column='domainnodeid', to='models.Nodes'),
        ),
        migrations.AddField(
            model_name='edges',
            name='rangenodeid',
            field=models.ForeignKey(related_name='edge_ranges', db_column='rangenodeid', to='models.Nodes'),
        ),
        migrations.AddField(
            model_name='concepts',
            name='nodetype',
            field=models.ForeignKey(to='models.DNodetypes', db_column='nodetype'),
        ),
        migrations.AddField(
            model_name='cardsxnodesxwidgets',
            name='nodeid',
            field=models.ForeignKey(to='models.Nodes', db_column='nodeid'),
        ),
        migrations.AddField(
            model_name='cardsxnodesxwidgets',
            name='widgetid',
            field=models.ForeignKey(to='models.Widgets', db_column='widgetid'),
        ),
        migrations.AddField(
            model_name='cardgroups',
            name='nodeid',
            field=models.ForeignKey(db_column='nodeid', blank=True, to='models.Nodes', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='resourceclassesxforms',
            unique_together=set([('resourceclassid', 'formid')]),
        ),
        migrations.AlterUniqueTogether(
            name='formsxcardgroups',
            unique_together=set([('formid', 'cardgroupid')]),
        ),
        migrations.AlterUniqueTogether(
            name='edges',
            unique_together=set([('rangenodeid', 'domainnodeid')]),
        ),
        migrations.AlterUniqueTogether(
            name='cardsxnodesxwidgets',
            unique_together=set([('nodeid', 'cardid', 'widgetid')]),
        ),
        migrations.AlterUniqueTogether(
            name='cardsxcardgroups',
            unique_together=set([('cardgroupid', 'cardid')]),
        ),

        CreateAutoPopulateUUIDField('branchmetadata', ['branchmetadataid']),
        CreateAutoPopulateUUIDField('cardgroups', ['cardgroupid']),
        CreateAutoPopulateUUIDField('cards', ['cardid']),
        CreateAutoPopulateUUIDField('classes', ['classid']),
        CreateAutoPopulateUUIDField('concepts', ['conceptid']),
        CreateAutoPopulateUUIDField('edges', ['edgeid']),
        CreateAutoPopulateUUIDField('edit_log', ['editlogid']),
        CreateAutoPopulateUUIDField('forms', ['formid']),
        CreateAutoPopulateUUIDField('nodegroups', ['nodegroupid']),
        CreateAutoPopulateUUIDField('nodes', ['nodeid']),
        CreateAutoPopulateUUIDField('properties', ['propertyid']),
        CreateAutoPopulateUUIDField('relations', ['relationid']),
        CreateAutoPopulateUUIDField('resource2resource_constraints', ['resource2resourceid']),
        CreateAutoPopulateUUIDField('resourceinstances', ['resourceinstanceid']),
        CreateAutoPopulateUUIDField('tileinstances', ['tileinstanceid']),
        CreateAutoPopulateUUIDField('values', ['valueid']),
        CreateAutoPopulateUUIDField('widgets', ['widgetid']),

        migrations.RunSQL(get_sql_string_from_file(os.path.join(settings.ROOT_DIR, 'db', 'dml', 'db_data.sql')), ''),
        migrations.RunPython(forwards_func, reverse_func),
    ]
