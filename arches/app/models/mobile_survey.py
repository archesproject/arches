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
import urlparse
import logging
from datetime import datetime
from datetime import timedelta
from copy import copy, deepcopy
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpRequest
from django.utils.translation import ugettext as _
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.models import models
from arches.app.models.concept import Concept
from arches.app.models.tile import Tile
from arches.app.models.card import Card
from arches.app.models.graph import Graph
from arches.app.models.models import ResourceInstance
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from arches.app.utils.geo_utils import GeoUtils
from arches.app.utils.couch import Couch
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
import arches.app.views.search as search

logger = logging.getLogger(__name__)


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
        # self.onlinebasemaps = JSONField(blank=True, null=True, db_column='onlinebasemaps')
        # self.datadownloadconfig = JSONField(blank=True, null=True, default='{"download":false, "count":1000, "resources":[]}')
        # end from models.MobileSurvey

        self.couch = Couch()

    def save(self):
        super(MobileSurvey, self).save()
        if self.datadownloadconfig['download'] and self.active:
            self.load_data_into_couch()
        else:
            # remove all docs by first deleting and then recreating the database
            try:
                self.couch.delete_db('project_' + str(self.id))
            except:
                pass

        db = self.couch.create_db('project_' + str(self.id))
        return db

    def delete(self):
        try:
            self.couch.delete_db('project_' + str(self.id))
        except Exception as e:
            print(e), _("Could not delete database in CouchDB")
        super(MobileSurvey, self).delete()

    def collect_card_widget_node_data(self, graph_obj, graph, parentcard, nodegroupids=[]):
        nodegroupids.append(str(parentcard.nodegroup_id))
        for node in graph_obj['nodes']:
            if node['nodegroup_id'] == str(parentcard.nodegroup_id):
                found = False
                for widget in graph_obj['widgets']:
                    if node['nodeid'] == str(widget.node_id):
                        found = True
                        try:
                            collection_id = node['config']['rdmCollection']
                            concept_collection = Concept().get_child_collections_hierarchically(collection_id, offset=None)
                            widget.config['options'] = concept_collection
                        except Exception as e:
                            pass
                        break
                if not found:
                    for card in graph_obj['cards']:
                        if card['nodegroup_id'] == node['nodegroup_id']:
                            widget = models.DDataType.objects.get(pk=node['datatype']).defaultwidget
                            if widget:
                                widget_model = models.CardXNodeXWidget()
                                widget_model.node_id = node['nodeid']
                                widget_model.card_id = card['cardid']
                                widget_model.widget_id = widget.pk
                                widget_model.config = widget.defaultconfig
                                try:
                                    collection_id = node['config']['rdmCollection']
                                    if collection_id:
                                        concept_collection = Concept().get_child_collections_hierarchically(collection_id, offset=None)
                                        widget_model.config['options'] = concept_collection
                                except Exception as e:
                                    pass
                                widget_model.label = node['name']
                                graph_obj['widgets'].append(widget_model)
                            break

                if node['datatype'] == 'resource-instance' or node['datatype'] == 'resource-instance-list':
                    if node['config']['graphid'] is not None:
                        try:
                            graphuuid = uuid.UUID(node['config']['graphid'][0])
                            graph_id = unicode(graphuuid)
                        except ValueError as e:
                            graphuuid = uuid.UUID(node['config']['graphid'])
                            graph_id = unicode(graphuuid)
                        node['config']['options'] = []
                        for resource_instance in Resource.objects.filter(graph_id=graph_id):
                            node['config']['options'].append({'id': str(resource_instance.pk), 'name': resource_instance.displayname})

        for subcard in parentcard.cards:
            self.collect_card_widget_node_data(graph_obj, graph, subcard, nodegroupids)

        return graph_obj

    def serialize_for_mobile(self):
        """
        serialize to a different form than used by the internal class structure
        used to append additional values (like parent ontology properties) that
        internal objects (like models.Nodes) don't support
        """
        serializer = JSONSerializer()
        serializer.geom_format = 'geojson'
        obj = serializer.handle_model(self)
        ordered_cards = self.get_ordered_cards()
        expired = False
        try:
            expired = (datetime.strptime(str(self.enddate), '%Y-%m-%d') - datetime.now() + timedelta(hours=24)).days < 0
        except ValueError:
            pass
        ret = JSONSerializer().serializeToPython(obj)
        if expired is True:
            self.active = False
            super(MobileSurvey, self).save()
            ret['active'] = False
        graphs = []
        card_lookup = {}
        for card in self.cards.all():
            if str(card.graph_id) in card_lookup:
                card_lookup[str(card.graph_id)].append(card)
            else:
                card_lookup[str(card.graph_id)] = [card]
        for graphid, cards in iter(card_lookup.items()):
            graph = Graph.objects.get(pk=graphid)
            graph_obj = graph.serialize(exclude=['domain_connections', 'edges', 'relatable_resource_model_ids'])
            graph_obj['widgets'] = list(models.CardXNodeXWidget.objects.filter(card__graph=graph).distinct())
            nodegroupids = []
            for card in cards:
                topcard = Card.objects.get(pk=card.cardid)
                self.collect_card_widget_node_data(graph_obj, graph, topcard, nodegroupids)
            graph_obj['widgets'] = serializer.serializeToPython(graph_obj['widgets'])

            nodegroup_filters = {'nodes': 'nodegroup_id', 'cards': 'nodegroup_id', 'nodegroups': 'nodegroupid'}

            for prop, id in iter(nodegroup_filters.items()):
                relevant_items = [item for item in graph_obj[prop] if item[id] in nodegroupids]
                graph_obj[prop] = relevant_items

            relevant_cardids = [card['cardid'] for card in graph_obj['cards']]
            relevant_widgets = [widget for widget in graph_obj['widgets'] if str(widget['card_id']) in relevant_cardids]
            graph_obj['widgets'] = relevant_widgets

            graphs.append(serializer.serializeToPython(graph_obj))

        ret['graphs'] = graphs
        ret['cards'] = ordered_cards
        try:
            bounds = json.loads(ret['bounds'])
            ret['bounds'] = bounds
            if (bounds['type'] == 'MultiPolygon'):
                singlepart = GeoUtils().convert_multipart_to_singlepart(bounds)
                ret['bounds'] = singlepart
        except TypeError as e:
            logger.error('Could not parse {0}, {1}'.format(ret['bounds'], e))
        return ret

    def serialize(self, fields=None, exclude=None):
        """
        serialize to a different form than used by the internal class structure
        used to append additional values (like parent ontology properties) that
        internal objects (like models.Nodes) don't support
        """
        serializer = JSONSerializer()
        serializer.geom_format = 'geojson'
        obj = serializer.handle_model(self)
        ordered_cards = self.get_ordered_cards()
        ret = JSONSerializer().serializeToPython(obj)
        ret['cards'] = ordered_cards
        try:
            bounds = json.loads(ret['bounds'])
            ret['bounds'] = bounds
            if (bounds['type'] == 'MultiPolygon'):
                singlepart = GeoUtils().convert_multipart_to_singlepart(bounds)
                ret['bounds'] = singlepart
        except TypeError as e:
            print 'Could not parse', ret['bounds'], e
        return ret

    def get_ordered_cards(self):
        ordered_cards = models.MobileSurveyXCard.objects.filter(mobile_survey=self).order_by('sortorder')
        ordered_card_ids = [unicode(mpc.card_id) for mpc in ordered_cards]
        return ordered_card_ids

    def handle_reviewer_edits(self, user, tile):
        if hasattr(user, 'userprofile') is not True:
            models.UserProfile.objects.create(user=user)
        if user.userprofile.is_reviewer():
            user_id = str(user.id)
            if tile.provisionaledits:
                if user_id in tile.provisionaledits:
                    tile.provisionaledits.pop(user_id, None)

    def get_provisional_edit(self, doc, tile, sync_user_id, db):
        if doc['provisionaledits'] != '':
            if sync_user_id in doc['provisionaledits']:
                user_edit = doc['provisionaledits'][sync_user_id]
                for nodeid, value in iter(user_edit['value'].items()):
                    datatype_factory = DataTypeFactory()
                    node = models.Node.objects.get(nodeid=nodeid)
                    datatype = datatype_factory.get_instance(node.datatype)
                    newvalue = datatype.process_mobile_data(tile, node, db, doc, value)
                    if newvalue is not None:
                        user_edit['value'][nodeid] = newvalue
                return user_edit['value']
        else:
            return None

    def check_if_revision_exists(self, doc):
        res = False
        if doc['type'] == 'resource':
            res = models.ResourceRevisionLog.objects.filter(revisionid=doc['_rev']).exists()
        elif doc['type'] == 'tile':
            res = models.TileRevisionLog.objects.filter(revisionid=doc['_rev']).exists()
        return res

    def save_revision_log(self, doc, synclog, action):
        if doc['type'] == 'resource':
            revisionlog = models.ResourceRevisionLog(
                    resourceid=doc['resourceinstanceid'],
                )
        elif doc['type'] == 'tile':
            revisionlog = models.TileRevisionLog(
                    tileid=doc['tileid'],
                    resourceid=doc['resourceinstance_id']
                )
        revisionlog.survey = self
        revisionlog.revisionid = doc['_rev']
        revisionlog.synclog = synclog
        revisionlog.action = action
        revisionlog.save()

    def push_edits_to_db(self, synclog=None, userid=None):
        # read all docs that have changes
        # save back to postgres db
        db = self.couch.create_db('project_' + str(self.id))
        user_lookup = {}
        is_reviewer = False
        sync_user = None
        sync_user_id = None
        if userid is not None:
            sync_user = User.objects.get(pk=userid)
            sync_user_id = str(sync_user.id)
        with transaction.atomic():
            couch_docs = self.couch.all_docs(db)
            for row in couch_docs:
                if row.doc['type'] == 'resource':
                    if self.check_if_revision_exists(row.doc) is False:
                        if 'provisional_resource' in row.doc and row.doc['provisional_resource'] == 'true':
                            resourceinstance, created = ResourceInstance.objects.update_or_create(
                                resourceinstanceid=uuid.UUID(str(row.doc['resourceinstanceid'])),
                                defaults={
                                    'graph_id': uuid.UUID(str(row.doc['graph_id']))
                                }
                            )
                            if created is True:
                                self.save_revision_log(row.doc, synclog, 'create')
                            else:
                                self.save_revision_log(row.doc, synclog, 'update')

                            logger.info('Resource {0} saved by {1}'.format(row.doc['resourceinstanceid'], sync_user.username))

            for row in couch_docs:
                if row.doc['type'] == 'tile' and \
                        ResourceInstance.objects.filter(pk=row.doc['resourceinstance_id']).exists():
                    if self.check_if_revision_exists(row.doc) is False:
                        if 'provisionaledits' in row.doc and row.doc['provisionaledits'] is not None:
                            action = 'update'
                            try:
                                tile = Tile.objects.get(tileid=row.doc['tileid'])
                                prov_edit = self.get_provisional_edit(row.doc, tile, sync_user_id, db)
                                if prov_edit is not None:
                                    tile.data = prov_edit

                                # If there are conflicting documents, lets clear those out
                                if '_conflicts' in row.doc:
                                    for conflict_rev in row.doc['_conflicts']:
                                        conflict_data = db.get(row.id, rev=conflict_rev)
                                        if conflict_data['provisionaledits'] != '' and \
                                                conflict_data['provisionaledits'] is not None:
                                            if sync_user_id in conflict_data['provisionaledits']:
                                                tile.data = conflict_data['provisionaledits'][sync_user_id]['value']
                                        # Remove conflicted revision from couch
                                        db.delete(conflict_data)

                            except Tile.DoesNotExist:
                                action = 'create'
                                tile = Tile(row.doc)
                                prov_edit = self.get_provisional_edit(row.doc, tile, sync_user_id, db)
                                if prov_edit is not None:
                                    tile.data = prov_edit
                            self.handle_reviewer_edits(sync_user, tile)
                            tile.save(user=sync_user)
                            self.save_revision_log(row.doc, synclog, action)
                            logger.info('Tile {0} saved by {1}'.format(row.doc['tileid'], sync_user.username))
                            db.compact()

    def append_to_instances(self, request, instances, resource_type_id):
        search_res_json = search.search_results(request)
        search_res = JSONDeserializer().deserialize(search_res_json.content)
        for hit in search_res['results']['hits']['hits']:
            if hit['_type'] == resource_type_id and len(instances.keys()) < int(self.datadownloadconfig['count']):
                instances[hit['_source']['resourceinstanceid']] = hit['_source']

    def collect_resource_instances_for_couch(self):
        """
        Uses the data definition configs of a mobile survey object to search for
        resource instances relevant to a mobile survey. Takes a user object which
        is required for search.
        """
        query = self.datadownloadconfig['custom']
        resource_types = self.datadownloadconfig['resources']
        all_instances = {}
        if query in ('', None) and len(resource_types) == 0:
            print("No resources or data query defined")
        else:
            request = HttpRequest()
            request.user = self.lasteditedby
            request.GET['mobiledownload'] = True
            request.GET['resourcecount'] = self.datadownloadconfig['count']
            if query in ('', None):
                if len(self.bounds.coords) == 0:
                    default_bounds = settings.DEFAULT_BOUNDS
                    default_bounds['features'][0]['properties']['inverted'] = False
                    map_filter = json.dumps(default_bounds)
                else:
                    map_filter = json.dumps({u'type': u'FeatureCollection', 'features': [
                                            {'geometry': json.loads(self.bounds.json)}]})
                try:
                    for res_type in resource_types:
                        instances = {}
                        request.GET['typeFilter'] = json.dumps([{'graphid': res_type, 'inverted': False}])
                        request.GET['mapFilter'] = map_filter
                        request.GET['resourcecount'] = self.datadownloadconfig['count']
                        self.append_to_instances(request, instances, res_type)
                        if len(instances.keys()) < int(self.datadownloadconfig['count']):
                            request.GET['mapFilter'] = '{}'
                            request.GET['resourcecount'] = int(
                                self.datadownloadconfig['count']) - len(instances.keys())
                            self.append_to_instances(request, instances, res_type)
                        for key, value in instances.iteritems():
                            all_instances[key] = value
                except KeyError:
                    print 'no instances found in', search_res
            else:
                try:
                    instances = {}
                    parsed = urlparse.urlparse(query)
                    urlparams = urlparse.parse_qs(parsed.query)
                    for k, v in urlparams.iteritems():
                        request.GET[k] = v[0]
                    search_res_json = search.search_results(request)
                    search_res = JSONDeserializer().deserialize(search_res_json.content)
                    for hit in search_res['results']['hits']['hits']:
                        instances[hit['_source']['resourceinstanceid']] = hit['_source']
                    for key, value in instances.iteritems():
                        all_instances[key] = value
                except KeyError:
                    print 'no instances found in', search_res
        return all_instances

    def load_tiles_into_couch(self, instances, nodegroup):
        """
        Takes a mobile survey object, a couch database instance, and a dictionary
        of resource instances to identify eligible tiles and load them into the
        database instance
        """
        db = self.couch.create_db('project_' + str(self.id))
        tiles = models.TileModel.objects.filter(nodegroup=nodegroup)
        tiles_serialized = json.loads(JSONSerializer().serialize(tiles))
        for tile in tiles_serialized:
            if str(tile['resourceinstance_id']) in instances:
                try:
                    tile['type'] = 'tile'
                    self.couch.update_doc(db, tile, tile['tileid'])
                except Exception as e:
                    print e, tile
        nodegroups = models.NodeGroup.objects.filter(parentnodegroup=nodegroup)
        for nodegroup in nodegroups:
            self.load_tiles_into_couch(instances, nodegroup)

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
        cards = self.cards.all()
        for card in cards:
            self.load_tiles_into_couch(instances, card.nodegroup)
        self.load_instances_into_couch(instances)
