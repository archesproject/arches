
import datetime
import arches.app.models.models as models
from arches.app.models.resource import Resource
import csv
from django.conf import settings

def validatedates(date):
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d') #Checks for format  YYYY-MM-DD
    except ValueError:
        try:
            d =datetime.datetime.strptime(date, '%Y-%m-%d %X') #Checks for format  YYYY-MM-DD hh:mm:ss
            date = d.strftime('%Y-%m-%d')
        except ValueError:
            try:
                d = datetime.datetime.strptime(date,'%d-%m-%Y') #Checks for format  DD-MM-YYYY
                date = d.strftime('%Y-%m-%d')
            except ValueError:
                try:
                    d = datetime.datetime.strptime(date,'%d/%m/%Y') #Checks for format  DD/MM/YYYY
                    date = d.strftime('%Y-%m-%d')
                except ValueError:
                    try:
                        d = datetime.datetime.strptime(date,'%d/%m/%y') #Checks for format  DD/MM/YY
                        date = d.strftime('%Y-%m-%d')       
                    except ValueError:
                        try:
                            d = datetime.datetime.strptime(date,'%Y') #Checks for format  YYYY
                            isodate = d.isoformat()
                            date = isodate.strip().split("T")[0] #
                        except ValueError:
                            try:
                                d = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S') #Checks for ISO 8601 format YYYY-MM-DDThh:mm:ss
                                date = d.strftime('%Y-%m-%d')
                            except:
                                raise ValueError("The value %s inserted is not a date" % date)
    return date


# def validate_concept(concept, concepts_in_node):
#     valuelist = [models.Values.objects.filter(value__iexact = concept, conceptid= concept_in_node) for concept_in_node in concepts_in_node]
#     valuelist = filter(None, valuelist)
#     if valuelist:
#         valueinstance = [x for x in valuelist if x]
#         return valueinstance
#     else:
#         return None
#         
# def collect_concepts(node_conceptid, full_concept_list = []):
#     ''' Collects a full list of child concepts given the conceptid of the node. Returns a list of a set of concepts, i.e. expounding the duplicates'''
#     concepts_in_node = models.ConceptRelations.objects.filter(conceptidfrom = node_conceptid)
#     if concepts_in_node.count() > 0:
#         full_concept_list.append(node_conceptid) 
#         for concept_in_node in concepts_in_node:
#             
#             collect_concepts(concept_in_node.conceptidto_id, full_concept_list)
#     else:
#         full_concept_list.append(node_conceptid)
#     return list(set(full_concept_list)) 

def return_one_node(nodename, destination):
    resources = models.Entities.objects.filter(entitytypeid = 'HERITAGE_RESOURCE_GROUP.E27').values_list('entityid', flat=True)
    ResourceList = []
    modelinstance = models.EntityTypes.objects.get(pk = nodename)
    for resourceid in resources:
        resource = Resource()
        resource.get(resourceid)
        node_entities = resource.find_entities_by_type_id(nodename)
        labels = []
        for node_entity in node_entities:
#             concepts_in_node = collect_concepts(modelinstance.conceptid_id, full_concept_list =[])
#             valueinstance =  validate_concept(node_entity.label, concepts_in_node)
#             if valueinstance is not None: 
#                 conceptinstance = models.Concepts.objects.get(pk=valueinstance[0][0].conceptid)            
#                 row = [resource.entityid, 'HERITAGE_RESOURCE_GROUP.E27', nodename, conceptinstance.legacyoid, 'NOT']
            labels.append(node_entity.label)
        row = [resource.entityid,';'.join(labels)]
        ResourceList.append(row)
        
    with open(destination, 'w') as csvfile:
            writer = csv.writer(csvfile)
#             writer.writerow(['RESOURCEID', 'RESOURCETYPE', 'ATTRIBUTENAME', 'ATTRIBUTEVALUE', 'GROUPID'])
#             ResourceList = sorted(ResourceList, key = lambda row:(row[0],row[4],row[2]), reverse = False)
            writer.writerow(['RESOURCEID',nodename])
            for row in ResourceList:
                writer.writerow(row)          