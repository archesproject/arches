from django.shortcuts import render
from django.views.generic import View
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
        projects = models.MobileSurveyModel.objects.all()
        response = JSONResponse(projects, indent=4)
        response['Access-Control-Allow-Origin'] = '*'
        return response
