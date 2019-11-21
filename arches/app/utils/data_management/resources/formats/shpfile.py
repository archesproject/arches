from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import MultiPoint
from django.contrib.gis.geos import MultiLineString
from django.contrib.gis.geos import MultiPolygon
from django.contrib.gis.geos import GeometryCollection
from .format import Writer
import datetime
import shapefile
import codecs

from io import StringIO
from io import BytesIO


class ShpWriter(Writer):
    def __init__(self, **kwargs):
        super(ShpWriter, self).__init__(**kwargs)

    def convert_geom(self, geos_geom):
        if geos_geom.geom_type == "Point":
            multi_geom = MultiPoint(geos_geom)
            shp_geom = [[c for c in multi_geom.coords]]
        if geos_geom.geom_type == "LineString":
            multi_geom = MultiLineString(geos_geom)
            shp_geom = [c for c in multi_geom.coords]
        if geos_geom.geom_type == "Polygon":
            multi_geom = MultiPolygon(geos_geom)
            shp_geom = [c[0] for c in multi_geom.coords]
        if geos_geom.geom_type == "MultiPoint":
            shp_geom = [[c for c in geos_geom.coords]]
        if geos_geom.geom_type == "MultiLineString":
            shp_geom = [c for c in geos_geom.coords]
        if geos_geom.geom_type == "MultiPolygon":
            shp_geom = [c[0] for c in geos_geom.coords]

        return shp_geom

    def process_feature_geoms(self, resource, geom_field):
        """
        Reduces an instances geometries from a geometry collection that potentially has any number of points, lines
        and polygons down to a list containing a MultiPoint and/or a MultiLine, and/or a MultiPolygon object.
        """
        result = []
        sorted_geoms = {"points": [], "lines": [], "polys": []}
        for geom in resource[geom_field]:
            if geom.geom_typeid == 0:
                sorted_geoms["points"].append(geom)
            if geom.geom_typeid == 1:
                sorted_geoms["lines"].append(geom)
            if geom.geom_typeid == 3:
                sorted_geoms["polys"].append(geom)
            if geom.geom_typeid == 4:
                for feat in geom:
                    sorted_geoms["points"].append(feat)
            if geom.geom_typeid == 5:
                for feat in geom:
                    sorted_geoms["lines"].append(feat)
            if geom.geom_typeid == 6:
                for feat in geom:
                    sorted_geoms["polys"].append(feat)

        if len(sorted_geoms["points"]) > 0:
            result.append(MultiPoint(sorted_geoms["points"]))
        if len(sorted_geoms["lines"]) > 0:
            result.append(MultiLineString(sorted_geoms["lines"]))
        if len(sorted_geoms["polys"]) > 0:
            result.append(MultiPolygon(sorted_geoms["polys"]))

        return result

    def create_shapefiles(self, instances, headers, name):
        """
        Takes a geojson-like (geojson-like because it has a geos geometry rather than a geojson geometry, allowing us to modify the
        geometry to be a centroid or hull if necessary.) feature collection, groups the data by resource type and creates a shapefile
        for each resource. Returns a .zip file with each of the shapefiles. An arches export configuration file is needed to map shapefile
        fields to resorce entitytypeids and specify the shapefile column datatypes (fiona schema).
        """
        geometry_field = None
        if len(instances) > 0:
            for k, v in instances[0].items():
                if isinstance(v, GeometryCollection):
                    geometry_field = k
        else:
            return []

        features_by_geom_type = {"point": [], "line": [], "poly": []}
        for instance in instances:
            feature_geoms = self.process_feature_geoms(instance, geometry_field)
            for geometry in feature_geoms:
                instance[geometry_field] = geometry
                if geometry.geom_typeid == 4:
                    features_by_geom_type["point"].append(instance)

                elif geometry.geom_typeid == 5:
                    features_by_geom_type["line"].append(instance)

                elif geometry.geom_typeid == (6):
                    features_by_geom_type["poly"].append(instance)

        shapefiles_for_export = []
        geos_datatypes_to_pyshp_types = {"str": "C", "datetime": "D", "float": "F"}
        for geom_type, features in features_by_geom_type.items():
            if len(features) > 0:

                shp = BytesIO()
                shx = BytesIO()
                dbf = BytesIO()
                prj = BytesIO()

                if geom_type == "point":
                    writer = shapefile.Writer(shp=shp, shx=shx, dbf=dbf, shapeType=shapefile.MULTIPOINT)
                elif geom_type == "line":
                    writer = shapefile.Writer(shp=shp, shx=shx, dbf=dbf, shapeType=shapefile.POLYLINE)
                elif geom_type == "poly":
                    writer = shapefile.Writer(shp=shp, shx=shx, dbf=dbf, shapeType=shapefile.POLYGON)

                for header in headers:
                    if header != geometry_field:
                        writer.field(header, "C", 255)

                for r in features:
                    shp_geom = self.convert_geom(r[geometry_field])
                    if geom_type in ["point", "line"]:
                        writer.line(shp_geom)
                    elif geom_type == "poly":
                        writer.poly(shp_geom)
                    # instance.pop(geometry_field)
                    writer.record(**instance)

                prj.write(
                    b'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]'
                )
                # writer.saveShp(shp)
                # writer.saveShx(shx)
                # writer.saveDbf(dbf)
                writer.close()
                print("writer saved", name, geom_type, shp)
                shapefiles_for_export += [
                    {"name": name + geom_type + ".shp", "outputfile": shp},
                    {"name": name + geom_type + ".dbf", "outputfile": dbf},
                    {"name": name + geom_type + ".shx", "outputfile": shx},
                    {"name": name + geom_type + ".prj", "outputfile": prj},
                ]
        print(shapefiles_for_export)
        return shapefiles_for_export
