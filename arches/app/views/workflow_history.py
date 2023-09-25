from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from arches.app.utils.response import JSONResponse
from arches.app.models import models
import json

class WorkflowHistoryView(View):

    def get(self, request, workflowid):
        try:
            workflow_history = models.WorkflowHistory.objects.get(workflowid=workflowid)
        except ObjectDoesNotExist as e:
            workflow_history = {}
        return JSONResponse(workflow_history, status=200)

    def post(self, request, workflowid):
        data = json.loads(request.body)
        # try:
        #     workflow_history = models.WorkflowHistory.objects.get(workflowid=workflowid)
        #     workflow_history.completed = data['completed']
        #     workflow_history.save()
        # except models.WorkflowHistory.DoesNotExist:
        #     models.WorkflowHistory.objects.udpate_or_create(
        #         workflowid=data['workflowid'],
        #         workflowdata=data['workflowdata'],
        #         user=request.user,
        #         completed=data['completed']
        #     )
        models.WorkflowHistory.objects.update_or_create(
            workflowid = data["workflowid"],
            defaults = {
                "workflowid": data["workflowid"],
                "workflowdata": data["workflowdata"],
                "user": request.user,
                "completed": data["completed"]
                },
            )
        return JSONResponse({'success': True}, status=200)