import csv
from arches.app.utils.data_management.resources.importer import ResourceLoader 
from arches.app.models.resource import Resource
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.models.models import RelatedResource
from arches.app.search.elasticsearch_dsl_builder import Query, Terms

def LoadRelations(source):
    """
    Simple utility to load relations without having an arches file
    
    AZ 14/12/16
    """

    with open(source, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter= ',')
        for row in reader:
            try:
                ResourceLoader().relate_resources(row, legacyid_to_entityid = None, archesjson = True)
            except:
                print "Issue with entity1 %s and entity2 %s" %(row['RESOURCEID_FROM'], row['RESOURCEID_TO'])
                
                
def get_related_resources(resourceid, lang='en-US', limit=1000, start=0):
    ret = {
        'resource_relationships': [],
        'related_resources': []
    }
    se = SearchEngineFactory().create()

    query = Query(se, limit=limit, start=start)
    query.add_filter(Terms(field='entityid1', terms=resourceid).dsl, operator='or')
    resource_relations = query.search(index='resource_relations', doc_type='all')
    ret['total'] = resource_relations['hits']['total']
    for relation in resource_relations['hits']['hits']:
        ret['resource_relationships'].append(relation['_source'])
    return ret

              
def UnloadRelations(source):
    """
    Simple utility to unload relations
    
    AZ 17/1/17
    """
    with open(source, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter= ',')
        se = SearchEngineFactory().create()
        for row in reader:
            entity = Resource()
            entity.entityid = row['RESOURCEID_FROM']          
            related_oldindex = get_related_resources(row['RESOURCEID_FROM'])
            if related_oldindex:
                for releted_res in related_oldindex['resource_relationships']:
                    if str(releted_res['entityid2']) == str(row['RESOURCEID_TO']):
                        se.delete(index='resource_relations', doc_type='all', id=releted_res['resourcexid'])
            try:            
                relationship = RelatedResource.objects.get(entityid1=entity.entityid, entityid2=row['RESOURCEID_TO'],relationshiptype=row['RELATION_TYPE'])
                entity.delete_resource_relationship(row['RESOURCEID_TO'], row['RELATION_TYPE'])
            except:
                print "Issues deleting DB instance of relation with entity1 %s and entity2 %s . Most likely, the instance has already been deleted" % (row['RESOURCEID_FROM'], row['RESOURCEID_TO'])
                pass
                                    
#             try:
#                 entity = Resource()
#                 entity.entityid = row['RESOURCEID_FROM']
#                 relationship = RelatedResource.objects.get(entityid1=entity.entityid, entityid2=row['RESOURCEID_TO'],relationshiptype=row['RELATION_TYPE'])                 
#                 se.delete(index='resource_relations', doc_type='all', id=relationship.resourcexid)
#                 entity.delete_resource_relationship(row['RESOURCEID_TO'], row['RELATION_TYPE'])
#             except:
#                 print "Issue unloading relation with resourcexid %s entity1 %s and entity2 %s" %(relationship.resourcexid, row['RESOURCEID_FROM'], row['RESOURCEID_TO'])
    