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

def delete_resource_list(resourcelist=[]):

    for resid in resourcelist:
        try:
            resource = Resource(resid)
            resource.delete_index()
            note = '{0} Deleted'.format(resid)
            resource.delete_all_resource_relationships()
            resource.delete(note=note)
        except ObjectDoesNotExist:
            print 'Entity',resid,'does not exist. Nothing to delete'          

def get_resourceids_from_edit_log(load_id=None,user_id=None):
    """collect all resources that match a load id or match a user id (not username)"""

    if load_id is not None:
        resources_for_removal = archesmodels.EditLog.objects.filter( Q(note=load_id) )
    elif user_id is not None:
        resources_for_removal = archesmodels.EditLog.objects.filter( Q(userid=user_id) )

    resourceids = set([editlog.resourceid for editlog in resources_for_removal])

    return resourceids

def get_resourceids_from_csv(data_source):
    """Reads a list of Resource IDs from a csv file and deletes them"""

    resource_list = list()
    with open(data_source, 'rb') as csvfile:
        try:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            csvfile.seek(0)
        except csv.Error:
            print "The source data is not a CSV file"

        reader = csv.reader(csvfile)
        for row in reader:
            try:
                uuid = uuid.UUID(reader[0])
                resource_list.append(uuid)
            except ValueError:
                print "{} is not a valid UUID (skipping).".format(row[0])

    return resource_list

def truncate_resources():
    """Deletes ALL resources in your database. Use with caution!"""
    cursor = connection.cursor()
    cursor.execute("""TRUNCATE data.entities CASCADE;""" )
    index_database.index_db()
    print 'Resources Truncated'