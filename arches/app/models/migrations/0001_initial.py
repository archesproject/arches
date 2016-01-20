# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import uuid
import sqlparse
from django.db import migrations, models
from django.conf import settings
import django.contrib.gis.db.models.fields


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

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.RunSQL('CREATE SCHEMA ontology; CREATE SCHEMA data; CREATE SCHEMA concepts; CREATE SCHEMA aux;', 'DROP SCHEMA ontology CASCADE; DROP SCHEMA data CASCADE; DROP SCHEMA concepts CASCADE; DROP SCHEMA aux CASCADE;'),
        migrations.RunSQL(get_sql_string_from_file(os.path.join(settings.ROOT_DIR, 'db', 'install', 'dependencies', 'batch_index.sql')), ''),
        migrations.RunSQL(get_sql_string_from_file(os.path.join(settings.ROOT_DIR, 'db', 'install', 'dependencies', 'isstring.sql')), ''),
        migrations.RunSQL(get_sql_string_from_file(os.path.join(settings.ROOT_DIR, 'db', 'install', 'dependencies', 'postgis_backward_compatibility.sql')), ''),
        migrations.RunSQL(get_sql_string_from_file(os.path.join(settings.ROOT_DIR, 'db', 'install', 'dependencies', 'uuid-ossp.sql')), ''),
        migrations.RunSQL(get_sql_string_from_file(os.path.join(settings.ROOT_DIR, 'db', 'ddl', 'db_ddl_v4.sql')), ''),

        migrations.CreateModel(
            name='FileValues',
            fields=[
                ('valueid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('value', models.FileField(upload_to=b'concepts')),
            ],
            options={
                'db_table': 'concepts"."values',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='VwConcepts',
            fields=[
                ('conceptid', models.TextField(serialize=False, primary_key=True)),
                ('conceptlabel', models.TextField()),
                ('legacyoid', models.TextField()),
            ],
            options={
                'db_table': 'vw_concepts',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='VwEdges',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source', models.TextField()),
                ('label', models.TextField()),
                ('target', models.TextField()),
            ],
            options={
                'db_table': 'vw_edges',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='VwEntitytypeDomains',
            fields=[
                ('id', models.TextField(serialize=False, primary_key=True)),
                ('entitytypeid', models.TextField(blank=True)),
                ('conceptid', models.TextField(blank=True)),
                ('value', models.TextField(blank=True)),
                ('valuetype', models.TextField(blank=True)),
                ('languageid', models.TextField(blank=True)),
                ('sortorder', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'vw_entitytype_domains',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='VwEntityTypes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('entitytypeid', models.TextField()),
                ('entitytypename', models.TextField()),
                ('description', models.TextField()),
                ('languageid', models.TextField()),
                ('reportwidget', models.TextField()),
                ('icon', models.TextField()),
                ('isresource', models.BooleanField()),
                ('conceptid', models.TextField()),
            ],
            options={
                'db_table': 'vw_entity_types',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='VwExportEdges',
            fields=[
                ('source', models.TextField()),
                ('label', models.TextField()),
                ('target', models.TextField(serialize=False, primary_key=True)),
                ('assettype', models.TextField()),
            ],
            options={
                'db_table': 'ontology"."vw_export_edges',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='VwExportNodes',
            fields=[
                ('id', models.TextField(serialize=False, primary_key=True)),
                ('label', models.TextField()),
                ('assettype', models.TextField()),
                ('mergenode', models.TextField()),
                ('businesstablename', models.TextField(null=True)),
            ],
            options={
                'db_table': 'ontology"."vw_export_nodes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='VwNodes',
            fields=[
                ('label', models.TextField()),
                ('id', models.TextField(serialize=False, primary_key=True)),
                ('val', models.TextField()),
            ],
            options={
                'db_table': 'vw_nodes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Addresses',
            fields=[
                ('addressid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('addressnum', models.TextField()),
                ('addressstreet', models.TextField()),
                ('vintage', models.TextField()),
                ('city', models.TextField()),
                ('postalcode', models.TextField()),
                ('geometry', django.contrib.gis.db.models.fields.MultiPointField(srid=4326)),
            ],
            options={
                'db_table': 'aux"."addresses',
            },
        ),
        migrations.CreateModel(
            name='Classes',
            fields=[
                ('classid', models.TextField(serialize=False, primary_key=True)),
                ('classname', models.TextField()),
                ('isactive', models.BooleanField()),
            ],
            options={
                'db_table': 'ontology"."classes',
            },
        ),
        migrations.CreateModel(
            name='ConceptRelations',
            fields=[
                ('relationid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'concepts"."relations',
            },
        ),
        migrations.CreateModel(
            name='Concepts',
            fields=[
                ('conceptid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('legacyoid', models.TextField()),
            ],
            options={
                'db_table': 'concepts"."concepts',
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
                'db_table': 'concepts"."d_languages',
            },
        ),
        migrations.CreateModel(
            name='DNodetypes',
            fields=[
                ('nodetype', models.TextField(serialize=False, primary_key=True)),
                ('namespace', models.TextField()),
            ],
            options={
                'db_table': 'concepts"."d_nodetypes',
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
                'db_table': 'concepts"."d_relationtypes',
            },
        ),
        migrations.CreateModel(
            name='EditLog',
            fields=[
                ('editlogid', models.TextField(serialize=False, primary_key=True)),
                ('resourceentitytypeid', models.TextField(null=True)),
                ('resourceid', models.TextField(null=True)),
                ('attributeentitytypeid', models.TextField(null=True)),
                ('edittype', models.TextField(null=True)),
                ('userid', models.TextField(null=True)),
                ('timestamp', models.DateTimeField()),
                ('oldvalue', models.TextField(null=True)),
                ('newvalue', models.TextField(null=True)),
                ('user_email', models.TextField(null=True)),
                ('user_firstname', models.TextField(null=True)),
                ('user_lastname', models.TextField(null=True)),
                ('note', models.TextField(null=True)),
            ],
            options={
                'db_table': 'data"."edit_log',
            },
        ),
        migrations.CreateModel(
            name='Entities',
            fields=[
                ('entityid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'data"."entities',
            },
        ),
        migrations.CreateModel(
            name='EntityTypes',
            fields=[
                ('businesstablename', models.TextField(null=True)),
                ('publishbydefault', models.BooleanField()),
                ('icon', models.TextField(null=True)),
                ('defaultvectorcolor', models.TextField(null=True)),
                ('entitytypeid', models.TextField(serialize=False, primary_key=True)),
                ('isresource', models.NullBooleanField()),
                ('classid', models.ForeignKey(related_name='entitytypes_classid', db_column=b'classid', to='models.Classes')),
                ('conceptid', models.ForeignKey(related_name='entitytypes_conceptid', db_column=b'conceptid', to='models.Concepts')),
            ],
            options={
                'db_table': 'data"."entity_types',
            },
        ),
        migrations.CreateModel(
            name='Mappings',
            fields=[
                ('mappingid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('mergenodeid', models.TextField()),
                ('entitytypeidfrom', models.ForeignKey(related_name='mappings_entitytypeidfrom', db_column=b'entitytypeidfrom', to='models.EntityTypes')),
                ('entitytypeidto', models.ForeignKey(related_name='mappings_entitytypeidto', db_column=b'entitytypeidto', to='models.EntityTypes')),
            ],
            options={
                'db_table': 'ontology"."mappings',
            },
        ),
        migrations.CreateModel(
            name='MappingSteps',
            fields=[
                ('mappingstepid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('order', models.IntegerField()),
                ('mappingid', models.ForeignKey(to='models.Mappings', db_column=b'mappingid')),
            ],
            options={
                'db_table': 'ontology"."mapping_steps',
            },
        ),
        migrations.CreateModel(
            name='Overlays',
            fields=[
                ('overlayid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('overlayty', models.TextField()),
                ('overlayval', models.TextField()),
                ('geometry', django.contrib.gis.db.models.fields.GeometryField(srid=4326)),
            ],
            options={
                'db_table': 'aux"."overlays',
            },
        ),
        migrations.CreateModel(
            name='Parcels',
            fields=[
                ('parcelid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('parcelapn', models.TextField()),
                ('vintage', models.TextField()),
                ('geometry', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
            options={
                'db_table': 'aux"."parcels',
            },
        ),
        migrations.CreateModel(
            name='Properties',
            fields=[
                ('propertyid', models.TextField(serialize=False, primary_key=True)),
                ('propertydisplay', models.TextField(null=True)),
                ('classdomain', models.ForeignKey(related_name='properties_classdomain', db_column=b'classdomain', to='models.Classes')),
                ('classrange', models.ForeignKey(related_name='properties_classrange', db_column=b'classrange', to='models.Classes')),
            ],
            options={
                'db_table': 'ontology"."properties',
            },
        ),
        migrations.CreateModel(
            name='RelatedResource',
            fields=[
                ('resourcexid', models.AutoField(serialize=False, primary_key=True)),
                ('entityid1', models.TextField()),
                ('entityid2', models.TextField()),
                ('notes', models.TextField()),
                ('relationshiptype', models.TextField()),
                ('datestarted', models.DateField()),
                ('dateended', models.DateField()),
            ],
            options={
                'db_table': 'data"."resource_x_resource',
            },
        ),
        migrations.CreateModel(
            name='Relations',
            fields=[
                ('relationid', models.AutoField(serialize=False, primary_key=True)),
                ('notes', models.TextField()),
            ],
            options={
                'db_table': 'data"."relations',
            },
        ),
        migrations.CreateModel(
            name='Rules',
            fields=[
                ('ruleid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('entitytypedomain', models.ForeignKey(related_name='rules_entitytypedomain', db_column=b'entitytypedomain', to='models.EntityTypes')),
                ('entitytyperange', models.ForeignKey(related_name='rules_entitytyperange', db_column=b'entitytyperange', to='models.EntityTypes')),
                ('propertyid', models.ForeignKey(to='models.Properties', db_column=b'propertyid')),
            ],
            options={
                'db_table': 'ontology"."rules',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('details', models.TextField()),
            ],
            options={
                'db_table': 'user_profile',
            },
        ),
        migrations.CreateModel(
            name='Values',
            fields=[
                ('valueid', models.UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('value', models.TextField()),
                ('conceptid', models.ForeignKey(to='models.Concepts', db_column=b'conceptid')),
                ('languageid', models.ForeignKey(to='models.DLanguages', db_column=b'languageid')),
            ],
            options={
                'db_table': 'concepts"."values',
            },
        ),
        migrations.CreateModel(
            name='ValueTypes',
            fields=[
                ('valuetype', models.TextField(serialize=False, primary_key=True)),
                ('category', models.TextField(null=True)),
                ('description', models.TextField(null=True)),
                ('namespace', models.TextField()),
                ('datatype', models.TextField(null=True)),
            ],
            options={
                'db_table': 'concepts"."d_valuetypes',
            },
        ),
        migrations.CreateModel(
            name='Dates',
            fields=[
                ('entityid', models.OneToOneField(primary_key=True, db_column=b'entityid', serialize=False, to='models.Entities')),
                ('val', models.DateTimeField()),
            ],
            options={
                'db_table': 'data"."dates',
            },
        ),
        migrations.CreateModel(
            name='Domains',
            fields=[
                ('entityid', models.OneToOneField(primary_key=True, db_column=b'entityid', serialize=False, to='models.Entities')),
            ],
            options={
                'db_table': 'data"."domains',
            },
        ),
        migrations.CreateModel(
            name='Files',
            fields=[
                ('entityid', models.OneToOneField(primary_key=True, db_column=b'entityid', serialize=False, to='models.Entities')),
                ('val', models.FileField(upload_to=b'files')),
            ],
            options={
                'db_table': 'data"."files',
            },
        ),
        migrations.CreateModel(
            name='Geometries',
            fields=[
                ('entityid', models.OneToOneField(primary_key=True, db_column=b'entityid', serialize=False, to='models.Entities')),
                ('val', django.contrib.gis.db.models.fields.GeometryField(srid=4326)),
            ],
            options={
                'db_table': 'data"."geometries',
            },
        ),
        migrations.CreateModel(
            name='Numbers',
            fields=[
                ('entityid', models.OneToOneField(primary_key=True, db_column=b'entityid', serialize=False, to='models.Entities')),
                ('val', models.FloatField()),
            ],
            options={
                'db_table': 'data"."numbers',
            },
        ),
        migrations.CreateModel(
            name='Strings',
            fields=[
                ('entityid', models.OneToOneField(primary_key=True, db_column=b'entityid', serialize=False, to='models.Entities')),
                ('val', models.TextField()),
            ],
            options={
                'db_table': 'data"."strings',
            },
        ),
        migrations.AddField(
            model_name='values',
            name='valuetype',
            field=models.ForeignKey(to='models.ValueTypes', db_column=b'valuetype'),
        ),
        migrations.AddField(
            model_name='relations',
            name='entityiddomain',
            field=models.ForeignKey(related_name='rules_entityiddomain', db_column=b'entityiddomain', to='models.Entities'),
        ),
        migrations.AddField(
            model_name='relations',
            name='entityidrange',
            field=models.ForeignKey(related_name='rules_entityidrange', db_column=b'entityidrange', to='models.Entities'),
        ),
        migrations.AddField(
            model_name='relations',
            name='ruleid',
            field=models.ForeignKey(to='models.Rules', db_column=b'ruleid'),
        ),
        migrations.AddField(
            model_name='mappingsteps',
            name='ruleid',
            field=models.ForeignKey(to='models.Rules', db_column=b'ruleid'),
        ),
        migrations.AddField(
            model_name='entities',
            name='entitytypeid',
            field=models.ForeignKey(to='models.EntityTypes', db_column=b'entitytypeid'),
        ),
        migrations.AddField(
            model_name='concepts',
            name='nodetype',
            field=models.ForeignKey(to='models.DNodetypes', db_column=b'nodetype'),
        ),
        migrations.AddField(
            model_name='conceptrelations',
            name='conceptidfrom',
            field=models.ForeignKey(related_name='concept_relation_from', db_column=b'conceptidfrom', to='models.Concepts'),
        ),
        migrations.AddField(
            model_name='conceptrelations',
            name='conceptidto',
            field=models.ForeignKey(related_name='concept_relation_to', db_column=b'conceptidto', to='models.Concepts'),
        ),
        migrations.AddField(
            model_name='conceptrelations',
            name='relationtype',
            field=models.ForeignKey(related_name='concept_relation_type', db_column=b'relationtype', to='models.DRelationtypes'),
        ),
        migrations.AlterUniqueTogether(
            name='mappingsteps',
            unique_together=set([('mappingid', 'ruleid', 'order')]),
        ),
        migrations.AddField(
            model_name='domains',
            name='val',
            field=models.ForeignKey(db_column=b'val', to='models.Values', null=True),
        ),

        migrations.RunSQL(get_sql_string_from_file(os.path.join(settings.ROOT_DIR, 'db', 'dml', 'db_data.sql')), ''),
        migrations.RunSQL("SET search_path TO " + settings.DATABASES['default']['SCHEMAS'], ''),
        
        migrations.RunPython(forwards_func, reverse_func),
    ]
