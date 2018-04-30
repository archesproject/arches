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

import json
import couchdb
from django.db import transaction
from urlparse import urlparse, urljoin
from arches.app.models import models
from arches.app.models.mobile_survey import MobileSurvey
from arches.app.models.system_settings import settings
from django.utils.translation import ugettext as _
from arches.app.utils.response import JSONResponse
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.http import HttpRequest, HttpResponseNotFound
import arches.app.views.search as search

class Couch(object):
    def __init__(self):
        self.couch = couchdb.Server(settings.COUCHDB_URL)
        # self.logger = logging.getLogger(__name__)

    def create_survey(self, mobile_survey, user=None):
        print 'Creating Couch DB: project_', str(mobile_survey.id)
        db = self.couch.create('project_' + str(mobile_survey.id))

        survey = JSONSerializer().serializeToPython(mobile_survey, exclude='cards')
        survey['type'] = 'metadata'
        db.save(survey)

    def delete_survey(self, mobile_survey_id):
        try:
            print 'Deleting Couch DB: project_', str(mobile_survey_id)
            return self.couch.delete('project_' + str(mobile_survey_id))
        except Exception as e:
            print e
            return connection_error


    def clear_associated_surveys(self):
        surveys = [str(msm['id']) for msm in models.MobileSurveyModel.objects.values("id")]
        couchdbs = [dbname for dbname in self.couch]
        for db in couchdbs:
            survey_id = db[-36:]
            if survey_id in surveys:
                self.delete_survey(survey_id)

    def clear_unassociated_surveys(self):
        surveys = [str(msm['id']) for msm in models.MobileSurveyModel.objects.values("id")]
        couchdbs = [dbname for dbname in couchserver]
        for db in couchdbs:
            survey_id = db[-36:]
            if survey_id not in surveys:
                if 'project' in db:
                    self.delete_survey(survey_id)

    def create_associated_surveys(self):
        for mobile_survey in models.MobileSurveyModel.objects.all():
            print "Creating", mobile_survey
            self.create_survey(mobile_survey)
            print "Populating"
            db = self.couch['project_' + str(mobile_survey.id)]
            self.load_data_into_couch(mobile_survey, db, mobile_survey.lasteditedby)

    def collect_resource_instances_for_couch(self, mobile_survey, user):
        """
        Uses the data definition configs of a mobile survey object to search for
        resource instances relevant to a mobile survey. Takes a user object which
        is required for search.
        """
        query = mobile_survey.datadownloadconfig['custom']
        resource_types = mobile_survey.datadownloadconfig['resources']
        instances = {}
        if query in ('', None) and len(resource_types) == 0:
            print "No resources or data query defined"
        else:
            request = HttpRequest()
            request.user = user
            request.GET['mobiledownload'] = True
            if query in ('', None):
                if len(mobile_survey.bounds.coords) == 0:
                    default_bounds = settings.DEFAULT_BOUNDS
                    default_bounds['features'][0]['properties']['inverted'] = False
                    request.GET['mapFilter'] = json.dumps(default_bounds)
                else:
                    request.GET['mapFilter'] = json.dumps({u'type': u'FeatureCollection', 'features':[{'geometry': json.loads(mobile_survey.bounds.json)}]})
                request.GET['typeFilter'] = json.dumps([{'graphid': resourceid, 'inverted': False } for resourceid in mobile_survey.datadownloadconfig['resources']])
            else:
                parsed = urlparse.urlparse(query)
                urlparams = urlparse.parse_qs(parsed.query)
                for k, v in urlparams.iteritems():
                    request.GET[k] = v[0]
            search_res_json = search.search_results(request)
            search_res = JSONDeserializer().deserialize(search_res_json.content)
            try:
                instances = {hit['_source']['resourceinstanceid']: hit['_source'] for hit in search_res['results']['hits']['hits']}
            except KeyError:
                print 'no instances found in', search_res
        return instances

    def load_tiles_into_couch(self, mobile_survey, db, instances):
        """
        Takes a mobile survey object, a couch database instance, and a dictionary
        of resource instances to identify eligible tiles and load them into the
        database instance
        """
        cards = mobile_survey.cards.all()
        for card in cards:
            tiles = models.TileModel.objects.filter(nodegroup=card.nodegroup_id)
            tiles_serialized = json.loads(JSONSerializer().serialize(tiles))
            for tile in tiles_serialized:
                if str(tile['resourceinstance_id']) in instances:
                    try:
                        tile['type'] = 'tile'
                        couch_record = db.get(tile['tileid'])
                        if couch_record == None:
                            db[tile['tileid']] = tile
                        else:
                            if couch_record['data'] != tile['data']:
                                couch_record['data'] = tile['data']
                                db[tile['tileid']] = couch_record
                    except Exception as e:
                        print e, tile

    def load_instances_into_couch(self, mobile_survey, db, instances):
        """
        Takes a mobile survey object, a couch database instance, and a dictionary
        of resource instances and loads them into the database instance.
        """
        for instanceid, instance in instances.iteritems():
            try:
                instance['type'] = 'resource'
                couch_record = db.get(instanceid)
                if couch_record == None:
                    db[instanceid] = instance
            except Exception as e:
                print e, instance

    def load_data_into_couch(self, mobile_survey, db, user):
        """
        Takes a mobile survey, a couch database intance and a django user and loads
        tile and resource instance data into the couch instance.
        """

        instances = self.collect_resource_instances_for_couch(mobile_survey, user)
        self.load_tiles_into_couch(mobile_survey, db, instances)
        self.load_instances_into_couch(mobile_survey, db, instances)
