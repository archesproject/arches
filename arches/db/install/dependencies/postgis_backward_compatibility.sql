--for backward compatibility with postgis 1.5 ...statement just fails in 2.0
INSERT INTO geometry_columns(
            f_table_catalog, f_table_schema, f_table_name, f_geometry_column, 
            coord_dimension, srid, "type")
    VALUES ('','app', 'geometries', 'geometry', 2, 4326, 'GEOMETRY');
