from django.contrib.gis.db.backends.postgis.base import DatabaseWrapper as PostGISDatabaseWrapper
from .schema import ArchesPostGISSchemaEditor

class DatabaseWrapper(PostGISDatabaseWrapper):
    SchemaEditorClass = ArchesPostGISSchemaEditor
    
    #
    # Code based off of django.db.backends.postgresql_psycopg2.base.py
    #
    def init_connection_state(self):
        settings_dict = self.settings_dict
        self.connection.set_client_encoding('UTF8')
        self.connection.cursor().execute("SET search_path TO " + settings_dict['SCHEMAS'])

        tz = self.settings_dict['TIME_ZONE']
        conn_tz = self.connection.get_parameter_status('TimeZone')

        if conn_tz != tz:
            cursor = self.connection.cursor()
            try:
                cursor.execute(self.ops.set_time_zone_sql(), [tz])
            finally:
                cursor.close()
            # Commit after setting the time zone (see #17062)
            if not self.get_autocommit():
                self.connection.commit()