import json
from django.views.generic import View
from django.core.paginator import Paginator
from django.utils.translation import gettext as _

from arches.app.models import models
from arches.app.utils.response import JSONResponse


class NotificationView(View):
    action = ""

    def get(self, request):
        if not request.user.is_authenticated:
            return JSONResponse(
                {"error": _("User not authenticated. Access denied.")}, status=401
            )

        if self.action == "get_types":
            default_types = list(models.NotificationType.objects.all())
            user_types = models.UserXNotificationType.objects.filter(
                user=request.user, notiftype__in=default_types
            )
            for user_type in user_types:
                if (
                    user_type.notiftype in default_types
                ):  # find an overridden default_type and copy notify settings from user_type
                    i = default_types.index(user_type.notiftype)
                    default_type = default_types[i]
                    default_type.webnotify = user_type.webnotify
                    default_type.emailnotify = user_type.emailnotify

            notiftype_dict_list = [_type.serialize() for _type in default_types]
            return JSONResponse(
                {"success": True, "types": notiftype_dict_list}, status=200
            )

        else:
            response = {}
            all_user_notifications = (
                models.UserXNotification.objects.filter(recipient=request.user)
                .select_related("notif")
                .order_by("notif__created")
                .reverse()
            )
            unread_notifications = all_user_notifications.filter(isread=False)
            unread_only = request.GET.get("unread_only", False)
            unread_only = True if str(unread_only).lower() == "true" else False

            # To maintain back-compat, funnel filtered notifs through common variable
            if unread_only:
                user_notifications = unread_notifications
            else:
                user_notifications = all_user_notifications

            page_number = request.GET.get("page")
            if page_number:
                page_number = int(page_number)
                count_per_page = int(request.GET.get("items", 10))
                paginator = Paginator(user_notifications, count_per_page)
                paginator_details = {
                    "current_page": page_number,
                    "total_pages": paginator.num_pages,
                    "results_per_page": paginator.per_page,
                    "has_next": paginator.num_pages > page_number,
                }
                if unread_only:
                    paginator_details.update(
                        {
                            "total_notifications": all_user_notifications.count(),
                            "unread_notifications": paginator.count,
                        }
                    )
                else:
                    paginator_details.update(
                        {
                            "total_notifications": paginator.count,
                            "unread_notifications": unread_notifications.count(),
                        }
                    )
                response["paginator"] = paginator_details
                user_notifications = paginator.page(page_number).object_list

            disabled_notification_type_ids = set(
                models.UserXNotificationType.objects.filter(
                    user=request.user,
                    webnotify=False,
                ).values_list("notiftype_id", flat=True)
            )

            notif_dict_list = []
            for user_notification in user_notifications:
                if (
                    user_notification.notif.notiftype_id
                    not in disabled_notification_type_ids
                ):
                    notif = user_notification.serialize()
                    notif["message"] = user_notification.notif.message
                    notif["created"] = user_notification.notif.created

                    if user_notification.notif.context:
                        notif["loaded_resources"] = user_notification.notif.context.get(
                            "loaded_resources", []
                        )
                        notif["link"] = user_notification.notif.context.get("link")
                        if user_notification.notif.context.get("files"):
                            notif["files"] = user_notification.notif.context.get(
                                "files"
                            )

                    notif_dict_list.append(notif)

            response["success"] = True
            response["notifications"] = notif_dict_list
            return JSONResponse(response, status=200)

    def post(self, request):
        if request.user.is_authenticated:
            if self.action == "update_types":
                # expects data payload of: types = [{"tyepid":some_id_123, "webnotify":true/false, "emailnotify":true/false}, ...]
                types = json.loads(request.POST.get("types"))
                for _type in types:
                    notif_type = models.NotificationType.objects.get(
                        typeid=_type["typeid"]
                    )
                    user_type, created = (
                        models.UserXNotificationType.objects.update_or_create(
                            user=request.user,
                            notiftype=notif_type,
                            defaults=dict(
                                webnotify=_type["webnotify"],
                                emailnotify=_type["emailnotify"],
                            ),
                        )
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
