from django.shortcuts import render
from django.views.generic import View
from django.db.models import Q
from revproxy.views import ProxyView

from arches.app.models import models
from arches.app.models.project import Project
from arches.app.models.system_settings import settings
from arches.app.utils.response import JSONResponse

class CouchdbProxy(ProxyView):
    #check user credentials here
    upstream = settings.COUCHDB_URL

class Surveys(View):
    def get(self, request):
        group_ids = list(request.user.groups.values_list('id', flat=True))
        projects = models.MobileSurveyModel.objects.filter(Q(users__in=[request.user]) | Q(groups__in=group_ids), active=True)
        response = JSONResponse(projects, indent=4)
        return response
