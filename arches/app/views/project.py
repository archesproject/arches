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
from django.db import transaction
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.utils.decorators import group_required
from arches.app.models import models
from arches.app.views.base import BaseManagerView
from django.contrib.auth.models import User, Group

@method_decorator(group_required('Application Administrator'), name='dispatch')
class ProjectManagerView(BaseManagerView):
    def get(self, request):
        projects = models.MobileProject.objects.order_by('name')
        identities = []
        for group in Group.objects.all():
            identities.append({'name': group.name, 'type': 'group', 'id': group.pk, 'default_permissions': group.permissions.all()})
        for user in User.objects.filter():
            groups = []
            default_perms = []
            for group in user.groups.all():
                groups.append(group.name)
                default_perms = default_perms + list(group.permissions.all())
            identities.append({'name': user.email or user.username, 'groups': ', '.join(groups), 'type': 'user', 'id': user.pk, 'default_permissions': set(default_perms), 'is_superuser':user.is_superuser})
        context = self.get_context_data(
            projects=JSONSerializer().serialize(projects),
            identities=JSONSerializer().serialize(identities),
            main_script='views/project-manager',
        )

        context['nav']['title'] = _('Mobile Project Manager')
        context['nav']['icon'] = 'fa-server'
        context['nav']['help'] = (_('Mobile Project Manager'),'help/project-manager-help.htm')

        return render(request, 'views/project-manager.htm', context)

    def post(self, request):
        data = JSONDeserializer().deserialize(request.body)
        if data['id'] is None:
            project = models.MobileProject()
            project.createdby = self.request.user
        else:
            project = models.MobileProject.objects.get(pk=data['id'])
        project.name = data['name']
        project.active = data['active']
        project.lasteditedby = self.request.user
        with transaction.atomic():
            project.save()
        return JSONResponse({'success':True, 'project': project})
