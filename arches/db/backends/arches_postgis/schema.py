import hashlib

from django.db.backends.utils import truncate_name
from django.utils.encoding import force_bytes
from django.contrib.gis.db.backends.postgis.schema import PostGISSchemaEditor


class ArchesPostGISSchemaEditor(PostGISSchemaEditor):

    #
    # Code based off of django.contrib.gis.db.backends.postgis.schema.py
    #
    def column_sql(self, model, field, include_default=False):
        from django.contrib.gis.db.models.fields import GeometryField
        if not isinstance(field, GeometryField):
            return super(ArchesPostGISSchemaEditor, self).column_sql(model, field, include_default)

        if field.geography or self.connection.ops.geometry:
            # Geography and Geometry (PostGIS 2.0+) columns are
            # created normally.

            # Added for Arches schema support
            # we are purposely calling the super class of PostGISSchemaEditor rather then ArchesPostGISSchemaEditor
            column_sql = super(PostGISSchemaEditor, self).column_sql(model, field, include_default)
        else:

            column_sql = None, None
            # Geometry columns are created by the `AddGeometryColumn`
            # stored procedure.
            self.geometry_sql.append(
                self.sql_add_geometry_column % {
                    "table": self.geo_quote_name(model._meta.db_table),
                    "column": self.geo_quote_name(field.column),
                    "srid": field.srid,
                    "geom_type": self.geo_quote_name(field.geom_type),
                    "dim": field.dim,
                }
            )

            if not field.null:
                self.geometry_sql.append(
                    self.sql_alter_geometry_column_not_null % {
                        "table": self.quote_name(model._meta.db_table),
                        "column": self.quote_name(field.column),
                    }
                )

        if field.spatial_index:
            # Spatial indexes created the same way for both Geometry and
            # Geography columns.
            # PostGIS 2.0 does not support GIST_GEOMETRY_OPS. So, on 1.5
            # we use GIST_GEOMETRY_OPS, on 2.0 we use either "nd" ops
            # which are fast on multidimensional cases, or just plain
            # gist index for the 2d case.
            if field.geography:
                index_ops = ''
            elif self.connection.ops.geometry:
                if field.dim > 2:
                    index_ops = self.geom_index_ops_nd
                else:
                    index_ops = ''
            else:
                index_ops = self.geom_index_ops

            table_name = model._meta.db_table.replace('"', '').replace('.', '_')

            self.geometry_sql.append(
                self.sql_add_spatial_index % {
                    "index": self.quote_name('%s_%s_id' % (table_name, field.column)),
                    "table": self.quote_name(model._meta.db_table),
                    "column": self.quote_name(field.column),
                    "index_type": self.geom_index_type,
                    "ops": index_ops,
                }
            )
        return column_sql

    # 
    # Code based off of django.db.backends.base.schema.py
    #
    def _create_index_name(self, model, column_names, suffix=""):
        """
        Generates a unique name for an index/unique constraint.
        """

        table_name = model._meta.db_table.replace('"', '').replace('.', '_')
        
        # If there is just one column in the index, use a default algorithm from Django
        if len(column_names) == 1 and not suffix:
            return truncate_name(
                '%s_%s' % (table_name, self._digest(column_names[0])),
                self.connection.ops.max_name_length()
            )
        # Else generate the name for the index using a different algorithm
        index_unique_name = '_%x' % abs(hash((table_name, ','.join(column_names))))
        max_length = self.connection.ops.max_name_length() or 200
        # If the index name is too long, truncate it
        index_name = ('%s_%s%s%s' % (
            table_name, column_names[0], index_unique_name, suffix,
        )).replace('"', '').replace('.', '_')
        if len(index_name) > max_length:
            part = ('_%s%s%s' % (column_names[0], index_unique_name, suffix))
            index_name = '%s%s' % (table_name[:(max_length - len(part))], part)
        # It shouldn't start with an underscore (Oracle hates this)
        if index_name[0] == "_":
            index_name = index_name[1:]
        # If it's STILL too long, just hash it down
        if len(index_name) > max_length:
            index_name = hashlib.md5(force_bytes(index_name)).hexdigest()[:max_length]
        # It can't start with a number on Oracle, so prepend D if we need to
        if index_name[0].isdigit():
            index_name = "D%s" % index_name[:-1]
 
        index_name = index_name.replace('"', '').replace('.', '_')
        return index_name

