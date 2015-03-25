{% if source_app == 'arches' %}

import os
import sys
from django.conf import settings
from django.core import management
from arches.setup import get_version
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.data_management.resources.importer import ResourceLoader
import arches.app.utils.data_management.resources.remover as resource_remover
from arches.management.commands.package_utils import resource_graphs
from arches.management.commands.package_utils import authority_files
from arches.app.models.resource import Resource


def setup():
    get_version(path_to_file=os.path.abspath(os.path.dirname(__file__)))

def install(path_to_source_data_dir=None):
    truncate_db()
    
    delete_index(index='concept_labels')
    delete_index(index='term') 
    Resource().prepare_term_index(create=True)

    load_resource_graphs()
    load_authority_files(path_to_source_data_dir)
    load_map_layers()

    resource_remover.truncate_resources()
    delete_index(index='resource')
    delete_index(index='entity')
    delete_index(index='maplayers')
    delete_index(index='resource_relations') 
    create_indexes()   

    load_resources()

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
    authority_files.load_authority_files(break_on_error=True)

def load_map_layers():
    pass

def delete_index(index=None):
    se = SearchEngineFactory().create()
    se.delete_index(index=index)

def create_indexes():
    pass
    # Resource().prepare_resource_relations_index(create=True)
    # Resource().prepare_search_index('HERITAGE_RESOURCE_GROUP.E27', create=True)
    # Resource().prepare_search_index('HERITAGE_RESOURCE.E18', create=True)
    # Resource().prepare_search_index('INFORMATION_RESOURCE.E73', create=True)
    # Resource().prepare_search_index('ACTIVITY.E7', create=True)
    # Resource().prepare_search_index('ACTOR.E39', create=True)
    # Resource().prepare_search_index('HISTORICAL_EVENT.E5', create=True)

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
        
if __name__ == "__main__":
    install()

{% else %}

import {{ source_app }}.setup as setup

def install(path_to_source_data_dir=None):
    setup.install()

def load_resource_graphs():
    setup.resource_graphs.load_graphs(break_on_error=True)

def load_authority_files(path_to_files=None):
    setup.authority_files.load_authority_files(path_to_files, break_on_error=True)

def load_resources(external_file=None):
    setup.load_resources(external_file)

{% endif %}