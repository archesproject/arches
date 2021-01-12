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
from datetime import datetime
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, Group
import django.contrib.auth.password_validation as validation
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic import View
from arches.app.models import models
from arches.app.models.card import Card
from arches.app.models.mobile_survey import MobileSurvey
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.decorators import group_required
from arches.app.views.base import BaseManagerView
from arches.app.utils.forms import ArchesUserProfileForm
from arches.app.utils.response import JSONResponse
from arches.app.utils.permission_backend import user_is_resource_reviewer


class UserManagerView(BaseManagerView):
    action = ""

    def get_last_login(self, date):
        result = _("Not yet logged in")
        try:
            result = datetime.strftime(date, "%Y-%m-%d %H:%M")
        except TypeError as e:
            pass
        return result

    def get_user_details(self, user):
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
                        "last_login": self.get_last_login(user.last_login),
                        "username": user.username,
                        "groups": [gp.id for gp in user.groups.all()],
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

        user_mobile_surveys = [pxu.mobile_survey for pxu in models.MobileSurveyXUser.objects.filter(user=user)]
        user_mobile_surveys_by_group = [
            pxu_x_group.mobile_survey for pxu_x_group in models.MobileSurveyXGroup.objects.filter(group__in=user.groups.all())
        ]

        for gp in user_mobile_surveys_by_group:
            if gp not in user_mobile_surveys:
                user_mobile_surveys.append(gp)

        mobile_surveys, resources = self.get_mobile_survey_resources(user_mobile_surveys)

        return {"identities": identities, "user_surveys": mobile_surveys, "resources": resources}

    def get(self, request):

        if self.request.user.is_authenticated and self.request.user.username != "anonymous":
            context = self.get_context_data(
                main_script="views/user-profile-manager",
            )

            user_details = self.get_user_details(request.user)

            context["nav"]["icon"] = "fa fa-user"
            context["nav"]["title"] = _("Profile Manager")
            context["nav"]["login"] = True
            context["nav"]["help"] = {
                "title": _("Profile Editing"),
                "template": "profile-manager-help",
            }
            context["validation_help"] = validation.password_validators_help_texts()

            context["user_surveys"] = JSONSerializer().serialize(user_details["user_surveys"], sort_keys=False)
            context["identities"] = JSONSerializer().serialize(user_details["identities"], sort_keys=False)
            context["resources"] = JSONSerializer().serialize(user_details["resources"], sort_keys=False, exclude=["is_editable"])

            return render(request, "views/user-profile-manager.htm", context)

    def post(self, request):

        if self.action == "get_user_names":
            data = {}
            if self.request.user.is_authenticated and user_is_resource_reviewer(request.user):
                userids = json.loads(request.POST.get("userids", "[]"))
                data = {u.id: u.username for u in User.objects.filter(id__in=userids)}
                return JSONResponse(data)

        if self.request.user.is_authenticated and self.request.user.username != "anonymous":

            user_details = self.get_user_details(request.user)

            context = self.get_context_data(
                main_script="views/user-profile-manager",
            )
            context["errors"] = []
            context["nav"]["icon"] = "fa fa-user"
            context["nav"]["title"] = _("Profile Manager")
            context["nav"]["login"] = True
            context["nav"]["help"] = {
                "title": _("Profile Editing"),
                "template": "profile-manager-help",
            }
            context["validation_help"] = validation.password_validators_help_texts()
            context["user_surveys"] = JSONSerializer().serialize(user_details["user_surveys"])
            context["identities"] = JSONSerializer().serialize(user_details["identities"])
            context["resources"] = JSONSerializer().serialize(user_details["resources"])

            user_info = request.POST.copy()
            user_info["id"] = request.user.id
            user_info["username"] = request.user.username
            user_info["password1"] = request.user.password
            user_info["password2"] = request.user.password

            form = ArchesUserProfileForm(user_info)

            if form.is_valid():
                user = form.save()
                try:
                    admin_info = settings.ADMINS[0][1] if settings.ADMINS else ""
                    message = _(
                        "Your "
                        + settings.APP_NAME
                        + " profile was just changed.  If this was unexpected, please contact your "
                        + settings.APP_NAME
                        + " administrator at %s." % (admin_info)
                    )
                    user.email_user(_("Your " + settings.APP_NAME + " Profile Has Changed"), message)
                except Exception as e:
                    print(e)
                request.user = user
            context["form"] = form

            return render(request, "views/user-profile-manager.htm", context)

    def get_mobile_survey_resources(self, mobile_survey_models):
        graphs = models.GraphModel.objects.filter(isresource=True).exclude(graphid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
        resources = []
        mobile_surveys = []
        all_ordered_card_ids = []

        for mobile_survey in mobile_survey_models:
            survey = MobileSurvey.objects.get(id=mobile_survey.id)
            mobile_survey_dict = survey.serialize()
            all_ordered_card_ids += mobile_survey_dict["cards"]
            mobile_surveys.append(mobile_survey_dict)

        active_graphs = {str(card.graph_id) for card in models.CardModel.objects.filter(cardid__in=all_ordered_card_ids)}

        for i, graph in enumerate(graphs):
            cards = []
            if i == 0 or str(graph.graphid) in active_graphs:
                cards = [Card.objects.get(pk=card.cardid) for card in models.CardModel.objects.filter(graph=graph)]
            resources.append(
                {"name": graph.name, "id": graph.graphid, "subtitle": graph.subtitle, "iconclass": graph.iconclass, "cards": cards}
            )

        return mobile_surveys, resources
