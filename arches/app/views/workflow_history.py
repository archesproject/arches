import json

from django.utils.translation import gettext as _
from django.views.generic import View

from arches.app.utils.permission_backend import user_is_resource_reviewer
from arches.app.utils.response import JSONErrorResponse, JSONResponse
from arches.app.models import models


class WorkflowHistoryView(View):

    def get(self, request, workflowid):
        if not user_is_resource_reviewer(request.user):
            return JSONErrorResponse(_("Request Failed"), _("Permission Denied"), status=403)
        try:
            workflow_history = models.WorkflowHistory.objects.get(workflowid=workflowid)
        except models.WorkflowHistory.DoesNotExist:
            workflow_history = {}
        return JSONResponse(workflow_history, status=200)

    def post(self, request, workflowid):
        if not user_is_resource_reviewer(request.user):
            return JSONErrorResponse(_("Request Failed"), _("Permission Denied"), status=403)

        data = json.loads(request.body)
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
