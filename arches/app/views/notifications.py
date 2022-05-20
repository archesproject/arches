from django.views.generic import View
from arches.app.utils.response import JSONResponse
from arches.app.models import models
import copy
import json
import logging


class NotificationView(View):
    action = ""

    def get(self, request):
        if request.user.is_authenticated:
            if self.action == "get_types":
                default_types = list(models.NotificationType.objects.all())
                user_types = models.UserXNotificationType.objects.filter(user=request.user, notiftype__in=default_types)
                for user_type in user_types:
                    if user_type.notiftype in default_types:  # find an overridden default_type and copy notify settings from user_type
                        i = default_types.index(user_type.notiftype)
                        default_type = default_types[i]
                        default_type.webnotify = user_type.webnotify
                        default_type.emailnotify = user_type.emailnotify

                notiftype_dict_list = [_type.__dict__ for _type in default_types]
                return JSONResponse({"success": True, "types": notiftype_dict_list}, status=200)

            else:
                if request.GET.get("unread_only"):
                    userxnotifs = (
                        models.UserXNotification.objects.filter(recipient=request.user, isread=False).order_by("notif__created").reverse()
                    )
                else:
                    userxnotifs = models.UserXNotification.objects.filter(recipient=request.user).order_by("notif__created").reverse()
                notif_dict_list = []
                for userxnotif in userxnotifs:
                    if (
                        models.UserXNotificationType.objects.filter(
                            user=request.user, notiftype=userxnotif.notif.notiftype, webnotify=False
                        ).exists()
                        is False
                    ):
                        notif = userxnotif.__dict__
                        notif["message"] = userxnotif.notif.message
                        notif["created"] = userxnotif.notif.created

                        if userxnotif.notif.context:
                            notif["loaded_resources"] = userxnotif.notif.context.get("loaded_resources", [])
                            notif["link"] = userxnotif.notif.context.get("link")

                        notif_dict_list.append(notif)

                return JSONResponse({"success": True, "notifications": notif_dict_list}, status=200)

        return JSONResponse({"error": "User not authenticated. Access denied."}, status=401)

    def post(self, request):
        if request.user.is_authenticated:
            if self.action == "update_types":
                # expects data payload of: types = [{"tyepid":some_id_123, "webnotify":true/false, "emailnotify":true/false}, ...]
                types = json.loads(request.POST.get("types"))
                for _type in types:
                    notif_type = models.NotificationType.objects.get(typeid=_type["typeid"])
                    user_type, created = models.UserXNotificationType.objects.update_or_create(
                        user=request.user,
                        notiftype=notif_type,
                        defaults=dict(webnotify=_type["webnotify"], emailnotify=_type["emailnotify"]),
                    )
                return JSONResponse({"status": "success"}, status=200)
            else:
                dismiss_notifs = json.loads(request.POST.get("dismissals"))
                if isinstance(dismiss_notifs, str):  # check if single notif id
                    dismissals = []
                    dismissals.append(dismiss_notifs)
                else:  # if already list
                    dismissals = dismiss_notifs
                notifs = models.UserXNotification.objects.filter(pk__in=dismissals)
                for n in notifs:
                    n.isread = True
                resp = models.UserXNotification.objects.bulk_update(notifs, ["isread"])

                return JSONResponse({"status": "success", "response": resp}, status=200)
        return JSONResponse({"status": "failed", "response": None}, status=500)
