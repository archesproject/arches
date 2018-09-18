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

import uuid
import json
import couchdb
from copy import copy, deepcopy
from django.db import transaction
from arches.app.models import models
from arches.app.models.tile import Tile
from arches.app.models.graph import Graph
from arches.app.models.system_settings import settings
from django.http import HttpRequest
from arches.app.utils.couch import Couch
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
import arches.app.views.search as search
from django.utils.translation import ugettext as _

class MobileSurvey(models.MobileSurveyModel):
    """
    Used for mapping complete mobile survey objects to and from the database
    """

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(MobileSurvey, self).__init__(*args, **kwargs)
        # from models.MobileSurveyModel
        # self.id = models.UUIDField(primary_key=True, default=uuid.uuid1)
        # self.name = models.TextField(null=True)
        # self.active = models.BooleanField(default=False)
        # self.createdby = models.ForeignKey(User, related_name='createdby')
        # self.lasteditedby = models.ForeignKey(User, related_name='lasteditedby')
        # self.users = models.ManyToManyField(to=User, through='MobileSurveyXUser')
        # self.groups = models.ManyToManyField(to=Group, through='MobileSurveyXGroup')
        # self.startdate = models.DateField(blank=True, null=True)
        # self.enddate = models.DateField(blank=True, null=True)
        # self.description = models.TextField(null=True)
        # self.bounds = models.MultiPolygonField(null=True)
        # self.tilecache = models.TextField(null=True)
        # self.datadownloadconfig = JSONField(blank=True, null=True, default='{"download":false, "count":1000, "resources":[]}')
        # end from models.MobileSurvey

        self.couch = Couch()

    def save(self):
        super(MobileSurvey, self).save()
        db = self.couch.create_db('project_' + str(self.id))

        survey = self.serialize()
        survey['type'] = 'metadata'
        self.couch.update_doc(db, survey, 'metadata')
        self.load_data_into_couch()
        return db

    def delete(self):
        self.couch.delete_db('project_' + str(self.id))
        super(MobileSurvey, self).delete()

    def serialize(self, fields=None, exclude=None):
        """
        serialize to a different form then used by the internal class structure
        used to append additional values (like parent ontology properties) that
        internal objects (like models.Nodes) don't support
        """
        serializer = JSONSerializer()
        serializer.geom_format = 'geojson'
        obj = serializer.handle_model(self)
        ordered_cards = self.get_ordered_cards()
        ret = JSONSerializer().serializeToPython(obj)
        graphs = []
        graphids = []
        for card in self.cards.all():
            if card.graph_id not in graphids:
                graphids.append(card.graph_id)
                #we may want the full proxy model at some point, but for now just the root node color
                # graphs.append(Graph.objects.get(pk=card.graph_id))
                graph = JSONSerializer().serializeToPython(card.graph, exclude=['functions','disable_instance_creation','deploymentdate','deploymentfile'])
                graph['color'] = card.graph.color
                graph['ontology_id'] = str(graph['ontology_id'])
                graph['template_id'] = str(graph['template_id'])
                graphs.append(graph)
        ret['graphs'] = graphs
        ret['cards'] = ordered_cards
        try:
            ret['bounds'] = json.loads(ret['bounds'])
        except TypeError as e:
            print 'Could not parse', ret['bounds'], e

        return ret

    def get_ordered_cards(self):
        ordered_cards = models.MobileSurveyXCard.objects.filter(mobile_survey=self).order_by('sortorder')
        ordered_card_ids = [unicode(mpc.card_id) for mpc in ordered_cards]
        return ordered_card_ids

    def push_edits_to_db(self):
        # read all docs that have changes
        # save back to postgres db
        db = self.couch.create_db('project_' + str(self.id))
        ret = []
        for row in db.view('_all_docs', include_docs=True):
            ret.append(row)
            if 'tileid' in row.doc:
                tile = Tile(row.doc)
                #if tile.filter_by_perm(request.user, 'write_nodegroup'):
                with transaction.atomic():
                    tile.save()
                #tile = models.TileModel.objects.get(pk=row.doc.tileid).update(**row.doc)
        return ret

    def collect_resource_instances_for_couch(self):
        """
        Uses the data definition configs of a mobile survey object to search for
        resource instances relevant to a mobile survey. Takes a user object which
        is required for search.
        """
        query = self.datadownloadconfig['custom']
        resource_types = self.datadownloadconfig['resources']
        instances = {}
        if query in ('', None) and len(resource_types) == 0:
            print "No resources or data query defined"
        else:
            request = HttpRequest()
            request.user = self.lasteditedby
            request.GET['mobiledownload'] = True
            if query in ('', None):
                if len(self.bounds.coords) == 0:
                    default_bounds = settings.DEFAULT_BOUNDS
                    default_bounds['features'][0]['properties']['inverted'] = False
                    request.GET['mapFilter'] = json.dumps(default_bounds)
                else:
                    request.GET['mapFilter'] = json.dumps({u'type': u'FeatureCollection', 'features':[{'geometry': json.loads(self.bounds.json)}]})
                request.GET['typeFilter'] = json.dumps([{'graphid': resourceid, 'inverted': False } for resourceid in self.datadownloadconfig['resources']])
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

    def load_tiles_into_couch(self, instances):
        """
        Takes a mobile survey object, a couch database instance, and a dictionary
        of resource instances to identify eligible tiles and load them into the
        database instance
        """
        db = self.couch.create_db('project_' + str(self.id))
        cards = self.cards.all()
        for card in cards:
            tiles = models.TileModel.objects.filter(nodegroup=card.nodegroup_id)
            tiles_serialized = json.loads(JSONSerializer().serialize(tiles))
            for tile in tiles_serialized:
                if str(tile['resourceinstance_id']) in instances:
                    try:
                        tile['type'] = 'tile'
                        self.couch.update_doc(db, tile, tile['tileid'])
                        # couch_record = db.get(tile['tileid'])
                        # if couch_record == None:
                        #     db[tile['tileid']] = tile
                        # else:
                        #     if couch_record['data'] != tile['data']:
                        #         couch_record['data'] = tile['data']
                        #         db[tile['tileid']] = couch_record
                    except Exception as e:
                        print e, tile

    def load_instances_into_couch(self, instances):
        """
        Takes a mobile survey object, a couch database instance, and a dictionary
        of resource instances and loads them into the database instance.
        """
        db = self.couch.create_db('project_' + str(self.id))
        for instanceid, instance in instances.iteritems():
            try:
                instance['type'] = 'resource'
                self.couch.update_doc(db, instance, instanceid)
            except Exception as e:
                print e, instance

    def load_data_into_couch(self):
        """
        Takes a mobile survey, a couch database intance and a django user and loads
        tile and resource instance data into the couch instance.
        """
        instances = self.collect_resource_instances_for_couch()
        self.load_tiles_into_couch(instances)
        self.load_instances_into_couch(instances)
