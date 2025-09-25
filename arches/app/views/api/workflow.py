import json

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import F, JSONField, Value
from django.db.models.expressions import CombinedExpression
from django.db.utils import IntegrityError
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import View

from arches.app.models import models
from arches.app.utils.betterJSONSerializer import JSONDeserializer, JSONSerializer
from arches.app.utils.decorators import group_required
from arches.app.utils.permission_backend import user_is_resource_editor
from arches.app.utils.response import JSONErrorResponse, JSONResponse
from arches.app.views.api import APIBase


class UserIncompleteWorkflows(APIBase):
    def get(self, request):
        if not user_is_resource_editor(request.user):
            return JSONErrorResponse(
                _("Request Failed"), _("Permission Denied"), status=403
            )

        if request.user.is_superuser:
            incomplete_workflows = (
                models.WorkflowHistory.objects.filter(completed=False)
                .exclude(componentdata__iexact="{}")
                .order_by("created")
            )
        else:
            incomplete_workflows = (
                models.WorkflowHistory.objects.filter(
                    user=request.user, completed=False
                )
                .exclude(componentdata__iexact="{}")
                .order_by("created")
            )

        incomplete_workflows_user_ids = [
            incomplete_workflow.user_id for incomplete_workflow in incomplete_workflows
        ]

        incomplete_workflows_users = models.User.objects.filter(
            pk__in=set(incomplete_workflows_user_ids)
        )

        user_ids_to_usernames = {
            incomplete_workflows_user.pk: incomplete_workflows_user.username
            for incomplete_workflows_user in incomplete_workflows_users
        }

        plugins = models.Plugin.objects.all()

        workflow_slug_to_workflow_name = {
            plugin.componentname: plugin.name for plugin in plugins
        }

        incomplete_workflows_json = JSONDeserializer().deserialize(
            JSONSerializer().serialize(incomplete_workflows)
        )

        for incomplete_workflow in incomplete_workflows_json:
            incomplete_workflow["username"] = user_ids_to_usernames[
                incomplete_workflow["user_id"]
            ]
            incomplete_workflow["pluginname"] = workflow_slug_to_workflow_name[
                incomplete_workflow["workflowname"]
            ]

        return JSONResponse(
            {
                "incomplete_workflows": incomplete_workflows_json,
                "requesting_user_is_superuser": request.user.is_superuser,
            }
        )


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
        completed = data.get("completed", False)

        # Required parameters.
        workflowid = data["workflowid"]
        workflowname = data["workflowname"]

        with transaction.atomic():
            try:
                (
                    history,
                    created,
                ) = models.WorkflowHistory.objects.select_for_update().update_or_create(
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

                if completed:
                    history.completed = True
                    history.user_id = request.user.pk
                    history.save()

        return JSONResponse({"success": True}, status=200)
