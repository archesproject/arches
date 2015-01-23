from django.conf import settings
from django.db import connection, transaction
from arches.app.models.resource import Resource
import arches.app.models.models as archesmodels
from django.db.models import Q
from django.db.models import Count
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist


def delete_resources(load_id):
    """Takes the load id stored in the note column of the edit log and deletes each resource with that id"""
    resources_for_removal = archesmodels.EditLog.objects.filter( Q(note=load_id) )
    resourceids = set([editlog.resourceid for editlog in resources_for_removal])
    for r_id in resourceids:
        try:
            resource = Resource(r_id)
            resource.delete_index()
            note = '{0} Deleted'.format(load_id)
            resource.delete_all_resource_relationships()
            resource.delete(note=note)
        except ObjectDoesNotExist:
            print 'Entity does not exist. Nothing to delete'


def truncate_resources():
    """Deletes ALL resources in your database. Use with caution!"""
    cursor = connection.cursor()
    cursor.execute("""TRUNCATE data.entities CASCADE;""" )
    print 'Resources Truncated'