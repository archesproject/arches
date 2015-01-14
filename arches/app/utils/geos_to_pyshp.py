from django.contrib.gis.geos import MultiPoint
from django.contrib.gis.geos import MultiLineString
from django.contrib.gis.geos import MultiPolygon

def convert_geom(geos_geom):
  if geos_geom.geom_type == 'Point':
      multi_geom = MultiPoint(geos_geom)
      shp_geom = [[c for c in multi_geom.coords]]
  if geos_geom.geom_type == 'LineString':
      multi_geom = MultiLineString(geos_geom)
      shp_geom = [c for c in multi_geom.coords]
  if geos_geom.geom_type == 'Polygon':
      multi_geom = MultiPolygon(geos_geom)
      shp_geom = [c[0] for c in multi_geom.coords]
  if geos_geom.geom_type == 'MultiPoint':
      shp_geom = [[c for c in geos_geom.coords]]
  if geos_geom.geom_type == 'MultiLineString':
      shp_geom = [c for c in geos_geom.coords]
  if geos_geom.geom_type == 'MultiPolygon':
      shp_geom = [c[0] for c in geos_geom.coords]

  return shp_geom