from django.conf import settings
from django.db import connection, transaction
from arches.app.models.resource import Resource
import arches.app.models.models as archesmodels
from django.db.models import Q
from django.db.models import Count
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
import arches.app.utils.index_database as index_database
import csv
import uuid

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


def delete_resources_from_csv(data_source):
    """Reads a list of Resource IDs from a csv file and deletes them"""
    
    with open(data_source, 'rb') as csvfile:
      try:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
      except csv.Error:
        print "The source data is not a CSV file"
      
      resource_list = csv.reader(csvfile, delimiter = ',')
      print "There are",sum(1 for line in open(data_source))," resources that will be deleted"
      
      for r_id in resource_list:
        try:
          uuid.UUID(r_id[0])
          try:
              resource = Resource(r_id[0])
              resource.delete_index()
              note = '{0} Deleted'.format(r_id[0])
              resource.delete_all_resource_relationships()
              resource.delete(note=note)
          except ObjectDoesNotExist:
              print 'Entity ',r_id[0],' does not exist. Nothing to delete'          
        except(ValueError):
          print r_id[0], "is not a valid UUID"
          break
          
        
def truncate_resources():
    """Deletes ALL resources in your database. Use with caution!"""
    cursor = connection.cursor()
    cursor.execute("""TRUNCATE data.entities CASCADE;""" )
    index_database.index_db()
    print 'Resources Truncated'