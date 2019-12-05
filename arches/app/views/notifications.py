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
            notifs = models.UserXNotification.objects.filter(recipient=request.user).order_by("created").reverse()
            notif_dict_list = []
            for n in notifs:
                notif = n.__dict__
                notif["message"] = n.notif.message
                notif_dict_list.append(notif)

            return JSONResponse({"success": True, "notifications": notif_dict_list}, status=200)

        return JSONResponse({"error": "User not authenticated. Access denied."}, status=401)

    def post(self, request):
        if request.user.is_authenticated:
            dismiss_notifs = json.loads(request.POST.get("dismissals"))
            if isinstance(dismiss_notifs, str):
                dismissals = []
                dismissals.append(dismiss_notifs)
            else:
                dismissals = dismiss_notifs
            notifs = models.UserXNotification.objects.filter(pk__in=dismissals)
            for n in notifs:
                n.isread = True
            resp = models.UserXNotification.objects.bulk_update(notifs, ["isread"])

            return JSONResponse({"status": "success", "response": resp}, status=200)
        return JSONResponse({"status": "failed", "response": None}, status=500)
