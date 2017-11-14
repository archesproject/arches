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

from datetime import datetime
from django.db import transaction
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseNotFound
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.utils.decorators import group_required
from arches.app.models import models
from arches.app.models.card import Card
from arches.app.models.system_settings import settings
from arches.app.views.base import BaseManagerView

@method_decorator(group_required('Application Administrator'), name='dispatch')
class ProjectManagerView(BaseManagerView):


    def get(self, request):

        def get_last_login(date):
            result = _("Not yet logged in")
            try:
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

        graphs = models.GraphModel.objects.filter(isresource=True).exclude(graphid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
        resources = []

        projects = []
        all_ordered_card_ids = []
        for project in models.MobileProject.objects.order_by('name'):
            ordered_cards = models.MobileProjectXCard.objects.filter(mobile_project=project).order_by('sortorder')
            ordered_card_ids = [unicode(mpc.card.cardid) for mpc in ordered_cards]
            all_ordered_card_ids += ordered_card_ids
            project_dict = project.__dict__
            project_dict['cards'] = ordered_card_ids
            project_dict['users'] = [u.id for u in project.users.all()]
            project_dict['groups'] = [g.id for g in project.users.all()]
            projects.append(project_dict)

        active_graphs = set([unicode(card.graph_id) for card in models.CardModel.objects.filter(cardid__in=all_ordered_card_ids)])

        for i, graph in enumerate(graphs):
            cards = []
            if i == 0 or unicode(graph.graphid) in active_graphs:
                cards = [Card.objects.get(pk=card.cardid) for card in models.CardModel.objects.filter(graph=graph)]

            resources.append({'name': graph.name, 'id': graph.graphid, 'subtitle': graph.subtitle, 'iconclass': graph.iconclass, 'cards': cards})

        context = self.get_context_data(
            projects=JSONSerializer().serialize(projects),
            identities=JSONSerializer().serialize(identities),
            resources=JSONSerializer().serialize(resources),
            main_script='views/project-manager',
        )

        context['nav']['title'] = _('Mobile Project Manager')
        context['nav']['icon'] = 'fa-server'
        context['nav']['help'] = (_('Mobile Project Manager'),'help/project-manager-help.htm')

        return render(request, 'views/project-manager.htm', context)

    def delete(self, request):

        project_id = None
        try:
            project_id = JSONDeserializer().deserialize(request.body)['id']
        except Exception as e:
            print e

        if project_id is not None:
            ret = models.MobileProject.objects.get(pk=project_id)
            ret.delete()
            return JSONResponse(ret)

        return HttpResponseNotFound()

    def update_identities(self, data, project, related_identities, identity_type='users', identity_model=User, xmodel=models.MobileProjectXUser):
        project_identity_ids = set([u.id for u in related_identities])
        identities_to_remove = project_identity_ids - set(data[identity_type])
        identities_to_add = set(data[identity_type]) - project_identity_ids

        for identity in identities_to_add:
            if identity_type == 'users':
                xmodel.objects.create(user=identity_model.objects.get(id=identity), mobile_project=project)
            else:
                xmodel.objects.create(group=identity_model.objects.get(id=identity), mobile_project=project)

        for identity in identities_to_remove:
            if identity_type == 'users':
                xmodel.objects.filter(user=identity_model.objects.get(id=identity), mobile_project=project).delete()
            else:
                xmodel.objects.filter(group=identity_model.objects.get(id=identity), mobile_project=project).delete()

    def post(self, request):
        data = JSONDeserializer().deserialize(request.body)

        if data['id'] is None:
            project = models.MobileProject()
            project.createdby = self.request.user
        else:
            project = models.MobileProject.objects.get(pk=data['id'])
            self.update_identities(data, project, project.users.all(), 'users', User, models.MobileProjectXUser)
            self.update_identities(data, project, project.groups.all(), 'groups', Group, models.MobileProjectXGroup)

            project_card_ids = set([unicode(c.cardid) for c in project.cards.all()])
            form_card_ids = set(data['cards'])
            cards_to_remove = project_card_ids - form_card_ids
            cards_to_add = form_card_ids - project_card_ids
            cards_to_update = project_card_ids & form_card_ids

            for card_id in cards_to_add:
                models.MobileProjectXCard.objects.create(card=models.CardModel.objects.get(cardid=card_id), mobile_project=project, sortorder=data['cards'].index(card_id))

            for card_id in cards_to_update:
                mobile_project_card = models.MobileProjectXCard.objects.filter(mobile_project=project).get(card=models.CardModel.objects.get(cardid=card_id))
                mobile_project_card.sortorder=data['cards'].index(card_id)
                mobile_project_card.save()

            for card_id in cards_to_remove:
                models.MobileProjectXCard.objects.filter(card=models.CardModel.objects.get(cardid=card_id), mobile_project=project).delete()


        if project.active != data['active']:
            # notify users in the project that the state of the project has changed
            if data['active']:
                self.notify_project_start(request, project)
            else:
                self.notify_project_end(request, project)
        project.name = data['name']
        project.description = data['description']
        if data['startdate'] != '':
            project.startdate = data['startdate']
        if data['enddate'] != '':
            project.enddate = data['enddate']
        project.active = data['active']
        project.lasteditedby = self.request.user

        with transaction.atomic():
            project.save()

        ordered_cards = models.MobileProjectXCard.objects.filter(mobile_project=project).order_by('sortorder')
        ordered_ids = [unicode(mpc.card.cardid) for mpc in ordered_cards]
        project_dict = project.__dict__
        project_dict['cards'] = ordered_ids
        project_dict['users'] = [u.id for u in project.users.all()]
        project_dict['groups'] = [g.id for g in project.users.all()]

        return JSONResponse({'success':True, 'project': project_dict})


    def get_project_users(self, project):
        users = set(project.users.all())

        for group in project.groups.all():
            users |= set(group.user_set.all())

        return users

    def notify_project_start(self, request, project):
        admin_email = settings.ADMINS[0][1] if settings.ADMINS else ''
        email_context = {
            'button_text': _('Logon to {app_name}'.format(app_name=settings.APP_NAME)),
            'link':request.build_absolute_uri(reverse('home')),
            'greeting': _('Welcome to Arches!  You\'ve just been added to a Mobile Project.  Please take a moment to review the project description and project start and end dates.'),
            'closing': _('If you have any qustions contact the site administrator at {admin_email}.'.format(admin_email=admin_email)),
        }

        html_content = render_to_string('email/general_notification.htm', email_context)
        text_content = strip_tags(html_content) # this strips the html, so people will have the text as well.

        # create the email, and attach the HTML version as well.
        for user in self.get_project_users(project):
            msg = EmailMultiAlternatives(_('You\'ve been invited to an {app_name} Project!'.format(app_name=settings.APP_NAME)), text_content, admin_email, [user.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

    def notify_project_end(self, request, project):
        admin_email = settings.ADMINS[0][1] if settings.ADMINS else ''
        email_context = {
            'button_text': _('Logon to {app_name}'.format(app_name=settings.APP_NAME)),
            'link':request.build_absolute_uri(reverse('home')),
            'greeting': _('Hi!  The Mobile Project you were part of has ended or is temporarily suspended.  Please permform a final sync of your local dataset as soon as possible.'),
            'closing': _('If you have any qustions contact the site administrator at {admin_email}.'.format(admin_email=admin_email)),
        }

        html_content = render_to_string('email/general_notification.htm', email_context)
        text_content = strip_tags(html_content) # this strips the html, so people will have the text as well.

        # create the email, and attach the HTML version as well.
        for user in self.get_project_users(project):
            msg = EmailMultiAlternatives(_('There\'s been a change to an {app_name} Project that you\'re part of!'.format(app_name=settings.APP_NAME)), text_content, admin_email, [user.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
