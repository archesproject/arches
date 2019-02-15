import os
import imp
import unicodecsv
import uuid
import json
import traceback
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from arches.app.models.entity import Entity
from arches.app.models.concept import Concept
from arches.app.models.models import ConceptRelations, Entities, EntityTypes

# this is really not the best way to import the Resource class, but I was unable
# to figure out how to import it using the string in settings.RESOURCE_MODEL
from eamena.models.resource import Resource

class Command(BaseCommand):

    option_list = BaseCommand.option_list + ()

    def handle(self, *args, **options):

        self.find_unused_nodes()
        self.test_form_classes()
    
    def find_unused_nodes(self):
        
        print "\n\n==== TESTING NODES ACROSS ALL FORMS ===="
        formdir = os.path.join(settings.PACKAGE_ROOT,"templates","views","forms")
        files = [i for i in os.listdir(formdir) if i.endswith(".htm")]

        entities = EntityTypes.objects.exclude(businesstablename="")
        entitynames = [i.entitytypeid for i in entities]
        data = {i.entitytypeid: list() for i in entities}

        # test that all of the nodes are in some file
        for form in files:
            filepath = os.path.join(formdir, form)
            with open(filepath,"rb") as f:
                contents = f.read().decode("ascii","ignore")
                for k in data:
                    if k in contents:
                        data[k].append(form)

        print "\n--- THESE NODES AREN'T USED IN ANY FORMS ---\n"
        for k in sorted(data):
            if len(data[k]) == 0:
                print k
                
        return entitynames

    def test_template(self,templateid,valid_nodes):

        formdir = os.path.join(settings.PACKAGE_ROOT,"templates","views","forms")
        filepath = os.path.join(formdir,templateid+".htm")

        nodes_in_file = list()
        with open(filepath,"rb") as f:
            lines = f.readlines()
            for line in lines:
                if "getEditedNode(" in line:
                    name = line.split("getEditedNode(")[1].split(",")[0]
                    name = name.replace("'","")
                    name = name.replace('"',"")
                    nodes_in_file.append(name)
        
        invalid = [i for i in nodes_in_file if not i in valid_nodes]
                
        return invalid

    def test_form_classes(self):
    
        print "\n\n==== TESTING ALL FORM CLASSES ===="
    
        # These are considered exceptions because they are often included
        # in a resource type but actually enter data for a different resource
        # type. So they will throw errors below, even if they are valid.
        form_exceptions = [
            'man-made',
            'man-made-component',
            'related-files',
            'related-resources',
            'file-upload'
        ]

        
        for restype in sorted(settings.RESOURCE_TYPE_CONFIGS()):
            print "\n\n--- {} FORMS ---".format(restype)

            q = Entity().get_mapping_schema(restype)
            restypenodes = set(q.keys())

            res = Resource({"entitytypeid":restype})

            for group in res.form_groups:
                for form in group['forms']:
                    invalid_nodes = []
                    fclass = form['class']
                    formid = fclass.get_info()['id']
                    if formid in form_exceptions:
                        continue
                    print "\nFORM:",formid
                    
                    template_errors = self.test_template(formid,restypenodes)
                    
                    print "{} invalid node{} in the template".format(
                            len(template_errors), "s" if len(template_errors) != 1 else "")
                    if len(template_errors) > 0:
                        print "  ", template_errors
            
                    a = res.get_form(formid)
                    try:
                        a.load("en-US")
                    except Exception as e:
                        print "ERROR LOADING THIS FORMS.PY CLASS"
                        print traceback.print_exc()
                        continue

                    for key in a.data:
                        if not key in restypenodes and "." in key:
                            invalid_nodes.append(key)
                        domains = a.data[key].get('domains',[])
                        for domainnode in domains:
                            if not domainnode in restypenodes:
                                invalid_nodes.append(domainnode)

                    print "{} invalid node{} in the forms.py class".format(
                            len(invalid_nodes), "s" if len(invalid_nodes) != 1 else "")
                    if len(invalid_nodes) > 0:
                        print "  ", invalid_nodes
