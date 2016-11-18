'''
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

from django.conf import settings
import urllib
import urllib2
import json

class Geocoder(object):

    def __init__(self):
        pass

    def find_candidates(self, search_string, api_key):
        pass

    def get_response(self, query_args, url):
        encoded_args = urllib.urlencode(query_args)
        complete_url = url + encoded_args
        response = json.loads(urllib2.urlopen(complete_url).read())
        return response


class BingGeocoder(Geocoder):

    def __init__(self):
        super(Geocoder, self).__init__()

    def find_candidates(self, search_string, api_key):
        query_args = { 'q': search_string, 'key': api_key }
        url = 'http://dev.virtualearth.net/REST/v1/Locations?'
        response = self.get_response(query_args, url)
        results = []
        for resource_set in response['resourceSets']:
            for feature in resource_set['resources']:
                results.append({
                    'id': feature['name'],
                    'text': feature['name'],
                    'geometry': {
                        "type": "Point",
                        "coordinates": [
                          feature['point']['coordinates'][1],
                          feature['point']['coordinates'][0]
                        ]
                    },
                    'score': feature['confidence']
                })

        return results

class MapzenGeocoder(Geocoder):
    def __init__(self):
        super(Geocoder, self).__init__()

    def find_candidates(self, search_string, api_key):
        query_args = { 'text': search_string, 'api_key': api_key }
        url = 'https://search.mapzen.com/v1/autocomplete?'
        response = self.get_response(query_args, url)
        results = []
        print response

        for feature in response['features']:
            results.append({
                'id': feature['properties']['id'],
                'text': feature['properties']['label'],
                'geometry': {
                    "type": "Point",
                    "coordinates": [
                      feature['geometry']['coordinates'][0],
                      feature['geometry']['coordinates'][1]
                    ]
                }
            })

        return results
