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


from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.views.base import BaseManagerView
from django.core.exceptions import ValidationError
import django.contrib.auth.password_validation as validation
from django.shortcuts import render
from django.utils.translation import ugettext as _

class UserManagerView(BaseManagerView):

    def get(self, request):

        context = self.get_context_data(
            main_script='views/user-profile-manager',
        )

        context['nav']['icon'] = "fa fa-user"
        context['nav']['title'] = _("Profile Manager")
        context['nav']['login'] = True
        context['nav']['help'] = (_('Creating Resources'),'help/resource-editor-landing-help.htm')
        context['validation_help'] = validation.password_validators_help_texts()
        return render(request, 'views/user-profile-manager.htm', context)

    def post(self, request):

        context = self.get_context_data(
            main_script='views/user-profile-manager',
        )
        context['nav']['icon'] = "fa fa-user"
        context['nav']['title'] = _("Profile Manager")
        context['nav']['login'] = True
        context['nav']['help'] = (_('Creating Resources'),'help/resource-editor-landing-help.htm')
        context['validation_help'] = validation.password_validators_help_texts()

        user = models.User.objects.get(pk=request.user.id)
        if user.username != request.POST.get('username'):
            in_use = models.User.objects.filter(username = request.POST.get('username')).count() > 0
            if in_use == True:
                try:
                    raise ValidationError(
                        _("The username, '{0}' is already in use".format(request.POST.get('username'))),
                        code='name in use',
                    )
                except ValidationError as e:
                    context["error"] = e[0]
                    print context["error"]
                    return render(request, 'views/user-profile-manager.htm', context)

        user.username = request.POST.get('username')
        user.first_name = request.POST.get('firstname')
        user.last_name = request.POST.get('lastname')
        user.email = request.POST.get('email')
        if models.UserProfile.objects.filter(user=user).count() == 0:
            models.UserProfile.objects.create(user=user)
        user.userprofile.phone = request.POST.get('phone')
        user.userprofile.save()
        user.save()
        request.user = user

        return render(request, 'views/user-profile-manager.htm', context)
