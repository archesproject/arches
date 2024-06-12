import json

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import F, JSONField, Value
from django.db.models.expressions import CombinedExpression
from django.db.utils import IntegrityError
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import View

from arches.app.utils.decorators import group_required
from arches.app.utils.response import JSONErrorResponse, JSONResponse
from arches.app.models import models


@method_decorator(
    group_required("Resource Editor", raise_exception=True), name="dispatch"
)
class WorkflowHistoryView(View):

    def get(self, request, workflowid):
        try:
            if request.user.is_superuser:
                workflow_history = models.WorkflowHistory.objects.get(
                    workflowid=workflowid
                )
            else:
                workflow_history = models.WorkflowHistory.objects.get(
                    workflowid=workflowid, user=request.user
                )
        except models.WorkflowHistory.DoesNotExist:
            workflow_history = {}

        return JSONResponse(workflow_history, status=200)

    def post(self, request, workflowid):
        data = json.loads(request.body)
        stepdata = data.get("stepdata", {})
        componentdata = data.get("componentdata", {})

        # TODO(Django 5.0) rewrite as a simpler update_or_create()
        # call using different `defaults` vs. `create_defaults`
        with transaction.atomic():
            workflowid = data["workflowid"]
            workflowname = data["workflowname"]
            try:
                (
                    history,
                    created,
                ) = models.WorkflowHistory.objects.select_for_update().get_or_create(
                    workflowid=workflowid,
                    workflowname=workflowname,
                    user=request.user,
                    defaults={
                        "stepdata": stepdata,
                        "componentdata": componentdata,
                        "workflowname": workflowname,
                        "user": request.user,
                        "completed": data.get("completed", False),
                    },
                )
            except IntegrityError:  # user mismatch
                if request.user.is_superuser:
                    created = False
                    history = models.WorkflowHistory.objects.select_for_update().get(
                        workflowid=workflowid,
                    )
                else:
                    raise PermissionDenied

            if not created:
                if history.completed:
                    return JSONErrorResponse(
                        _("Request Failed"),
                        _("Workflow already completed"),
                        status=400,
                    )

                history.completed = data.get("completed", False)
                if history.completed:
                    history.user_id = request.user.pk

                # Preserve existing keys, so that the client no longer has to
                # GET existing data, which is slower and race-condition prone.
                history.stepdata = CombinedExpression(
                    F("stepdata"),
                    "||",
                    Value(stepdata, output_field=JSONField()),
                )
                history.componentdata = CombinedExpression(
                    F("componentdata"),
                    "||",
                    Value(componentdata, output_field=JSONField()),
                )
                history.save()

        return JSONResponse({"success": True}, status=200)
