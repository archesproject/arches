from django.db import connection, transaction

cursor = connection.cursor()

def insert_concept_relations(sourcelegacyid, relationshiptype, targetlegacyid):
    sql = """
        SELECT concepts.insert_relation('%s','%s','%s');
    """ % (sourcelegacyid, relationshiptype.replace("'","''"), targetlegacyid)

    # print sql
    cursor.execute(sql)
    cursor.fetchone()
    transaction.commit_unless_managed()

def insert_concept(label, note, languageid, legacyid):
    sql = """
        SELECT concepts.insert_concept('%s','%s','%s','%s');
    """ % (label.replace("'","''"), note, languageid, legacyid)

    #print sql
    cursor.execute(sql)
    cursor.fetchone()
    transaction.commit_unless_managed()

def insert_concept_value(legacyid, label, labeltype, datatype=''):
    label_is_timestamp = 'N'
    try:
        timestamp_result = ''
        cursor.execute("""SELECT concepts.is_timestamp('{0}');""".format(label))
        timestamp_result = cursor.fetchone()
        #print timestamp_result
        label_is_timestamp = timestamp_result[0]
    except:
        pass

    if label_is_timestamp == 'N':
        if label.startswith('POINT') or label.startswith('POLY') or label.startswith('MULTI') or label.startswith('LINE'):
            try:
                label_geom = GEOSGeometry(label)
                if label_geom.valid:
                    datatype = 'geometry'
            except:
                pass
        else:
            try:
                float(label)
                datatype = 'numeric'
            except:
                try:
                    len(label)
                    datatype = 'text'
                except:
                    datatype = 'unk'
    else:
        datatype = 'timestamp'


    sql = """
        SELECT concepts.insert_value('%s','%s','%s','%s');
    """ % (legacyid, label, labeltype, datatype)

    # print sql
    cursor.execute(sql)
    cursor.fetchone()
    transaction.commit_unless_managed()
