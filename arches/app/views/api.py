from django.shortcuts import render
from django.views.generic import View
from django.db.models import Q
from django.http.request import QueryDict
from revproxy.views import ProxyView

from arches.app.models import models
from arches.app.models.mobile_survey import MobileSurvey
from arches.app.models.system_settings import settings
from arches.app.utils.response import JSONResponse
from arches.app.utils.betterJSONSerializer import JSONSerializer


class CouchdbProxy(ProxyView):
    #check user credentials here
    upstream = settings.COUCHDB_URL


class APIBase(View):
    def dispatch(self, request, *args, **kwargs):
        get_params = request.GET.copy()
        for key, value in request.META.iteritems():
            if key.startswith('HTTP_X_ARCHES_'):
                if key.replace('HTTP_X_ARCHES_','').lower() not in request.GET:
                    get_params[key.replace('HTTP_X_ARCHES_','').lower()] = value

        get_params._mutable = False
        request.GET = get_params
        return super(APIBase, self).dispatch(request, *args, **kwargs)


class Surveys(APIBase):
    def get(self, request):
        group_ids = list(request.user.groups.values_list('id', flat=True))
        projects = MobileSurvey.objects.filter(Q(users__in=[request.user]) | Q(groups__in=group_ids), active=True)
        response = JSONResponse(projects, indent=4)
        return response
