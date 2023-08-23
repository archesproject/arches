from django.views.generic import View
from arches.app.utils.response import JSONResponse
from arches.app.models import models
import json

class WorkflowHistoryView(View):

    def get(self, request, workflowid):
        workflow_history = models.WorkflowHistory.objects.get(workflowid=workflowid)
        return JSONResponse(workflow_history, status=200)

    def post(self, request, workflowid):
        data = json.loads(request.body)
        try:
            workflow_history = models.WorkflowHistory.objects.get(workflowid=workflowid)
            workflow_history.completed = data['completed']
            workflow_history.save()
        except models.WorkflowHistory.DoesNotExist:
            models.WorkflowHistory.objects.create(
                workflowid=data['workflowid'],
                workflowstepids=data['workflowstepids'],
                user=request.user,
                completed=data['completed']
            )
        return JSONResponse({'success': True}, status=200)