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

import json
import couchdb
import urlparse
from datetime import datetime
from django.db import transaction
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.contrib.gis.geos import MultiPolygon
from django.contrib.gis.geos import Polygon
from django.core.urlresolvers import reverse
from django.core.mail import EmailMultiAlternatives
from django.http import HttpRequest, HttpResponseNotFound
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.views.generic import View
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.response import JSONResponse
from arches.app.utils.decorators import group_required
from arches.app.utils.geo_utils import GeoUtils
from arches.app.utils.couch import Couch
from arches.app.models import models
from arches.app.models.card import Card
from arches.app.models.mobile_survey import MobileSurvey
from arches.app.models.system_settings import settings
from arches.app.views.base import MapBaseManagerView
import arches.app.views.search as search

@method_decorator(group_required('Application Administrator'), name='dispatch')
class MobileSurveyManagerView(MapBaseManagerView):

    def get(self, request):

        def get_last_login(date):
            result = _("Not yet logged in")
            try:
                if date is not None:
                    result = datetime.strftime(date, '%Y-%m-%d %H:%M')
            except TypeError as e:
                print e
            return result

        identities = []
        for group in Group.objects.all():
            users = group.user_set.all()
            if len(users) > 0:
                groupUsers = [{'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'last_login': get_last_login(user.last_login), 'username': user.username, 'groups': [g.id for g in user.groups.all()], 'group_names': ', '.join([g.name for g in user.groups.all()]) } for user in users]
            identities.append({'name': group.name, 'type': 'group', 'id': group.pk, 'users': groupUsers, 'default_permissions': group.permissions.all()})
        for user in User.objects.filter():
            groups = []
            group_ids = []
            default_perms = []
            for group in user.groups.all():
                groups.append(group.name)
                group_ids.append(group.id)
                default_perms = default_perms + list(group.permissions.all())
            identities.append({'name': user.email or user.username, 'groups': ', '.join(groups), 'type': 'user', 'id': user.pk, 'default_permissions': set(default_perms), 'is_superuser':user.is_superuser, 'group_ids': group_ids, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email})

        map_layers = models.MapLayer.objects.all()
        map_markers = models.MapMarker.objects.all()
        map_sources = models.MapSource.objects.all()
        geocoding_providers = models.Geocoder.objects.all()

        mobile_survey_models = models.MobileSurveyModel.objects.order_by('name')
        mobile_surveys, resources = self.get_survey_resources(mobile_survey_models)

        for mobile_survey in mobile_surveys:
            try:
                mobile_survey['datadownloadconfig'] = json.loads(mobile_survey['datadownloadconfig'])
            except TypeError:
                pass
            multipart = mobile_survey['bounds']
            singlepart = GeoUtils().convert_multipart_to_singlepart(multipart)
            mobile_survey['bounds'] = singlepart

        serializer = JSONSerializer()
        context = self.get_context_data(
            map_layers=map_layers,
            map_markers=map_markers,
            map_sources=map_sources,
            geocoding_providers=geocoding_providers,
            mobile_surveys=serializer.serialize(mobile_surveys, sort_keys=False),
            identities=serializer.serialize(identities, sort_keys=False),
            resources=serializer.serialize(resources, sort_keys=False),
            resource_download_limit=settings.MOBILE_DOWNLOAD_RESOURCE_LIMIT,
            main_script='views/mobile-survey-manager',
        )

        context['nav']['title'] = _('Mobile Survey Manager')
        context['nav']['icon'] = 'fa-server'
        context['nav']['help'] = {
            'title': _('Mobile Survey Manager'),
            'template': 'mobile-survey-manager-help',
        }

        return render(request, 'views/mobile-survey-manager.htm', context)

    def delete(self, request):
        mobile_survey_id = None
        try:
            mobile_survey_id = JSONDeserializer().deserialize(request.body)['id']
        except Exception as e:
            print e

        try:
            connection_error = False
            with transaction.atomic():
                if mobile_survey_id is not None:
                    ret = MobileSurvey.objects.get(pk=mobile_survey_id)
                    ret.delete()
                    return JSONResponse({'success': True})
        except Exception as e:
            if connection_error == False:
                error_title = _('Unable to delete survey')
                if e.strerror == 'Connection refused':
                    error_message = "Unable to connect to CouchDB"
                else:
                    error_message = e.message
                connection_error = JSONResponse({'success':False,'message': error_message,'title': error_title}, status=500)
            return connection_error

        return HttpResponseNotFound()

    def update_identities(self, data, mobile_survey, related_identities, identity_type='users', identity_model=User, xmodel=models.MobileSurveyXUser):
        mobile_survey_identity_ids = set([u.id for u in related_identities])
        identities_to_remove = mobile_survey_identity_ids - set(data[identity_type])
        identities_to_add = set(data[identity_type]) - mobile_survey_identity_ids

        for identity in identities_to_add:
            if identity_type == 'users':
                xmodel.objects.create(user=identity_model.objects.get(id=identity), mobile_survey=mobile_survey)
            else:
                xmodel.objects.create(group=identity_model.objects.get(id=identity), mobile_survey=mobile_survey)

        for identity in identities_to_remove:
            if identity_type == 'users':
                xmodel.objects.filter(user=identity_model.objects.get(id=identity), mobile_survey=mobile_survey).delete()
            else:
                xmodel.objects.filter(group=identity_model.objects.get(id=identity), mobile_survey=mobile_survey).delete()

    def post(self, request):
        data = JSONDeserializer().deserialize(request.body)

        if data['id'] is None:
            mobile_survey = MobileSurvey()
            mobile_survey.createdby = self.request.user
        else:
            mobile_survey = MobileSurvey.objects.get(pk=data['id'])
            self.update_identities(data, mobile_survey, mobile_survey.users.all(), 'users', User, models.MobileSurveyXUser)
            self.update_identities(data, mobile_survey, mobile_survey.groups.all(), 'groups', Group, models.MobileSurveyXGroup)

            mobile_survey_card_ids = set([unicode(c.cardid) for c in mobile_survey.cards.all()])
            form_card_ids = set(data['cards'])
            cards_to_remove = mobile_survey_card_ids - form_card_ids
            cards_to_add = form_card_ids - mobile_survey_card_ids
            cards_to_update = mobile_survey_card_ids & form_card_ids

            for card_id in cards_to_add:
                models.MobileSurveyXCard.objects.create(card=models.CardModel.objects.get(cardid=card_id), mobile_survey=mobile_survey, sortorder=data['cards'].index(card_id))

            for card_id in cards_to_update:
                mobile_survey_card = models.MobileSurveyXCard.objects.filter(mobile_survey=mobile_survey).get(card=models.CardModel.objects.get(cardid=card_id))
                mobile_survey_card.sortorder=data['cards'].index(card_id)
                mobile_survey_card.save()

            for card_id in cards_to_remove:
                models.MobileSurveyXCard.objects.filter(card=models.CardModel.objects.get(cardid=card_id), mobile_survey=mobile_survey).delete()


        if mobile_survey.active != data['active']:
            # notify users in the mobile_survey that the state of the mobile_survey has changed
            if data['active']:
                self.notify_mobile_survey_start(request, mobile_survey)
            else:
                self.notify_mobile_survey_end(request, mobile_survey)
        mobile_survey.name = data['name']
        mobile_survey.description = data['description']
        if data['startdate'] != '':
            mobile_survey.startdate = data['startdate']
        if data['enddate'] != '':
            mobile_survey.enddate = data['enddate']
        mobile_survey.datadownloadconfig = data['datadownloadconfig']
        mobile_survey.active = data['active']
        mobile_survey.tilecache = data['tilecache']
        polygons = []

        try:
            data['bounds'].upper()
            data['bounds'] = json.loads(data['bounds'])
        except AttributeError:
            pass

        if 'features' in data['bounds']:
            for feature in data['bounds']['features']:
                for coord in feature['geometry']['coordinates']:
                    polygons.append(Polygon(coord))

        mobile_survey.bounds = MultiPolygon(polygons)
        mobile_survey.lasteditedby = self.request.user
        try:
            connection_error = False
            with transaction.atomic():
                mobile_survey.save()
        except Exception as e:
            if connection_error == False:
                error_title = _('Unable to save survey')
                if e.strerror == 'Connection refused':
                    error_message = "Unable to connect to CouchDB"
                else:
                    error_message = e.message
                connection_error = JSONResponse({'success':False,'message': error_message,'title': error_title}, status=500)
            return connection_error

        return JSONResponse({'success':True, 'mobile_survey': mobile_survey})

    def get_mobile_survey_users(self, mobile_survey):
        users = set(mobile_survey.users.all())

        for group in mobile_survey.groups.all():
            users |= set(group.user_set.all())

        return users

    def notify_mobile_survey_start(self, request, mobile_survey):
        admin_email = settings.ADMINS[0][1] if settings.ADMINS else ''
        email_context = {
            'button_text': _('Logon to {app_name}'.format(app_name=settings.APP_NAME)),
            'link':request.build_absolute_uri(reverse('home')),
            'greeting': _('Welcome to Arches!  You\'ve just been added to a Mobile Survey.  Please take a moment to review the mobile_survey description and mobile_survey start and end dates.'),
            'closing': _('If you have any qustions contact the site administrator at {admin_email}.'.format(admin_email=admin_email)),
        }

        html_content = render_to_string('email/general_notification.htm', email_context)
        text_content = strip_tags(html_content) # this strips the html, so people will have the text as well.

        # create the email, and attach the HTML version as well.
        for user in self.get_mobile_survey_users(mobile_survey):
            msg = EmailMultiAlternatives(_('You\'ve been invited to an {app_name} Survey!'.format(app_name=settings.APP_NAME)), text_content, admin_email, [user.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

    def notify_mobile_survey_end(self, request, mobile_survey):
        admin_email = settings.ADMINS[0][1] if settings.ADMINS else ''
        email_context = {
            'button_text': _('Logon to {app_name}'.format(app_name=settings.APP_NAME)),
            'link':request.build_absolute_uri(reverse('home')),
            'greeting': _('Hi!  The Mobile Survey you were part of has ended or is temporarily suspended.  Please permform a final sync of your local dataset as soon as possible.'),
            'closing': _('If you have any qustions contact the site administrator at {admin_email}.'.format(admin_email=admin_email)),
        }

        html_content = render_to_string('email/general_notification.htm', email_context)
        text_content = strip_tags(html_content) # this strips the html, so people will have the text as well.

        # create the email, and attach the HTML version as well.
        for user in self.get_mobile_survey_users(mobile_survey):
            msg = EmailMultiAlternatives(_('There\'s been a change to an {app_name} Survey that you\'re part of!'.format(app_name=settings.APP_NAME)), text_content, admin_email, [user.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

    def get_survey_resources(self, mobile_survey_models):
        graphs = models.GraphModel.objects.filter(isresource=True).exclude(graphid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
        resources = []
        mobile_surveys = []
        all_ordered_card_ids = []

        for mobile_survey in mobile_survey_models:
            survey = MobileSurvey.objects.get(id=mobile_survey.id)
            mobile_survey_dict = survey.serialize()
            all_ordered_card_ids += mobile_survey_dict['cards']
            mobile_surveys.append(mobile_survey_dict)

        active_graphs = set([unicode(card.graph_id) for card in models.CardModel.objects.filter(cardid__in=all_ordered_card_ids)])

        for i, graph in enumerate(graphs):
            cards = []
            if i == 0 or unicode(graph.graphid) in active_graphs:
                cards = [Card.objects.get(pk=card.cardid) for card in models.CardModel.objects.filter(graph=graph)]
            resources.append({'name': graph.name, 'id': graph.graphid, 'subtitle': graph.subtitle, 'iconclass': graph.iconclass, 'cards': cards})

        return mobile_surveys, resources


# @method_decorator(can_read_resource_instance(), name='dispatch')
class MobileSurveyResources(View):

    def get(self, request, surveyid=None):
        graphs = models.GraphModel.objects.filter(isresource=True).exclude(graphid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
        resources = []
        all_ordered_card_ids = []

        proj = MobileSurvey.objects.get(id=surveyid)
        all_ordered_card_ids = proj.get_ordered_cards()
        active_graphs = set([unicode(card.graph_id) for card in models.CardModel.objects.filter(cardid__in=all_ordered_card_ids)])
        for i, graph in enumerate(graphs):
            cards = []
            if unicode(graph.graphid) in active_graphs:
                cards = [Card.objects.get(pk=card.cardid) for card in models.CardModel.objects.filter(graph=graph)]
                resources.append({'name': graph.name, 'id': graph.graphid, 'subtitle': graph.subtitle, 'iconclass': graph.iconclass, 'cards': cards})

        return JSONResponse({'success':True, 'resources': resources})
