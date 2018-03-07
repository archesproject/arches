import urllib,json
from django.contrib.gis.geos import GEOSGeometry
from django.conf import settings
import datetime
from arches.app.utils.betterJSONSerializer import JSONSerializer

def getdates(geometry):
    """
    This method retrieves the vintage dates of Bing imagery using Bing REST API methods. The dates relate
    to the centre point of the geometry passed as argument to the method.
    """
    if geometry is not None:
        geometry = JSONSerializer().serialize(geometry)
        BingDates = {}
        dates = []
        try: 
            geom = GEOSGeometry(geometry)
        except:
            geom = GEOSGeometry(geometry[1:-1]) # This is to account for the different formats of coordinates as present in the search index and in forms.py. The former is in GeoJSON, the latter in WKT.
        centroid = geom.centroid
        url = 'http://dev.virtualearth.net/REST/v1/Imagery/Metadata/Aerial/' + str(centroid.coords[1]) + ',' + str(centroid.coords[0]) + '?zl=19&key=' + settings.BING_KEY
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        dates.append(data['resourceSets'][0]['resources'][0]['vintageStart'])
        dates.append(data['resourceSets'][0]['resources'][0]['vintageEnd'])
        for date in dates:
          if date:
            date = datetime.datetime.strptime(date, '%d %b %Y %Z')
            
        BingDates['start'] = dates[0]
        BingDates['end'] = dates[1] if dates[1] != dates[0] and dates[0] !=None else None
        return BingDates
    else:
        return 'null'