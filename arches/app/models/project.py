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
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.utils.translation import ugettext as _


class Project(models.MobileSurveyModel):
    """
    Used for mapping complete project objects to and from the database

    """

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)
        # from models.MobileSurveyModel
        # self.id = models.UUIDField(primary_key=True, default=uuid.uuid1)
        # self.name = models.TextField(null=True)
        # self.active = models.BooleanField(default=False)
        # self.createdby = models.ForeignKey(User, related_name='createdby')
        # self.lasteditedby = models.ForeignKey(User, related_name='lasteditedby')
        # self.users = models.ManyToManyField(to=User, through='MobileSurveyModelXUser')
        # self.groups = models.ManyToManyField(to=Group, through='MobileSurveyModelXGroup')
        # self.startdate = models.DateField(blank=True, null=True)
        # self.enddate = models.DateField(blank=True, null=True)
        # self.description = models.TextField(null=True)
        # end from models.MobileSurveyModel
        # import ipdb 
        # ipdb.set_trace()
        self.couch = couchdb.Server(settings.COUCHDB_URL)

    def save(self):
        """
        

        """

        #with transaction.atomic():
        super(Project, self).save()
        try:
            db = self.couch['project_' + str(self.id)]
        except couchdb.ResourceNotFound:
            db = self.couch.create('project_' + str(self.id))
            tile = models.TileModel.objects.get(pk='4345f530-aa90-48cf-b4b3-92d1185ca439')
            tile = json.loads(JSONSerializer().serialize(tile))
            print 'herre'
            tile['_id'] = tile['tileid']
            db.save(tile)

        db.save(self.serialize())

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

    def serialize(self):
        """
        serialize to a different form then used by the internal class structure

        used to append additional values (like parent ontology properties) that
        internal objects (like models.Nodes) don't support

        """

        ret = JSONSerializer().handle_model(self)

        return JSONSerializer().serializeToPython(ret)
