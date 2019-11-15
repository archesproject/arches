from django.views.generic import View
from arches.app.utils.response import JSONResponse
from django.http import HttpResponseNotFound
from arches.app.models import models


class UserTaskView(View):
    action = ""

    def get(self, request):

        if request.user.is_authenticated:
            if request.GET.get("action", None) == "get_all":
                tasks = models.UserXTask.objects.all()
            else:
                tasks = models.UserXTask.objects.filter(user_id=request.user.id)
            return JSONResponse({"tasks": tasks})

        return HttpResponseNotFound()
