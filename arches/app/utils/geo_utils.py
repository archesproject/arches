from django.contrib.gis.geos import GEOSGeometry, GeometryCollection
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer


class GeoUtils(object):

    def get_bounds_from_geojson(self, geojson):
        """
        Takes a geojson object with polygon(s) and returns the coordinates of
        the extent of the polygons.

        """
        polygons = []
        try:
            for feature in geojson['features']:
                if feature['geometry']['type'] == 'Polygon':
                    polygons.append(GEOSGeometry(JSONSerializer().serialize(feature['geometry'])))
            bounds = GeometryCollection(polygons).extent
        except:
            bounds = geojson

        return bounds
