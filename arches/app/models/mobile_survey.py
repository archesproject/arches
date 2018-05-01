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
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
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
        self.couch = couchdb.Server(settings.COUCHDB_URL)

    def save(self):
        super(MobileSurvey, self).save()
        if 'project_' + str(self.id) in self.couch:
            db = self.couch['project_' + str(self.id)]
        else:
            db = self.couch.create('project_' + str(self.id))
        survey = self.serialize()
        survey['type'] = 'metadata'
        db.save(survey)

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
                proxy_graph = Graph.objects.get(pk=card.graph_id)
                color = proxy_graph.color
                graph = card.graph
                graph = JSONSerializer().serializeToPython(graph, exclude=['functions','disable_instance_creation','deploymentdate','deploymentfile'])
                graph['color'] = color
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
        db = self.couch['project_' + str(self.id)]
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
