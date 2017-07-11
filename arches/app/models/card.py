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
from django.db import transaction
from arches.app.models import models
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.forms import ModelForm

class Card(models.CardModel):
    """
    Used for mapping complete card object to and from the database

    """

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        """
        Init a Card from a dictionary representation of from a model method call

        init this object by using Django query syntax, eg:
        .. code-block:: python

            Card.objects.get(pk=some_card_id)
            # or
            Card.objects.filter(name=some_value_to_filter_by)

        OR, init this object with a dictionary, eg:
        .. code-block:: python

            Card({
                name:'some name',
                cardid: '12341234-1234-1234-1324-1234123433433',
                ...
            })

        Arguments:
        args -- a dictionary of properties repsenting a Card object
        kwargs -- unused

        """

        super(Card, self).__init__(*args, **kwargs)
        # from models.CardModel
        # self.cardid
        # self.name
        # self.description
        # self.instructions
        # self.helpenabled
        # self.helptitle
        # self.helptext
        # self.nodegroup
        # self.graph
        # self.active
        # self.visible
        # self.sortorder
        # end from models.CardModel
        self.cardinality = ''
        self.cards = []
        self.widgets = []
        self.nodes = []
        self.ontologyproperty = None

        if args:
            if isinstance(args[0], dict):
                for key, value in args[0].iteritems():
                    if not (key == 'cards' or key == 'widgets' or key == 'nodes'):
                        setattr(self, key, value)

                for card in args[0]["cards"]:
                    self.cards.append(Card(card))

                for widget in args[0]["widgets"]:
                    widget_model = models.CardXNodeXWidget()
                    widget_model.pk = widget.get('id', None)
                    widget_model.node_id = widget.get('node_id', None)
                    widget_model.card_id = widget.get('card_id', None)
                    widget_model.widget_id = widget.get('widget_id', None)
                    widget_model.config = widget.get('config', {})
                    widget_model.label = widget.get('label', '')
                    widget_model.sortorder = widget.get('sortorder', None)
                    if widget_model.pk == None:
                        widget_model.save()
                    self.widgets.append(widget_model)

                for node in args[0]["nodes"]:
                    nodeid = node.get('nodeid', None)
                    if nodeid is not None:
                        node_model = models.Node.objects.get(nodeid=nodeid)
                        node_model.config = node.get('config', None)
                        self.nodes.append(node_model)

            else:
                self.widgets = list(self.cardxnodexwidget_set.all())

                sub_groups = models.NodeGroup.objects.filter(parentnodegroup=self.nodegroup)
                for sub_group in sub_groups:
                    self.cards.extend(Card.objects.filter(nodegroup=sub_group))

                self.cardinality = self.nodegroup.cardinality

    def save(self):
        """
        Saves an a card and it's parent ontology property back to the db

        """

        with transaction.atomic():
            if self.graph.ontology and self.graph.isresource:
                edge = self.get_edge_to_parent()
                edge.ontologyproperty = self.ontologyproperty
                edge.save()

            self.nodegroup.cardinality = self.cardinality
            self.nodegroup.save()

            super(Card, self).save()
            for widget in self.widgets:
                widget.save()
            for node in self.nodes:
                node.save()
            for card in self.cards:
                card.save()

        return self

    def get_edge_to_parent(self):
        """
        Finds the edge model that relates this card to it's parent node

        """
        return models.Edge.objects.get(rangenode_id=self.nodegroup_id)

    def filter_by_perm(self, user, perm):
        """
        Filters out any cards that don't have the permission for the user

        Arguments:
        user -- the user object to check permsission against
        perm -- the permission string to check (eg: 'read_nodegroup')

        """

        if user:
            if user.has_perm(perm, self.nodegroup):
                cards = []
                for card in self.cards:
                    if user.has_perm(perm, card.nodegroup):
                        cards.append(card)
                self.cards = cards
            else:
                return None
        return self

    def serialize(self):
        """
        serialize to a different form then used by the internal class structure

        """

        ret = JSONSerializer().handle_model(self)
        ret['cardinality'] = self.cardinality
        ret['cards'] = self.cards
        ret['nodes'] = list(self.nodegroup.node_set.all())
        ret['visible'] = self.visible
        ret['active'] = self.active
        ret['widgets'] = self.widgets
        ret['ontologyproperty'] = self.ontologyproperty

        if self.graph and self.graph.ontology and self.graph.isresource:
            edge = self.get_edge_to_parent()
            ret['ontologyproperty'] = edge.ontologyproperty

        # provide a models.CardXNodeXWidget model for every node
        # even if a widget hasn't been configured
        for node in ret['nodes']:
            found = False
            for widget in ret['widgets']:
                if node.nodeid == widget.node_id:
                    found = True
            if not found:
                widget = models.DDataType.objects.get(pk=node.datatype).defaultwidget
                if widget:
                    widget_model = models.CardXNodeXWidget()
                    widget_model.node_id = node.nodeid
                    widget_model.card_id = self.cardid
                    widget_model.widget_id = widget.pk
                    widget_model.config = JSONSerializer().serialize(widget.defaultconfig)
                    widget_model.label = node.name
                    ret['widgets'].append(widget_model)

        return ret


class CardXNodeXWidgetForm(ModelForm):
    class Meta:
        model = models.CardXNodeXWidget
        fields = '__all__'
