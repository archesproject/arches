
from django.views.generic import View
from arches.app.utils.response import JSONResponse
from django.http import HttpResponseNotFound

class UserTaskView(View):

    def get(self, request):
        action = ""

        if request.user.is_authenticated:
            tasks = models.UserXTask.objects.filter(user_id=request.user.id)
            if len(tasks) > 0:
                return JSONResponse({"tasks": tasks})

        return HttpResponseNotFound()