import json

from django.db import transaction
from django.db.models import F, JSONField, Value
from django.db.models.expressions import CombinedExpression
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

        # TODO(Django 5.0) rewrite as a simpler update_or_create()
        # call using different `defaults` vs. `create_defaults`
        with transaction.atomic():
            workflowid = data["workflowid"]
            history, created = models.WorkflowHistory.objects.select_for_update().get_or_create(
                workflowid = workflowid,
                defaults = {
                    "workflowdata": data["workflowdata"],
                    "user": request.user,
                    "completed": data["completed"],
                },
            )
            if not created:
                # Don't allow patching the user or the workflow id.
                history.completed = data["completed"]
                # Preserve existing keys, so that the client no longer has to
                # GET existing data, which is slower and race-condition prone.
                history.workflowdata = CombinedExpression(
                    F("workflowdata"),
                    "||",
                    Value(data["workflowdata"], output_field=JSONField()),
                )
                history.save()

        return JSONResponse({'success': True}, status=200)
