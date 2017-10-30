from django.core import management
from django.core.management.base import BaseCommand, CommandError
# 
import django.apps
# import psycopg2
import arches
import json
import uuid
import time

class Command(BaseCommand):

    help = 'finds a uuid throughout your database and prints info from postgres'

    def add_arguments(self, parser):
        parser.add_argument("uuid",help='input the uuid string to find')

    def handle(self, *args, **options):

        self.find_uuid(options['uuid'])

    def find_uuid(self,in_uuid):
    
        ## check for valid uuid input
        try:
            val = uuid.UUID(in_uuid, version=4)
        except:
            print "  -- this is not a vali uuid"
            return False
        
        # start1 = time.time()
        
        ## search all models and see if the UUID matches an existing object
        neo = False
        for m in django.apps.apps.get_models():
            if m._meta.pk.get_internal_type() == "UUIDField":
                ob = m.objects.filter(pk=in_uuid)
                if len(ob) == 1:
                    neo = ob[0]
                    break
        
        ## return False if nothing was found
        if not neo:
            print "  -- this uuid doesn't match any objects in your database"
            return False
        
        print "this is a", neo
        
        for k,v in vars(neo).iteritems():
            print k
            print " ",v
        
        # print round(time.time()-start1,2)
        
        return neo