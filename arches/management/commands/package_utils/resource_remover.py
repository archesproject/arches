from django.conf import settings
from django.db import connection, transaction
from arches.app.models.entity import Entity
import arches.app.models.models as archesmodels
from django.db.models import Q
from django.db.models import Count
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist


def delete_resources(load_id, truncate='False'):
	"""Takes the load id stored in the note column of the edit log and deletes each resource with that id"""
	resources_for_removal = archesmodels.EditLog.objects.filter( Q(note=load_id) )
	resourceids = set([editlog.resourceid for editlog in resources_for_removal])
	for r_id in resourceids:
		try:
			entity = Entity(r_id)
			entity.delete_index()
			entity.delete(delete_root=True)
		except ObjectDoesNotExist:
			print 'Entity does not exist. Nothing to delete'

    # if truncate == 'True':
    #     cursor = connection.cursor()
    #     cursor.execute("""TRUNCATE data.entities CASCADE;""" )