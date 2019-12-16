from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import MultiPoint
from django.contrib.gis.geos import MultiLineString
from django.contrib.gis.geos import MultiPolygon
from django.contrib.gis.geos import GeometryCollection
from .format import Writer
import datetime
import shapefile
from io import BytesIO
import copy


class ShpWriter(Writer):
    def __init__(self, **kwargs):
        super(ShpWriter, self).__init__(**kwargs)

    def convert_geom(self, geos_geom):
        """Coverts GEOS geometries to shapefile geometries"""
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
            shp_geom = [c for c in geos_geom.coords]
        if geos_geom.geom_type == "MultiLineString":
            shp_geom = [c for c in geos_geom.coords]
        if geos_geom.geom_type == "MultiPolygon":
            shp_geom = [c[0] for c in geos_geom.coords]

        return shp_geom

    def process_feature_geoms(self, resource, geom_field):
        """
        Reduces an instances geometries from a geometry collection, that potentially has any number of points, lines
        and polygons, down to a list containing a MultiPoint and/or a MultiLine, and/or a MultiPolygon object.
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

    def get_geometry_fieldnames(self, instance):
        """
        Finds GeometryCollection field in a flattened resource intance to use as the geometry of each shapefile record.
        """
        geometry_fields = []
        for k, v in instance.items():
            if isinstance(v, GeometryCollection):
                geometry_fields.append(k)
        return geometry_fields

    def sort_by_geometry_type(self, instances, geometry_field):
        """
        Sorts flattend resource instances by their geometry type (multipoint=4, multipolyline==5, multipolygon==6).
        If an instance has more than one geometry type, it is assigned to the respective geometry type once
        for each of its geometries.
        """
        features_by_geom_type = {"point": [], "line": [], "poly": []}
        for instance in instances:
            feature_geoms = self.process_feature_geoms(instance, geometry_field)
            for geometry in feature_geoms:
                feature = copy.copy(instance)
                feature[geometry_field] = geometry
                if geometry.geom_typeid == 4:
                    features_by_geom_type["point"].append(feature)

                elif geometry.geom_typeid == 5:
                    features_by_geom_type["line"].append(feature)

                elif geometry.geom_typeid == 6:
                    features_by_geom_type["poly"].append(feature)

        return features_by_geom_type

    def create_shapefiles(self, instances, headers, name):
        """
        Takes an array of flattened resource instances. If one of the resource fields contains a GeometryCollection,
        the instances will be grouped by geometry type and a shapefile file-like object will be returned for each
        geometry type.
        """

        if len(instances) > 0:
            geometry_fields = self.get_geometry_fieldnames(instances[0])
        else:
            return []

        shapefiles_for_export = []
        geos_datatypes_to_pyshp_types = {"str": "C", "datetime": "D", "float": "F"}

        for geometry_field in geometry_fields:
            features_by_geom_type = self.sort_by_geometry_type(instances, geometry_field)
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
                        try:
                            datatype = header.pop("datatype")
                        except KeyError:
                            pass
                        if header["fieldname"] != geometry_field:
                            writer.field(header["fieldname"], "C", 255)

                    for feature in features:
                        shp_geom = self.convert_geom(feature[geometry_field])
                        if geom_type == "point":
                            writer.multipoint(shp_geom)
                        if geom_type == "line":
                            writer.line(shp_geom)
                        elif geom_type == "poly":
                            writer.poly(shp_geom)

                        for header in headers:
                            if header["fieldname"] not in feature:
                                feature[header["fieldname"]] = ""

                        writer.record(**feature)

                    prj.write(
                        b'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],\
                        PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]'
                    )

                    writer.close()
                    shapefiles_for_export += [
                        {"name": f"{name}_{geometry_field}_{geom_type}.shp", "outputfile": shp},
                        {"name": f"{name}_{geometry_field}_{geom_type}.dbf", "outputfile": dbf},
                        {"name": f"{name}_{geometry_field}_{geom_type}.shx", "outputfile": shx},
                        {"name": f"{name}_{geometry_field}_{geom_type}.prj", "outputfile": prj},
                    ]

        return shapefiles_for_export
