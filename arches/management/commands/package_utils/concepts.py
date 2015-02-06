from django.db import connection, transaction

def insert_concept_relations(sourcelegacyid, relationshiptype, targetlegacyid):
    cursor = connection.cursor()

    sql = """
        SELECT concepts.insert_relation('%s','%s','%s');
    """ % (sourcelegacyid, relationshiptype.replace("'","''"), targetlegacyid)

    # print sql
    cursor.execute(sql)

def index_entity_concept_lables():
    from arches.app.models import models
    from arches.app.models.concept import Concept
    
    domains_concept = Concept('00000000-0000-0000-0000-000000000003')
    entitynodes_concept = Concept('00000000-0000-0000-0000-000000000004')
    
    entitytypes = models.EntityTypes.objects.all()
    for entitytype in entitytypes:
        concept = Concept(entitytype.conceptid).get(include=['label'])
        if entitytype.businesstablename == 'domains':
            concept.index(scheme=domains_concept)
        else:
            concept.index(scheme=entitynodes_concept)
