"""
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
"""

import io
import uuid
import json
import urllib.parse
import logging
import traceback
from PIL import Image
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
from arches.app.models.models import MobileSyncLog
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from arches.app.utils.geo_utils import GeoUtils
from arches.app.utils.couch import Couch
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.permission_backend import user_is_resource_reviewer
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Terms, Query
from arches.app.search.mappings import RESOURCES_INDEX
import arches.app.views.search as search
import arches.app.utils.task_management as task_management

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
        if self.datadownloadconfig["download"] and self.active:
            self.load_data_into_couch(initializing_couch=True)
        else:
            # remove all docs by first deleting and then recreating the database
            try:
                self.couch.delete_db("project_" + str(self.id))
            except:
                pass

        db = self.couch.create_db("project_" + str(self.id))
        return db

    def delete(self):
        try:
            self.couch.delete_db("project_" + str(self.id))
        except Exception as e:
            print(e, _("Could not delete database in CouchDB"))
        super(MobileSurvey, self).delete()

    def collect_card_widget_node_data(self, graph_obj, graph, parentcard, nodegroupids=[]):
        nodegroupids.append(str(parentcard.nodegroup_id))
        for node in graph_obj["nodes"]:
            if node["nodegroup_id"] == str(parentcard.nodegroup_id):
                found = False
                for widget in graph_obj["widgets"]:
                    if node["nodeid"] == str(widget.node_id):
                        found = True
                        try:
                            collection_id = node["config"]["rdmCollection"]
                            concept_collection = Concept().get_child_collections_hierarchically(collection_id, offset=None)
                            widget.config["options"] = concept_collection
                        except Exception as e:
                            pass
                        break
                if not found:
                    for card in graph_obj["cards"]:
                        if card["nodegroup_id"] == node["nodegroup_id"]:
                            widget = models.DDataType.objects.get(pk=node["datatype"]).defaultwidget
                            if widget:
                                widget_model = models.CardXNodeXWidget()
                                widget_model.node_id = node["nodeid"]
                                widget_model.card_id = card["cardid"]
                                widget_model.widget_id = widget.pk
                                widget_model.config = widget.defaultconfig
                                try:
                                    collection_id = node["config"]["rdmCollection"]
                                    if collection_id:
                                        concept_collection = Concept().get_child_collections_hierarchically(collection_id, offset=None)
                                        widget_model.config["options"] = concept_collection
                                except Exception as e:
                                    pass
                                widget_model.label = node["name"]
                                graph_obj["widgets"].append(widget_model)
                            break

                if node["datatype"] == "resource-instance" or node["datatype"] == "resource-instance-list":
                    if node["config"]["graphs"] is not None:
                        graph_ids = []
                        for graph in node["config"]["graphs"]:
                            graphuuid = uuid.UUID(graph["graphid"])
                            graph_ids.append(str(graphuuid))
                        node["config"]["options"] = []
                        for resource_instance in Resource.objects.filter(graph_id__in=graph_ids):
                            node["config"]["options"].append(
                                {
                                    "id": str(resource_instance.pk),
                                    "name": resource_instance.displayname,
                                    "graphid": str(resource_instance.graph_id),
                                }
                            )

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
        serializer.geom_format = "geojson"
        obj = serializer.handle_model(self)
        ordered_cards = self.get_ordered_cards()
        expired = False
        try:
            expired = (datetime.strptime(str(self.enddate), "%Y-%m-%d") - datetime.now() + timedelta(hours=24)).days < 0
        except ValueError:
            pass
        ret = JSONSerializer().serializeToPython(obj)
        if expired is True:
            self.active = False
            super(MobileSurvey, self).save()
            ret["active"] = False
        graphs = []
        card_lookup = {}
        for card in self.cards.all():
            if str(card.graph_id) in card_lookup:
                card_lookup[str(card.graph_id)].append(card)
            else:
                card_lookup[str(card.graph_id)] = [card]
        for graphid, cards in iter(list(card_lookup.items())):
            graph = Graph.objects.get(pk=graphid)
            graph_obj = graph.serialize(exclude=["domain_connections", "edges", "relatable_resource_model_ids"])
            graph_obj["widgets"] = list(models.CardXNodeXWidget.objects.filter(card__graph=graph).distinct())
            nodegroupids = []
            for card in cards:
                topcard = Card.objects.get(pk=card.cardid)
                self.collect_card_widget_node_data(graph_obj, graph, topcard, nodegroupids)
            graph_obj["widgets"] = serializer.serializeToPython(graph_obj["widgets"])

            nodegroup_filters = {"nodes": "nodegroup_id", "cards": "nodegroup_id", "nodegroups": "nodegroupid"}

            for prop, id in iter(list(nodegroup_filters.items())):
                relevant_items = [item for item in graph_obj[prop] if item[id] in nodegroupids]
                graph_obj[prop] = relevant_items

            relevant_cardids = [card["cardid"] for card in graph_obj["cards"]]
            relevant_widgets = [widget for widget in graph_obj["widgets"] if str(widget["card_id"]) in relevant_cardids]
            graph_obj["widgets"] = relevant_widgets

            graphs.append(serializer.serializeToPython(graph_obj))

        ret["graphs"] = graphs
        ret["cards"] = ordered_cards
        ret["image_size_limits"] = settings.MOBILE_IMAGE_SIZE_LIMITS
        try:
            bounds = json.loads(ret["bounds"])
            ret["bounds"] = bounds
            if bounds["type"] == "MultiPolygon":
                singlepart = GeoUtils().convert_multipart_to_singlepart(bounds)
                ret["bounds"] = singlepart
        except TypeError as e:
            logger.error("Could not parse {0}, {1}".format(ret["bounds"], e))
        return ret

    def serialize(self, fields=None, exclude=None):
        """
        serialize to a different form than used by the internal class structure
        used to append additional values (like parent ontology properties) that
        internal objects (like models.Nodes) don't support
        """
        serializer = JSONSerializer()
        serializer.geom_format = "geojson"
        obj = serializer.handle_model(self)
        ordered_cards = self.get_ordered_cards()
        ret = JSONSerializer().serializeToPython(obj)
        ret["cards"] = ordered_cards
        try:
            bounds = json.loads(ret["bounds"])
            ret["bounds"] = bounds
            if bounds["type"] == "MultiPolygon":
                singlepart = GeoUtils().convert_multipart_to_singlepart(bounds)
                ret["bounds"] = singlepart
        except TypeError as e:
            print("Could not parse", ret["bounds"], e)
        return ret

    def get_ordered_cards(self):
        ordered_cards = models.MobileSurveyXCard.objects.filter(mobile_survey=self).order_by("sortorder")
        ordered_card_ids = [str(mpc.card_id) for mpc in ordered_cards]
        return ordered_card_ids

    def handle_reviewer_edits(self, user, tile):
        if hasattr(user, "userprofile") is not True:
            models.UserProfile.objects.create(user=user)
        if user_is_resource_reviewer(user):
            user_id = str(user.id)
            if tile.provisionaledits:
                tile.provisionaledits.pop(user_id, None)

    def get_provisional_edit(self, doc, tile, sync_user_id, db):
        if doc["provisionaledits"] != "":
            if sync_user_id in doc["provisionaledits"]:
                user_edit = doc["provisionaledits"][sync_user_id]
                for nodeid, value in iter(list(user_edit["value"].items())):
                    datatype_factory = DataTypeFactory()
                    node = models.Node.objects.get(nodeid=nodeid)
                    datatype = datatype_factory.get_instance(node.datatype)
                    newvalue = datatype.process_mobile_data(tile, node, db, doc, value)
                    if newvalue is not None:
                        user_edit["value"][nodeid] = newvalue
                return user_edit["value"]
        else:
            return None

    def check_if_revision_exists(self, doc):
        res = False
        if doc["type"] == "resource":
            res = models.ResourceRevisionLog.objects.filter(revisionid=doc["_rev"]).exists()
        elif doc["type"] == "tile":
            res = models.TileRevisionLog.objects.filter(revisionid=doc["_rev"]).exists()
        return res

    def save_revision_log(self, doc, synclog, action):
        if doc["type"] == "resource":
            revisionlog = models.ResourceRevisionLog(resourceid=doc["resourceinstanceid"])
        elif doc["type"] == "tile":
            revisionlog = models.TileRevisionLog(tileid=doc["tileid"], resourceid=doc["resourceinstance_id"])
        revisionlog.survey = self
        revisionlog.revisionid = doc["_rev"]
        revisionlog.synclog = synclog
        revisionlog.action = action
        revisionlog.save()

    def check_if_resource_deleted(self, doc):
        return models.EditLog.objects.filter(resourceinstanceid=doc["resourceinstanceid"], edittype="delete").exists()

    def check_if_tile_deleted(self, doc):
        return models.EditLog.objects.filter(tileinstanceid=doc["tileid"], edittype="tile delete").exists()

    def sync(self, userid=None, use_celery=True):
        # delegates the _sync process to celery or to be directly invoked
        synclog = MobileSyncLog(userid=userid, survey=self, status="PROCESSING")
        synclog.save()
        logger.info("Starting sync for userid {0}".format(userid))
        res = None
        if use_celery:
            celery_worker_running = task_management.check_if_celery_available()
            if celery_worker_running is True:
                import arches.app.tasks as tasks

                tasks.sync.apply_async(
                    (self.id, userid, synclog.pk), link=tasks.update_user_task_record.s(), link_error=tasks.log_error.s()
                )
            else:
                err = _("Celery appears not to be running, you need to have celery running in order to sync from Arches Collector.")
                self._sync_failed(synclog, userid, Exception(err))
        else:
            self._sync(synclog.pk, userid=userid)
        return synclog

    def _sync(self, synclogid, userid=None):
        # core function that manages the syncing of data between CouchDB and Postgres
        try:
            synclog = MobileSyncLog.objects.get(pk=synclogid)
            self.push_edits_to_db(synclog, userid)
            self.load_data_into_couch()
            self._sync_succeeded(synclog, userid)
        except Exception as err:
            self._sync_failed(synclog, userid, err)

    def _sync_succeeded(self, synclog, userid):
        logger.info("Sync complete for userid {0}".format(userid))
        synclog.status = "FINISHED"
        synclog.message = _("Sync Completed")
        synclog.save()

    def _sync_failed(self, synclog, userid, err=None):
        msg = str(err) + "\n"
        for tb in traceback.format_tb(err.__traceback__):
            msg += tb
        logger.warning(f"Sync failed for userid {userid}, with error: \n{msg}")
        synclog.status = "FAILED"
        synclog.message = err
        synclog.save()

    def push_edits_to_db(self, synclog, userid=None):
        # read all docs that have changes
        # save back to postgres db
        synclog.message = _("Pushing Edits to Arches")
        synclog.save()
        db = self.couch.create_db("project_" + str(self.id))
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
                if row.doc["type"] == "resource":
                    if self.check_if_revision_exists(row.doc) is False and self.check_if_resource_deleted(row.doc) is False:
                        if "provisional_resource" in row.doc and row.doc["provisional_resource"] == "true":
                            resourceinstance, created = ResourceInstance.objects.update_or_create(
                                resourceinstanceid=uuid.UUID(str(row.doc["resourceinstanceid"])),
                                defaults=dict(graph_id=uuid.UUID(str(row.doc["graph_id"]))),
                            )
                            if created is True:
                                print(f"ResourceInstance created: {resourceinstance.pk}")
                                self.save_revision_log(row.doc, synclog, "create")
                            else:
                                print(f"ResourceInstance updated: {resourceinstance.pk}")
                                self.save_revision_log(row.doc, synclog, "update")

                            print("Resource {0} Saved".format(row.doc["resourceinstanceid"]))
                    else:
                        print("{0}: already saved".format(row.doc["_rev"]))

            for row in couch_docs:
                if row.doc["type"] == "tile" and ResourceInstance.objects.filter(pk=row.doc["resourceinstance_id"]).exists():
                    if self.check_if_revision_exists(row.doc) is False and self.check_if_tile_deleted(row.doc) is False:
                        if "provisionaledits" in row.doc and row.doc["provisionaledits"] is not None:
                            action = "update"
                            try:
                                tile = Tile.objects.get(tileid=row.doc["tileid"])
                                prov_edit = self.get_provisional_edit(row.doc, tile, sync_user_id, db)
                                if prov_edit is not None:
                                    tile.data = prov_edit

                                # If there are conflicting documents, lets clear those out
                                if "_conflicts" in row.doc:
                                    for conflict_rev in row.doc["_conflicts"]:
                                        conflict_data = db.get(row.id, rev=conflict_rev)
                                        if conflict_data["provisionaledits"] != "" and conflict_data["provisionaledits"] is not None:
                                            if sync_user_id in conflict_data["provisionaledits"]:
                                                tile.data = conflict_data["provisionaledits"][sync_user_id]["value"]
                                        # Remove conflicted revision from couch
                                        db.delete(conflict_data)

                            except Tile.DoesNotExist:
                                action = "create"
                                tile = Tile(row.doc)
                                prov_edit = self.get_provisional_edit(row.doc, tile, sync_user_id, db)
                                if prov_edit is not None:
                                    tile.data = prov_edit

                            self.handle_reviewer_edits(sync_user, tile)
                            tile.save(user=sync_user)
                            self.save_revision_log(row.doc, synclog, action)
                            print("Tile {0} Saved".format(row.doc["tileid"]))
                            db.compact()

    def append_to_instances(self, request, instances, resource_type_id):
        search_res_json = search.search_results(request)
        search_res = JSONDeserializer().deserialize(search_res_json.content)
        try:
            for hit in search_res["results"]["hits"]["hits"]:
                if hit["_source"]["graph_id"] == resource_type_id and len(list(instances)) < int(self.datadownloadconfig["count"]):
                    instances[hit["_source"]["resourceinstanceid"]] = hit["_source"]
        except Exception as e:
            print(e)

    def collect_resource_instances_for_couch(self):
        """
        Uses the data definition configs of a mobile survey object to search for
        resource instances relevant to a mobile survey. Takes a user object which
        is required for search.
        """

        query = self.datadownloadconfig["custom"]
        resource_types = self.datadownloadconfig["resources"]
        all_instances = {}
        if query in ("", None) and len(resource_types) == 0:
            logger.info("No resources or data query defined")
        else:
            resources_in_couch = set()
            resources_in_couch_by_type = {}
            for res_type in resource_types:
                resources_in_couch_by_type[res_type] = []

            db = self.couch.create_db("project_" + str(self.id))
            couch_query = {"selector": {"type": "resource"}, "fields": ["_id", "graph_id"]}
            for doc in db.find(couch_query):
                resources_in_couch.add(doc["_id"])
                resources_in_couch_by_type[doc["graph_id"]].append(doc["_id"])

            if self.datadownloadconfig["download"]:
                request = HttpRequest()
                request.user = self.lasteditedby
                request.GET["mobiledownload"] = True
                if query in ("", None):
                    if len(self.bounds.coords) == 0:
                        default_bounds = settings.DEFAULT_BOUNDS
                        default_bounds["features"][0]["properties"]["inverted"] = False
                        map_filter = json.dumps(default_bounds)
                    else:
                        map_filter = json.dumps({"type": "FeatureCollection", "features": [{"geometry": json.loads(self.bounds.json)}]})
                    try:
                        for res_type in resource_types:
                            instances = {}
                            request.GET["resource-type-filter"] = json.dumps([{"graphid": res_type, "inverted": False}])
                            request.GET["map-filter"] = map_filter
                            request.GET["paging-filter"] = "1"
                            request.GET["resourcecount"] = int(self.datadownloadconfig["count"]) - len(resources_in_couch_by_type[res_type])
                            self.append_to_instances(request, instances, res_type)
                            if len(list(instances.keys())) < request.GET["resourcecount"]:
                                request.GET["map-filter"] = "{}"
                                request.GET["resourcecount"] = request.GET["resourcecount"] - len(list(instances.keys()))
                                self.append_to_instances(request, instances, res_type)
                            for key, value in instances.items():
                                all_instances[key] = value
                    except Exception as e:
                        logger.exception(e)
                else:
                    try:
                        request.GET["resourcecount"] = int(self.datadownloadconfig["count"]) - len(resources_in_couch)
                        parsed = urllib.parse.urlparse(query)
                        urlparams = urllib.parse.parse_qs(parsed.query)
                        for k, v in urlparams.items():
                            request.GET[k] = v[0]
                        search_res_json = search.search_results(request)
                        search_res = JSONDeserializer().deserialize(search_res_json.content)
                        for hit in search_res["results"]["hits"]["hits"]:
                            all_instances[hit["_source"]["resourceinstanceid"]] = hit["_source"]
                    except KeyError:
                        print("no instances found in", search_res)

            # this effectively makes sure that resources in couch always get updated
            # even if they weren't included in the search results above (assuming self.datadownloadconfig["download"] == True)
            # if self.datadownloadconfig["download"] == False then this will always update the resources in couch
            ids = list(resources_in_couch - set(all_instances.keys()))

            if len(ids) > 0:
                se = SearchEngineFactory().create()
                query = Query(se, start=0, limit=settings.SEARCH_RESULT_LIMIT)
                ids_query = Terms(field="_id", terms=ids)
                query.add_query(ids_query)
                results = query.search(index=RESOURCES_INDEX)
                if results is not None:
                    for result in results["hits"]["hits"]:
                        all_instances[result["_id"]] = result["_source"]
        return all_instances

    def load_tiles_into_couch(self, instances, nodegroup):
        """
        Takes a mobile survey object, a couch database instance, and a dictionary
        of resource instances to identify eligible tiles and load them into the
        database instance
        """
        db = self.couch.create_db("project_" + str(self.id))
        tiles = models.TileModel.objects.filter(nodegroup=nodegroup)
        tiles_serialized = json.loads(JSONSerializer().serialize(tiles))
        for tile in tiles_serialized:
            if str(tile["resourceinstance_id"]) in instances:
                try:
                    tile["type"] = "tile"
                    doc = self.couch.update_doc(db, tile, tile["tileid"])
                    self.add_attachments(db, doc)
                except Exception as e:
                    print("error on load_tiles_into_couch")
                    print(e, tile)
        nodegroups = models.NodeGroup.objects.filter(parentnodegroup=nodegroup)
        for nodegroup in nodegroups:
            self.load_tiles_into_couch(instances, nodegroup)

    def add_attachments(self, db, tile):
        files = models.File.objects.filter(tile_id=tile["tileid"])
        for file in files:
            with Image.open(file.path.file).copy() as image:
                image = image.convert("RGB")
                image.thumbnail((settings.MOBILE_IMAGE_SIZE_LIMITS["thumb"], settings.MOBILE_IMAGE_SIZE_LIMITS["thumb"]))
                b = io.BytesIO()
                image.save(b, "JPEG")
                db.put_attachment(tile, b.getvalue(), filename=str(file.fileid), content_type="image/jpeg")

    def load_instances_into_couch(self, instances):
        """
        Takes a mobile survey object, a couch database instance, and a dictionary
        of resource instances and loads them into the database instance.
        """
        db = self.couch.create_db("project_" + str(self.id))
        for instanceid, instance in instances.items():
            try:
                instance["type"] = "resource"
                self.couch.update_doc(db, instance, instanceid)
            except Exception as e:
                print(e, instance)

    def _delete_items_from_couch(self, key, items_to_delete):
        db = self.couch.create_db("project_" + str(self.id))
        query = {"selector": {key: {"$in": list(items_to_delete)}}}
        for doc in db.find(query):
            print(f"deleting {doc['type']}: {doc['_id']}")
            db.delete(doc)

    def delete_resource_instances_from_couch(self):
        instances_to_delete = []
        try:
            synclog = models.MobileSyncLog.objects.filter(survey=self, status="FINISHED").latest("finished")
            instances_to_delete = models.EditLog.objects.filter(edittype="delete").values_list("resourceinstanceid", flat=True)
        except models.MobileSyncLog.DoesNotExist:
            pass

        # print("deleting resources: ", instances_to_delete)
        # delete resouce instances
        self._delete_items_from_couch("resourceinstanceid", instances_to_delete)
        # delete tiles related to those resources that were deleted
        self._delete_items_from_couch("resourceinstance_id", instances_to_delete)

    def delete_tiles_from_couch(self):
        tiles_to_delete = []
        try:
            synclog = models.MobileSyncLog.objects.filter(survey=self, status="FINISHED").latest("finished")
            tiles_to_delete = models.EditLog.objects.filter(edittype="tile delete").values_list("tileinstanceid", flat=True)
        except models.MobileSyncLog.DoesNotExist:
            pass

        # print("deleting tiles: ", tiles_to_delete)
        # delete just individual tiles that were deleted
        self._delete_items_from_couch("tileid", tiles_to_delete)

    def load_data_into_couch(self, initializing_couch=False):
        """
        Takes a mobile survey, a couch database intance and a django user and loads
        tile and resource instance data into the couch instance.
        """

        if initializing_couch is False:
            self.delete_resource_instances_from_couch()
            self.delete_tiles_from_couch()

        instances = self.collect_resource_instances_for_couch()
        cards = self.cards.all()
        for card in cards:
            self.load_tiles_into_couch(instances, card.nodegroup)
        self.load_instances_into_couch(instances)
