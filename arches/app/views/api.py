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
            #print "%s - %s" % (key, value)
            if key.startswith('X_ARCHES_'):
                pass
            if key == 'HTTP_CACHE_CONTROL':
                get_params['HTTP_CACHE_CONTROL'] = value

        get_params._mutable = False
        request.GET = get_params
        return super(APIBase, self).dispatch(request, *args, **kwargs)

    # def get_param(self, request, param):
    #     return request.META['X_ARCHES_%s' % param.upper()] or request.GET.get(param) or request.POST.get(param)


class Surveys(APIBase):
    def get(self, request):
        print request.GET.get('HTTP_CACHE_CONTROL')
        #request.GET['HTTP_CACHE_CONTROL'] = 'taco'
        group_ids = list(request.user.groups.values_list('id', flat=True))
        projects = MobileSurvey.objects.filter(Q(users__in=[request.user]) | Q(groups__in=group_ids), active=True)
        response = JSONResponse(projects, indent=4)
        return response
