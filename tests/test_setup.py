import os
import sys
from django.db import transaction, connection
from tests import test_settings as settings
from django.core import management
from arches.app.models import models
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.data_management.resources.importer import ResourceLoader
import arches.app.utils.data_management.resources.remover as resource_remover
from arches.management.commands.package_utils import resource_graphs
from arches.management.commands.package_utils import authority_files
from arches.app.models.resource import Resource


def install(path_to_source_data_dir=None):
    #truncate_db()

    execute_sql("Truncate public.auth_permission Cascade;")

    for concept in models.Concept.objects.filter(nodetype='Concept'):
        concept.delete()

    
    delete_index(index='concept_labels')
    delete_index(index='term') 
    Resource().prepare_term_index(create=True)

    #load_resource_graphs()
    load_authority_files(path_to_source_data_dir)
    load_map_layers()

    #resource_remover.truncate_resources()
    delete_index(index='resource')
    delete_index(index='entity')
    delete_index(index='maplayers')
    delete_index(index='resource_relations') 
    create_indexes()   

    #load_resources()

def export_data():
    pass

def import_data():
    pass

def truncate_db():
    management.call_command('packages', operation='setup_db') 

def load_resource_graphs():
    resource_graphs.load_graphs(break_on_error=True)
    pass

def load_authority_files(path_to_files=None):
    authority_files.load_authority_files(path_to_files, break_on_error=True)

def load_map_layers():
    pass

def delete_index(index=None):
    se = SearchEngineFactory().create()
    se.delete_index(index=index)

def create_indexes():
    Resource().prepare_resource_relations_index(create=True)
    Resource().prepare_search_index('PERSON.E1', create=True)

def install_dependencies():
    pass

def build_permissions():
    pass

def load_users():
    pass

def load_resources(external_file=None):
    rl = ResourceLoader()
    if external_file != None:
        print 'loading:', external_file
        rl.load(external_file)
    else:
        for f in settings.BUSISNESS_DATA_FILES:
            rl.load(f)
            
def execute_sql(sql):
    cursor = connection.cursor()
    cursor.execute(sql)
    #cursor.fetchall()