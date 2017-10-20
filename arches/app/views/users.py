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

from django.shortcuts import render
from django.utils.translation import ugettext as _
import django.contrib.auth.password_validation as validation
from arches.app.views.base import BaseManagerView
from arches.app.utils.forms import ArchesUserProfileForm

class UserManagerView(BaseManagerView):

    def get(self, request):

        context = self.get_context_data(
            main_script='views/user-profile-manager',
        )

        context['nav']['icon'] = "fa fa-user"
        context['nav']['title'] = _("Profile Manager")
        context['nav']['login'] = True
        context['nav']['help'] = (_('Profile Editing'),'help/profile-manager-help.htm')
        context['validation_help'] = validation.password_validators_help_texts()
        return render(request, 'views/user-profile-manager.htm', context)

    def post(self, request):

        context = self.get_context_data(
            main_script='views/user-profile-manager',
        )
        context['errors'] = []
        context['nav']['icon'] = 'fa fa-user'
        context['nav']['title'] = _('Profile Manager')
        context['nav']['login'] = True
        context['nav']['help'] = (_('Profile Editing'),'help/profile-manager-help.htm')
        context['validation_help'] = validation.password_validators_help_texts()


        user_info = request.POST.copy()
        user_info['id'] = request.user.id
        user_info['username'] = request.user.username
        
        form = ArchesUserProfileForm(user_info)
        if form.is_valid():
            user = form.save()
            request.user = user
        context['form'] = form

        return render(request, 'views/user-profile-manager.htm', context)
