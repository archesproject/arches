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
import itertools
from copy import copy, deepcopy
from django.db import transaction
from arches.app.models import models
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.conf import settings
from django.utils.translation import ugettext as _

class Card(models.CardModel):
    """
    Used for mapping complete card object to and from the database

    """

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(Card, self).__init__(*args, **kwargs)
        self.sub_cards = []
        self.nodegroups = []
        self.nodes = []

        if args:
            if isinstance(args[0], dict):
                pass

            else:
                sub_groups = models.NodeGroup.objects.filter(parentnodegroup=self.nodegroup)
                card_sets = [group.cardmodel_set.all() for group in sub_groups]
                self.sub_cards = list(itertools.chain.from_iterable(card_sets))
                
                nodegroups = [sub_card.nodegroup for sub_card in self.sub_cards]
                self.nodegroups.append(self.nodegroup)

                node_sets = [group.node_set.all() for group in self.nodegroups]
                self.nodes = list(itertools.chain.from_iterable(node_sets))

    def serialize(self):
        """
        serialize to a different form then used by the internal class structure

        """

        ret = JSONSerializer().handle_model(self)
        ret['sub_cards'] = self.sub_cards
        ret['nodegroups'] = self.nodegroups
        ret['nodes'] = self.nodes

        return ret
