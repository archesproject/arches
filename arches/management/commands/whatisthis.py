from django.core import management
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import psycopg2
import json
import uuid

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
            print "  -- invalid uuid"
            return
    
        db = settings.DATABASES['default']
        db_conn = "dbname = {} user = {} host = {} password = {}".format(
            db['NAME'],db['USER'],db['HOST'],db['PASSWORD'])
        conn = psycopg2.connect(db_conn)
        cur = conn.cursor()
        
        sql = '''
        SELECT tc.table_name, kc.column_name
            FROM  
                information_schema.table_constraints tc,  
                information_schema.key_column_usage kc,
                information_schema.columns c
            WHERE 
                kc.table_name = tc.table_name and kc.table_schema = tc.table_schema
                AND kc.constraint_name = tc.constraint_name
                AND kc.table_name = c.table_name and kc.table_schema = c.table_schema
                AND c.data_type = 'uuid'
                AND tc.constraint_type = 'PRIMARY KEY' 
            GROUP BY tc.table_name, kc.column_name
            ORDER BY table_name;
        '''
        
        cur.execute(sql)
        result = cur.fetchall()
       
        match = False
        for table,column in result:
            sql = '''SELECT * FROM {} WHERE {} = '{}';'''.format(table,column,in_uuid)
            cur.execute(sql)
            result = cur.fetchall()
            if len(result) > 0:
                sql2 = '''
                    SELECT COLUMN_NAME
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_NAME='{}';
                    '''.format(table)
                cur.execute(sql2)
                col_names = cur.fetchall()
                match = True
                break
        
        if not match:
            print "  -- this uuid could not be found in your database"
            return
        
        info = {}
        info['table name']=table
        for i, col in enumerate(col_names):
            info[col[0]] = str(result[0][i])
        
        print json.dumps(info, indent=2)
        
        return info
        