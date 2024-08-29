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
from arches.app.models.models import WorkflowHistory


@method_decorator(
    group_required("Resource Editor", raise_exception=True), name="dispatch"
)
class WorkflowHistoryView(View):

    def get(self, request, workflowid):
        try:
            if request.user.is_superuser:
                workflow_history = WorkflowHistory.objects.get(workflowid=workflowid)
            else:
                workflow_history = WorkflowHistory.objects.get(
                    workflowid=workflowid, user=request.user
                )
        except WorkflowHistory.DoesNotExist:
            workflow_history = {}

        return JSONResponse(workflow_history, status=200)

    def post(self, request, workflowid):
        data = json.loads(request.body)
        stepdata = data.get("stepdata", {})
        componentdata = data.get("componentdata", {})
        completed = data.get("completed", False)

        # Required parameters.
        workflowid = data["workflowid"]
        workflowname = data["workflowname"]

        with transaction.atomic():
            try:
                (
                    history,
                    created,
                ) = WorkflowHistory.objects.select_for_update().update_or_create(
                    workflowid=workflowid,
                    workflowname=workflowname,
                    user=request.user,
                    defaults={
                        # Preserve existing keys, so that the client no longer has to
                        # GET existing data, which is slower and race-condition prone.
                        "stepdata": CombinedExpression(
                            F("stepdata"),
                            "||",
                            Value(stepdata, output_field=JSONField()),
                        ),
                        "componentdata": CombinedExpression(
                            F("componentdata"),
                            "||",
                            Value(componentdata, output_field=JSONField()),
                        ),
                    },
                    create_defaults={
                        "stepdata": stepdata,
                        "componentdata": componentdata,
                        "completed": completed,
                    },
                )
            except IntegrityError:  # user mismatch
                if request.user.is_superuser:
                    created = False
                    history = WorkflowHistory.objects.select_for_update().get(
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

                if completed:
                    history.completed = True
                    history.user_id = request.user.pk
                    history.save()

        return JSONResponse({"success": True}, status=200)
