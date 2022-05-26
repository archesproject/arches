try:
    from .dataspace.settings import *
except ImportError:
    pass
try:
    GEOS_LIBRARY_PATH = 'C:\\OSGeo4W\\bin\\geos_c.dll'
    GDAL_LIBRARY_PATH = 'C:\\OSGeo4W\\bin\\gdal304.dll'
    
except ImportError:
    pass