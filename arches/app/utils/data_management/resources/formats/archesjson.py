
import os
import types
import sys
from django.conf import settings
from django.db import connection
import arches.app.models.models as archesmodels
from arches.app.models.resource import Resource
import codecs
from format import Writer
import json
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
import csv

import time
from multiprocessing import Pool, TimeoutError, cpu_count
from django.db import connections

# this wrapper function must be outside of the class to be called during the
# multiprocessing operations.
def write_one_resource_wrapper(args):
    return JsonWriter.write_one_resource(*args)

class JsonWriter(Writer):

    def __init__(self, jsonl=False):
        super(JsonWriter, self).__init__()
        self.jsonl = jsonl

    def write_one_resource(self, resource_id):

        a_resource = Resource().get(resource_id)
        a_resource.form_groups = None
        jsonres = JSONSerializer().serialize(a_resource, separators=(',',':'))
        return jsonres

    def write_resources(self, dest_dir):

        # if JSONL file is desired, use this code to write the resource line by
        # line, and also introduce multiprocessing to speed things up.
        if self.jsonl is True:

            process_count = cpu_count()
            print "number of cores:", cpu_count()
            print "number of parallel processes:", process_count
            pool = Pool(cpu_count())

            restypes = [i.entitytypeid for i in archesmodels.EntityTypes.objects.filter(isresource=True)]

            for restype in restypes:
                start = time.time()
                resources = archesmodels.Entities.objects.filter(entitytypeid=restype)
                resids = [r.entityid for r in resources]
                
                for conn in connections.all():
                    conn.close()
                
                outfile = dest_dir.replace(".jsonl","-"+restype+".jsonl")
                with open(outfile, 'w') as f:

                    print "Writing {0} {1} resources".format(len(resids), restype) 
                    joined_input = [(self,r) for r in resids]
                    for res in pool.imap(write_one_resource_wrapper, joined_input):
                        f.write(res+"\n")

                print "elapsed time:", time.time()-start

        # if standard JSON is desired, use the existing JSON export code
        else:
            cursor = connection.cursor()
            cursor.execute("""select entitytypeid from data.entity_types where isresource = TRUE""")
            resource_types = cursor.fetchall()

            start = time.time()
            json_resources = []
            with open(dest_dir, 'w') as f:
                for resource_type in resource_types:
                    resources = archesmodels.Entities.objects.filter(entitytypeid = resource_type)
                    print "Writing {0} {1} resources".format(len(resources), resource_type[0])
                    errors = []
                    for resource in resources:
                        try:
                            a_resource = Resource().get(resource.entityid)
                            a_resource.form_groups = None
                            json_resources.append(a_resource)
                        except Exception as e:
                            if e not in errors:
                                errors.append(e)
                    if len(errors) > 0:
                        print errors[0], ':', len(errors)
                f.write((JSONSerializer().serialize({'resources':json_resources}, separators=(',',':'))))
            print "elapsed time:", time.time()-start
        

class JsonReader():

    def validate_file(self, archesjson, break_on_error=True):
        pass

    def load_file(self, archesjson):
        resources = []
        with open(archesjson, 'r') as f:
            resources = JSONDeserializer().deserialize(f.read())
        return resources['resources']