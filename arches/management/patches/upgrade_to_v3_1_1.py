from django.db import connection, transaction
from django.contrib.auth.models import User, Group
from arches.app.search.search_engine_factory import SearchEngineFactory
import pip
import time



from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

def main():

    sql = """ALTER TABLE concepts.concepts
            ALTER COLUMN conceptid DROP DEFAULT;

    ALTER TABLE concepts.concepts
            ALTER COLUMN legacyoid SET NOT NULL;

    ALTER TABLE concepts.concepts
            DROP CONSTRAINT IF EXISTS unique_concepts_legacyoid;

    ALTER TABLE concepts.concepts
            ADD CONSTRAINT unique_concepts_legacyoid UNIQUE (legacyoid);


    CREATE OR REPLACE VIEW ontology.vw_export_nodes AS 
            SELECT foo.assettype,
                    foo.node AS label,
                    (foo.assettype || ':'::text) || foo.node AS id,
                    foo.mergenodeid AS mergenode,
                    foo.businesstable AS businesstablename
            FROM ( SELECT m.entitytypeidfrom AS assettype,
                            r.entitytypedomain AS node,
                            m.mergenodeid,
                            ( SELECT entity_types.businesstablename
                                         FROM data.entity_types
                                        WHERE entity_types.entitytypeid = r.entitytypedomain) AS businesstable
                         FROM ontology.mapping_steps ms
                             JOIN ontology.mappings m ON m.mappingid = ms.mappingid
                             JOIN ontology.rules r ON r.ruleid = ms.ruleid
                    UNION
                     SELECT m.entitytypeidfrom,
                            r.entitytyperange AS node,
                            m.mergenodeid,
                            ( SELECT entity_types.businesstablename
                                         FROM data.entity_types
                                        WHERE entity_types.entitytypeid = r.entitytyperange) AS businesstable
                         FROM ontology.mapping_steps ms
                             JOIN ontology.mappings m ON m.mappingid = ms.mappingid
                             JOIN ontology.rules r ON r.ruleid = ms.ruleid) foo
            WHERE (foo.node <> ALL (ARRAY['ARCHES_RECORD.E31'::text, 'CREATION_EVENT.E65'::text, 'UPDATE_EVENT.E65'::text, 'COMPILER.E82'::text, 'COMPILER_PERSON.E21'::text, 'REFERENCE_NUMBER_(INTERNAL).E42'::text, 'TIME-SPAN_UPDATE_EVENT.E52'::text, 'TIME-SPAN_CREATION_EVENT.E52'::text, 'DATE_OF_COMPILATION.E50'::text, 'DATE_OF_LAST_UPDATE.E50'::text])) AND foo.node <> foo.assettype
            ORDER BY foo.assettype, foo.node;

            ALTER TABLE ontology.vw_export_nodes
                OWNER TO postgres;


    CREATE OR REPLACE VIEW ontology.vw_export_edges AS 
            SELECT m.entitytypeidfrom AS assettype,
                    (m.entitytypeidfrom || ':'::text) || r.entitytypedomain AS source,
                    (m.entitytypeidfrom || ':'::text) || r.entitytyperange AS target,
                    r.propertyid AS label
            FROM ontology.mapping_steps ms
                    JOIN ontology.mappings m ON m.mappingid = ms.mappingid
                    JOIN ontology.rules r ON r.ruleid = ms.ruleid
            WHERE (m.entitytypeidfrom <> ALL (ARRAY['ARCHES_RECORD.E31'::text, 'CREATION_EVENT.E65'::text, 'UPDATE_EVENT.E65'::text, 'COMPILER.E82'::text, 'COMPILER_PERSON.E21'::text, 'REFERENCE_NUMBER_(INTERNAL).E42'::text, 'TIME-SPAN_UPDATE_EVENT.E52'::text, 'TIME-SPAN_CREATION_EVENT.E52'::text, 'DATE_OF_COMPILATION.E50'::text, 'DATE_OF_LAST_UPDATE.E50'::text])) AND (r.entitytypedomain <> ALL (ARRAY['ARCHES_RECORD.E31'::text, 'CREATION_EVENT.E65'::text, 'UPDATE_EVENT.E65'::text, 'COMPILER.E82'::text, 'COMPILER_PERSON.E21'::text, 'REFERENCE_NUMBER_(INTERNAL).E42'::text, 'TIME-SPAN_UPDATE_EVENT.E52'::text, 'TIME-SPAN_CREATION_EVENT.E52'::text, 'DATE_OF_COMPILATION.E50'::text, 'DATE_OF_LAST_UPDATE.E50'::text])) AND (r.entitytyperange <> ALL (ARRAY['ARCHES_RECORD.E31'::text, 'CREATION_EVENT.E65'::text, 'UPDATE_EVENT.E65'::text, 'COMPILER.E82'::text, 'COMPILER_PERSON.E21'::text, 'REFERENCE_NUMBER_(INTERNAL).E42'::text, 'TIME-SPAN_UPDATE_EVENT.E52'::text, 'TIME-SPAN_CREATION_EVENT.E52'::text, 'DATE_OF_COMPILATION.E50'::text, 'DATE_OF_LAST_UPDATE.E50'::text])) AND m.entitytypeidto = r.entitytyperange
            ORDER BY m.entitytypeidfrom;

    ALTER TABLE ontology.vw_export_edges
        OWNER TO postgres;

    INSERT INTO concepts.d_valuetypes SELECT 'sortorder', 'undefined', null, 'arches', 'text'
            WHERE NOT EXISTS (SELECT 1 FROM concepts.d_valuetypes WHERE valuetype = 'sortorder'); 


    CREATE OR REPLACE FUNCTION concepts.concpets_ins()
            RETURNS trigger AS
            $BODY$
            DECLARE
             v_uuid uuid = public.uuid_generate_v1mc();

            BEGIN
            --Provides CONCEPTID for RDM inserts and cases where ETL conceptid is not a UUID
                IF NEW.CONCEPTID IS NULL THEN
                     NEW.CONCEPTID := v_uuid;
                END IF;

             -- Supports RDM where no concpetid or legacyoid is fed in
                IF NEW.CONCEPTID IS NULL AND (NEW.LEGACYOID IS NULL OR NEW.LEGACYOID = '') THEN
                     NEW.LEGACYOID = v_uuid::text;
                END IF;   


            -- I would assume that two cases below are handled in python code by being explicit about insert values for both columns... just coding defensively here. ABL.
            -- Supports where ETL provided conceptid is a UUID and will be kept, but no LEGACYOID provided.
                IF NEW.CONCEPTID IS NOT NULL and (NEW.LEGACYOID is null or NEW.LEGACYOID = '') THEN
                     NEW.LEGACYOID = NEW.CONCEPTID::text;     
                END IF;   

            -- Supports where ETL'ed conceptid is not a UUID.  Populates original "concpetid" as LEGACYOID.
                IF NEW.LEGACYOID IS NOT NULL OR NEW.LEGACYOID != '' then
                     NEW.LEGACYOID = NEW.LEGACYOID;     
                END IF;   

            RETURN NEW;
            END$BODY$
                LANGUAGE plpgsql VOLATILE
                COST 100;

    ALTER FUNCTION concepts.concpets_ins()
        OWNER TO postgres;

        
        
    -- Trigger: concepts_ins_tgr on concepts.concepts

    DROP TRIGGER IF EXISTS concepts_ins_tgr ON concepts.concepts;

    CREATE TRIGGER concepts_ins_tgr
        BEFORE INSERT
        ON concepts.concepts
        FOR EACH ROW
        EXECUTE PROCEDURE concepts.concpets_ins();"""


    with transaction.atomic():
        #import arches.management.patches.upgrade_to_v3_0_4

        cursor = connection.cursor()
        cursor.execute(sql)

        anonymous_user, created = User.objects.get_or_create(username='anonymous')
        if created:
                anonymous_user.set_password('')

        read_group, created = Group.objects.get_or_create(name='read')
        anonymous_user.groups.add(read_group)

        edit_group, created = Group.objects.get_or_create(name='edit')
        admin_user = User.objects.get(username='admin')
        admin_user.groups.add(edit_group)
        admin_user.groups.add(read_group)

        print '\nINSTALLING PYSHP MODULE'
        print '-----------------------'
        pip.main(['install', 'pyshp'])


        print '\nUPDATING ENTITY INDEX'
        print '---------------------'

        # Add numbers array to resources that do not have them. Move numbers data from child_entities to numbers array in index.
        resourceid_sql = "SELECT entityid FROM data.entities WHERE entitytypeid IN (SELECT distinct(entitytypeid) FROM data.entity_types WHERE isresource =True);"
        cursor.execute(resourceid_sql)
        resourceids = []
        for val in cursor.fetchall():
            resourceids.append(val[0])
        
        start = time.time()
        records = 0
        se = SearchEngineFactory().create()
        for resourceid in resourceids:
            indexed_resource = se.search(index='entity', id=resourceid)        

            if 'numbers' not in indexed_resource['_source']:
                indexed_resource['_source']['numbers'] = []
            else:
                pass
                
            for child_entity in indexed_resource['_source']['child_entities']:
                if child_entity['businesstablename'] == 'numbers':
                    index_resource['_source']['numbers'].append(child_entity)
                    indexed_resource['_source']['child_entities'].remove(child_entity)
        
            ## Reindex resource here.
            se.index_data(index='entity',doc_type=indexed_resource['_type'], body=indexed_resource['_source'], id=indexed_resource['_id'])
            records+=1
            # if records%500 == 0:
            #     print '%s records processed'%str(records)

        print '%s records updated' % str(records)

        # print 'Patch took %s seconds to run.'%str(time.time() - start)

        print "\npatch '%s' successfully applied." % __name__

main()