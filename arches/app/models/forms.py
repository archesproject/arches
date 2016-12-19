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

import copy
from arches.app.models import models
from arches.app.models.tile import Tile
from arches.app.models.card import Card
from django.utils.translation import ugettext as _
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer

class Form(object):
    def __init__(self, resourceid=None, formid=None):
        self.forms = []
        self.tiles = {}
        self.blanks = {}

        if resourceid or formid:
            self.load(resourceid, formid=formid)

    def load(self, resourceid, formid=None):
        tiles = Tile.objects.filter(resourceinstance_id=resourceid).order_by('sortorder')

        # get the form and card data
        if formid is not None:
            form = models.Form.objects.get(pk=formid)
            formxcards = form.formxcard_set.all()
            form_obj = {
                'id': form.pk,
                'title': form.title,
                'subtitle': form.subtitle
            }
            form_obj['cardgroups'] = []
            for formxcard in formxcards:
                card_obj = JSONSerializer().serializeToPython(Card.objects.get(cardid=formxcard.card_id))
                form_obj['cardgroups'].append(card_obj)
            self.forms = [form_obj]


        # get the actual tile data
        for form in self.forms:
            for cardgroup in form['cardgroups']:
                self.tiles[cardgroup['nodegroup_id']] = JSONSerializer().serializeToPython(tiles.filter(nodegroup_id=cardgroup['nodegroup_id']))

                if len(self.tiles[cardgroup['nodegroup_id']]) > 0:
                    for parentTile in self.tiles[cardgroup['nodegroup_id']]:
                        parentTile['tiles'] = {}
                        for card in cardgroup['cards']:
                            parentTile['tiles'][card['nodegroup_id']] = []
                        for tile in JSONSerializer().serializeToPython(tiles.filter(parenttile_id=parentTile['tileid'])):
                            parentTile['tiles'][str(tile['nodegroup_id'])].append(tile)


        # get the blank tile data
        for form in self.forms:
            for cardgroup in form['cardgroups']:
                # add blank parent tile
                parentTile = JSONSerializer().serializeToPython(Tile())
                parentTile['tileid'] = ''
                parentTile['parenttile_id'] = None
                parentTile['resourceinstance_id'] = resourceid
                parentTile['nodegroup_id'] = cardgroup['nodegroup_id']
                parentTile['tiles'] = {}
                parentTile['data'] = {}
                for widget in cardgroup['widgets']:
                    parentTile['data'][widget['node_id']] = None

                # add a blank tile for the cardgroup
                self.blanks[parentTile['nodegroup_id']] = [parentTile]

                for card in cardgroup['cards']:
                    # make a blank tile
                    tile = JSONSerializer().serializeToPython(Tile())
                    tile['tileid'] = ''
                    tile['parenttile_id'] = None # parentTile
                    tile['resourceinstance_id'] = resourceid
                    tile['nodegroup_id'] = card['nodegroup_id']
                    tile['tiles'] = {}
                    tile['data'] = {}
                    for widget in card['widgets']:
                        tile['data'][widget['node_id']] = None

                    if(card['cardinality'] == '1'):
                        parentTile['tiles'][card['nodegroup_id']] = [tile]
                    else:
                        parentTile['tiles'][card['nodegroup_id']] = []

                    # add a blank tile for each card
                    self.blanks[tile['nodegroup_id']] = [tile]
