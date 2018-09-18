from django.shortcuts import render
from arches.app.models import models
from arches.app.models.project import Project
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.response import JSONResponse
from revproxy.views import ProxyView

class CouchdbProxy(ProxyView):
    #check user credentials here
    upstream = settings.COUCHDB_URL

def index(request):
    # import ipdb
    # ipdb.set_trace()
    projects = models.MobileSurveyModel.objects.all().order_by('name')
    context = {
        "projects": projects
    }

    return render(request, 'pouch_demo.htm', context)

def myProjects(request):
    projects = models.MobileSurveyModel.objects.all()
    response = JSONResponse(projects, indent=4)
    response['Access-Control-Allow-Origin'] = '*'
    return response

def push_edits_to_db(request):
    project_id = request.GET.get('project_id', None)
    # read all docs that have changes
    # save back to postgres db
    project = Project.objects.get(pk=project_id)
    return JSONResponse(project.push_edits_to_db(), indent=4)