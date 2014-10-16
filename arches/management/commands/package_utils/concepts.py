from django.db import connection, transaction

def insert_concept_relations(sourcelegacyid, relationshiptype, targetlegacyid):
    cursor = connection.cursor()

    sql = """
        SELECT concepts.insert_relation('%s','%s','%s');
    """ % (sourcelegacyid, relationshiptype.replace("'","''"), targetlegacyid)

    # print sql
    cursor.execute(sql)
    #cursor.fetchone()