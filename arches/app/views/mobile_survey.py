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

import json
import couchdb
import logging
import urllib.parse
from datetime import datetime
from datetime import timedelta
from django.db import transaction
from django.shortcuts import render
from django.db.models import Count
from django.contrib.auth.models import User, Group
from django.contrib.gis.geos import MultiPolygon
from django.contrib.gis.geos import Polygon
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.http import HttpRequest, HttpResponseNotFound
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.views.generic import View
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.response import JSONResponse, JSONErrorResponse
from arches.app.utils.decorators import group_required
from arches.app.utils.geo_utils import GeoUtils
from arches.app.utils.couch import Couch
from arches.app.models import models
from arches.app.models.card import Card
from arches.app.models.mobile_survey import MobileSurvey
from arches.app.models.system_settings import settings
from arches.app.views.base import BaseManagerView
from arches.app.views.base import MapBaseManagerView
import arches.app.views.search as search


def get_survey_resources(mobile_survey):
    graphs = models.GraphModel.objects.filter(isresource=True).exclude(graphid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
    resources = []
    all_ordered_card_ids = mobile_survey["cards"]
    active_graphs = {str(card.graph_id) for card in models.CardModel.objects.filter(cardid__in=all_ordered_card_ids)}
    for i, graph in enumerate(graphs):
        cards = []
        if i == 0 or str(graph.graphid) in active_graphs:
            cards = [Card.objects.get(pk=card.cardid) for card in models.CardModel.objects.filter(graph=graph).order_by("sortorder")]
        resources.append(
            {"name": graph.name, "id": graph.graphid, "subtitle": graph.subtitle, "iconclass": graph.iconclass, "cards": cards}
        )

    return resources


logger = logging.getLogger(__name__)


@method_decorator(group_required("Application Administrator"), name="dispatch")
class MobileSurveyManagerView(BaseManagerView):
    def get(self, request):
        mobile_survey_models = models.MobileSurveyModel.objects.order_by("name")
        mobile_surveys = []
        serializer = JSONSerializer()
        for survey in mobile_survey_models:
            survey.deactivate_expired_survey()
            serialized_survey = serializer.serializeToPython(survey)
            serialized_survey["edited_by"] = {
                "username": survey.lasteditedby.username,
                "first": survey.lasteditedby.first_name,
                "last": survey.lasteditedby.last_name,
                "id": survey.lasteditedby.id,
            }
            serialized_survey["created_by"] = created_by = {
                "username": survey.createdby.username,
                "first": survey.createdby.first_name,
                "last": survey.createdby.last_name,
                "id": survey.createdby.id,
            }
            mobile_surveys.append(serialized_survey)

        context = self.get_context_data(
            mobile_surveys=serializer.serialize(mobile_surveys, sort_keys=False), main_script="views/mobile-survey-manager"
        )

        context["nav"]["title"] = _("Arches Collector Manager")
        context["nav"]["icon"] = "fa-globe"
        context["nav"]["help"] = {"title": _("Arches Collector Manager"), "template": "arches-collector-manager-help"}

        return render(request, "views/mobile-survey-manager.htm", context)

    def delete(self, request):
        mobile_survey_id = None
        try:
            mobile_survey_id = JSONDeserializer().deserialize(request.body)["id"]
        except Exception as e:
            logger.exception(e)

        try:
            connection_error = False
            with transaction.atomic():
                if mobile_survey_id is not None:
                    ret = MobileSurvey.objects.get(pk=mobile_survey_id)
                    ret.delete()
                    return JSONResponse({"success": True})
        except Exception as e:
            if connection_error is False:
                error_title = _("Unable to delete collector project")
                if "strerror" in e and e.strerror == "Connection refused" or "Connection refused" in e:
                    error_message = _("Unable to connect to CouchDB")
                else:
                    error_message = e.message
                connection_error = JSONResponse({"success": False, "message": error_message, "title": error_title}, status=500)
            return connection_error

        return HttpResponseNotFound()


@method_decorator(group_required("Application Administrator"), name="dispatch")
class MobileSurveyDesignerView(MapBaseManagerView):
    def get(self, request, surveyid):
        def get_history(survey, history):
            sync_log_records = models.MobileSyncLog.objects.order_by("-finished").values().filter(survey=survey)
            resourceedits = (
                models.TileRevisionLog.objects.filter(survey=survey).values("resourceid").annotate(Count("tileid", distinct=True))
            )
            if len(sync_log_records) > 0:
                lastsync = datetime.strftime(sync_log_records[0]["finished"], "%Y-%m-%d %H:%M:%S")
                history["lastsync"] = lastsync
            for entry in sync_log_records:
                history["edits"] = len(resourceedits)
                if entry["userid"] not in history["editors"]:
                    history["editors"][entry["userid"]] = {"lastsync": entry["finished"]}
                else:
                    if entry["finished"] > history["editors"][entry["userid"]]["lastsync"]:
                        history["editors"][entry["userid"]]["lastsync"] = entry["finished"]
            for id, editor in iter(list(history["editors"].items())):
                editor["lastsync"] = datetime.strftime(editor["lastsync"], "%Y-%m-%d %H:%M:%S")
            return history

        identities = []
        for group in Group.objects.all():
            users = group.user_set.all()
            if len(users) > 0:
                groupUsers = [
                    {
                        "id": user.id,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                        "username": user.username,
                        "groups": [g.id for g in user.groups.all()],
                        "group_names": ", ".join([g.name for g in user.groups.all()]),
                    }
                    for user in users
                ]
            identities.append(
                {"name": group.name, "type": "group", "id": group.pk, "users": groupUsers, "default_permissions": group.permissions.all()}
            )
        for user in User.objects.filter():
            groups = []
            group_ids = []
            default_perms = []
            for group in user.groups.all():
                groups.append(group.name)
                group_ids.append(group.id)
                default_perms = default_perms + list(group.permissions.all())
            identities.append(
                {
                    "name": user.email or user.username,
                    "groups": ", ".join(groups),
                    "type": "user",
                    "id": user.pk,
                    "default_permissions": set(default_perms),
                    "is_superuser": user.is_superuser,
                    "group_ids": group_ids,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                }
            )

        history = {"lastsync": "", "edits": 0, "editors": {}}
        map_layers = models.MapLayer.objects.all()
        map_markers = models.MapMarker.objects.all()
        map_sources = models.MapSource.objects.all()
        geocoding_providers = models.Geocoder.objects.all()

        survey_exists = models.MobileSurveyModel.objects.filter(pk=surveyid).exists()

        if survey_exists is True:
            survey = MobileSurvey.objects.get(pk=surveyid)
            mobile_survey = survey.serialize()
            history = get_history(survey, history)
            resources = get_survey_resources(mobile_survey)
        else:
            survey = MobileSurvey(
                id=surveyid,
                name="",
                datadownloadconfig={"download": False, "count": 100, "resources": [], "custom": None},
                onlinebasemaps=settings.MOBILE_DEFAULT_ONLINE_BASEMAP,
            )
            mobile_survey = survey.serialize()
            mobile_survey["bounds"] = settings.DEFAULT_BOUNDS

        resources = get_survey_resources(mobile_survey)

        try:
            mobile_survey["datadownloadconfig"] = json.loads(mobile_survey["datadownloadconfig"])
        except TypeError:
            pass

        try:
            if mobile_survey["bounds"]["type"] == "MultiPolygon":
                multipart = mobile_survey["bounds"]
                singlepart = GeoUtils().convert_multipart_to_singlepart(multipart)
                mobile_survey["bounds"] = singlepart
        except TypeError as e:
            pass

        serializer = JSONSerializer()
        context = self.get_context_data(
            map_layers=map_layers,
            map_markers=map_markers,
            map_sources=map_sources,
            history=serializer.serialize(history),
            geocoding_providers=geocoding_providers,
            mobile_survey=serializer.serialize(mobile_survey, sort_keys=False),
            identities=serializer.serialize(identities, sort_keys=False),
            resources=serializer.serialize(resources, sort_keys=False),
            resource_download_limit=mobile_survey["datadownloadconfig"]["count"],
            main_script="views/mobile-survey-designer",
        )

        context["nav"]["menu"] = True
        context["nav"]["title"] = _("Arches Collector Manager")
        context["nav"]["icon"] = "fa-globe"
        context["nav"]["help"] = {"title": _("Arches Collector Manager"), "template": "arches-collector-manager-help"}

        return render(request, "views/mobile-survey-designer.htm", context)

    def delete(self, request, surveyid):
        try:
            connection_error = False
            with transaction.atomic():
                if surveyid is not None:
                    ret = MobileSurvey.objects.get(pk=surveyid)
                    ret.delete()
                    return JSONResponse({"success": True})
        except Exception as e:
            if connection_error is False:
                error_title = _("Unable to delete survey")
                if "strerror" in e and e.strerror == "Connection refused" or "Connection refused" in e:
                    error_message = _("Unable to connect to CouchDB. Please confirm that CouchDB is running")
                else:
                    error_message = e.message
                connection_error = JSONErrorResponse(error_title, error_message)
            return connection_error

        return HttpResponseNotFound()

    def update_identities(
        self, data, mobile_survey, related_identities, identity_type="users", identity_model=User, xmodel=models.MobileSurveyXUser
    ):
        mobile_survey_identity_ids = {u.id for u in related_identities}
        identities_to_remove = mobile_survey_identity_ids - set(data[identity_type])
        identities_to_add = set(data[identity_type]) - mobile_survey_identity_ids

        for identity in identities_to_add:
            if identity_type == "users":
                xmodel.objects.create(user=identity_model.objects.get(id=identity), mobile_survey=mobile_survey)
            else:
                xmodel.objects.create(group=identity_model.objects.get(id=identity), mobile_survey=mobile_survey)

        for identity in identities_to_remove:
            if identity_type == "users":
                xmodel.objects.filter(user=identity_model.objects.get(id=identity), mobile_survey=mobile_survey).delete()
            else:
                xmodel.objects.filter(group=identity_model.objects.get(id=identity), mobile_survey=mobile_survey).delete()

    def post(self, request, surveyid):
        data = JSONDeserializer().deserialize(request.body)
        if models.MobileSurveyModel.objects.filter(pk=data["id"]).exists() is False:
            mobile_survey_model = models.MobileSurveyModel(
                id=surveyid, name=data["name"], createdby=self.request.user, lasteditedby=self.request.user
            )
            mobile_survey_model.save()

        mobile_survey = MobileSurvey.objects.get(pk=data["id"])
        self.update_identities(data, mobile_survey, mobile_survey.users.all(), "users", User, models.MobileSurveyXUser)
        self.update_identities(data, mobile_survey, mobile_survey.groups.all(), "groups", Group, models.MobileSurveyXGroup)

        mobile_survey_card_ids = {str(c.cardid) for c in mobile_survey.cards.all()}
        form_card_ids = set(data["cards"])
        cards_to_remove = mobile_survey_card_ids - form_card_ids
        cards_to_add = form_card_ids - mobile_survey_card_ids
        cards_to_update = mobile_survey_card_ids & form_card_ids

        for card_id in cards_to_add:
            models.MobileSurveyXCard.objects.create(
                card=models.CardModel.objects.get(cardid=card_id), mobile_survey=mobile_survey, sortorder=data["cards"].index(card_id)
            )

        for card_id in cards_to_update:
            mobile_survey_card = models.MobileSurveyXCard.objects.filter(mobile_survey=mobile_survey).get(
                card=models.CardModel.objects.get(cardid=card_id)
            )
            mobile_survey_card.sortorder = data["cards"].index(card_id)
            mobile_survey_card.save()

        for card_id in cards_to_remove:
            models.MobileSurveyXCard.objects.filter(card=models.CardModel.objects.get(cardid=card_id), mobile_survey=mobile_survey).delete()

        # TODO Disabling the following section until we make emailing users optional
        # if mobile_survey.active != data['active']:
        # notify users in the mobile_survey that the state of the mobile_survey has changed
        # if data['active']:
        #     self.notify_mobile_survey_start(request, mobile_survey)
        # else:
        #     self.notify_mobile_survey_end(request, mobile_survey)
        mobile_survey.name = data["name"]
        mobile_survey.description = data["description"]
        mobile_survey.onlinebasemaps = data["onlinebasemaps"]
        if data["startdate"] != "":
            mobile_survey.startdate = data["startdate"]
        if data["enddate"] != "":
            mobile_survey.enddate = data["enddate"]
        mobile_survey.datadownloadconfig = data["datadownloadconfig"]
        mobile_survey.active = data["active"]
        mobile_survey.tilecache = data["tilecache"]
        polygons = []

        # try:
        #     data['bounds'].upper()
        #     data['bounds'] = json.loads(data['bounds'])
        # except AttributeError as e:
        #     print('bounds is not a string')

        if "features" in data["bounds"]:
            for feature in data["bounds"]["features"]:
                for coord in feature["geometry"]["coordinates"]:
                    polygons.append(Polygon(coord))

        elif len(polygons) == 0:
            try:
                if data["bounds"]["type"] == "MultiPolygon":
                    for poly in data["bounds"]["coordinates"]:
                        for coords in poly:
                            polygons.append(Polygon(coords))
            except AttributeError as e:
                print("bounds is not a geojson geometry object")

        mobile_survey.bounds = MultiPolygon(polygons)
        mobile_survey.lasteditedby = self.request.user

        try:
            with transaction.atomic():
                mobile_survey.save()
        except ConnectionRefusedError as e:
            error_title = _("Unable to save collector project")
            error_message = _("Failed to connect to a CouchDB service")
            connection_error = JSONErrorResponse(error_title, error_message)
            return connection_error
        except Exception as e:
            error_title = _("Unable to save collector project")
            logger.exception(e)
            connection_error = JSONErrorResponse(error_title, e)
            return connection_error

        return JSONResponse({"success": True, "mobile_survey": mobile_survey})

    def get_mobile_survey_users(self, mobile_survey):
        users = set(mobile_survey.users.all())

        for group in mobile_survey.groups.all():
            users |= set(group.user_set.all())

        return users

    def notify_mobile_survey_start(self, request, mobile_survey):
        admin_email = settings.ADMINS[0][1] if settings.ADMINS else ""
        email_context = {
            "button_text": _("Logon to {app_name}".format(app_name=settings.APP_NAME)),
            "link": request.build_absolute_uri(reverse("home")),
            "greeting": _(
                "Welcome to Arches!  You've just been added to a Mobile Survey.  \
                Please take a moment to review the mobile_survey description and mobile_survey start and end dates."
            ),
            "closing": _("If you have any qustions contact the site administrator at {admin_email}.").format(**locals()),
        }

        html_content = render_to_string("email/general_notification.htm", email_context)
        text_content = strip_tags(html_content)  # this strips the html, so people will have the text as well.

        # create the email, and attach the HTML version as well.
        for user in self.get_mobile_survey_users(mobile_survey):
            msg = EmailMultiAlternatives(
                _("You've been invited to an {app_name} Survey!".format(app_name=settings.APP_NAME)),
                text_content,
                admin_email,
                [user.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

    def notify_mobile_survey_end(self, request, mobile_survey):
        admin_email = settings.ADMINS[0][1] if settings.ADMINS else ""
        email_context = {
            "button_text": _("Logon to {app_name}".format(app_name=settings.APP_NAME)),
            "link": request.build_absolute_uri(reverse("home")),
            "greeting": _(
                "Hi!  The Mobile Survey you were part of has ended or is temporarily suspended. \
                Please permform a final sync of your local dataset as soon as possible."
            ),
            "closing": _("If you have any qustions contact the site administrator at {admin_email}.").format(**locals()),
        }

        html_content = render_to_string("email/general_notification.htm", email_context)
        text_content = strip_tags(html_content)  # this strips the html, so people will have the text as well.

        # create the email, and attach the HTML version as well.
        for user in self.get_mobile_survey_users(mobile_survey):
            msg = EmailMultiAlternatives(
                _("There's been a change to an {app_name} Survey that you're part of!".format(app_name=settings.APP_NAME)),
                text_content,
                admin_email,
                [user.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()


# @method_decorator(can_read_resource_instance(), name='dispatch')
class MobileSurveyResources(View):
    def get(self, request, surveyid=None):
        graphs = models.GraphModel.objects.filter(isresource=True).exclude(graphid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
        resources = []
        all_ordered_card_ids = []
        proj = MobileSurvey.objects.get(id=surveyid)
        all_ordered_card_ids = proj.get_ordered_cards()
        active_graphs = {str(card.graph_id) for card in models.CardModel.objects.filter(cardid__in=all_ordered_card_ids)}
        for i, graph in enumerate(graphs):
            cards = []
            if str(graph.graphid) in active_graphs:
                cards = [Card.objects.get(pk=card.cardid) for card in models.CardModel.objects.filter(graph=graph)]
                resources.append(
                    {"name": graph.name, "id": graph.graphid, "subtitle": graph.subtitle, "iconclass": graph.iconclass, "cards": cards}
                )

        return JSONResponse({"success": True, "resources": resources})
