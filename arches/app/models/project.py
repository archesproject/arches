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
from django.db import transaction
from arches.app.models import models
from arches.app.models.tile import Tile
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.utils.translation import ugettext as _


class Project(models.MobileProject):
    """
    Used for mapping complete project objects to and from the database
    """

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)
        # from models.MobileProject
        # self.id = models.UUIDField(primary_key=True, default=uuid.uuid1)
        # self.name = models.TextField(null=True)
        # self.active = models.BooleanField(default=False)
        # self.createdby = models.ForeignKey(User, related_name='createdby')
        # self.lasteditedby = models.ForeignKey(User, related_name='lasteditedby')
        # self.users = models.ManyToManyField(to=User, through='MobileProjectXUser')
        # self.groups = models.ManyToManyField(to=Group, through='MobileProjectXGroup')
        # self.startdate = models.DateField(blank=True, null=True)
        # self.enddate = models.DateField(blank=True, null=True)
        # self.description = models.TextField(null=True)
        # end from models.MobileProject

    def save(self):
        #with transaction.atomic():
        super(Project, self).save()

    def serialize(self):
        """
        serialize to a different form then used by the internal class structure
        used to append additional values (like parent ontology properties) that
        internal objects (like models.Nodes) don't support
        """
        obj = JSONSerializer().handle_model(self)
        ordered_cards = self.get_ordered_cards()
        ret = JSONSerializer().serializeToPython(obj)
        ret['cards'] = ordered_cards
        return ret

    def get_ordered_cards(self):
        ordered_cards = models.MobileProjectXCard.objects.filter(mobile_project=self).order_by('sortorder')
        ordered_card_ids = [unicode(mpc.card.cardid) for mpc in ordered_cards]
        return ordered_card_ids
