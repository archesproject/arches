from django.views.generic import View
from arches.app.utils.response import JSONResponse
from arches.app.models import models
from pprint import pprint
import copy
import json
from arches.app.utils.betterJSONSerializer import JSONSerializer
from django.forms.models import model_to_dict


class NotificationView(View):
    action = ""

    def get(self, request):
        if request.user.is_authenticated:
            notifs = models.Notification.objects.filter(recipient_id=request.user.id).order_by("created").reverse()
            return JSONResponse({"success": True, "notifications": notifs}, status=200)

        return JSONResponse({"error": "User not authenticated. Access denied."}, status=401)

    def post(self, request):
        if request.user.is_authenticated:
            dismiss_notifs = json.loads(request.POST.get("dismissals"))
            if isinstance(dismiss_notifs, str):
                dismissals = []
                dismissals.append(dismiss_notifs)
            else:
                dismissals = dismiss_notifs

            notifs = models.Notification.objects.filter(pk__in=dismissals)
            for n in notifs:
                n.is_read = True

            resp = models.Notification.objects.bulk_update(notifs, ["is_read"])

            return JSONResponse({"status": "success", "response": resp}, status=200)
        return JSONResponse({"status": "failed", "response": None}, status=500)
