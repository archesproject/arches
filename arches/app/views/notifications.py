import json
from django.views.generic import View
from django.core.paginator import Paginator

from arches.app.models import models
from arches.app.utils.pagination import get_paginator
from arches.app.utils.response import JSONResponse


class NotificationView(View):
    action = ""

    def get(self, request):
        if not request.user.is_authenticated:
            return JSONResponse(
                {"error": "User not authenticated. Access denied."}, status=401
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

            notiftype_dict_list = [_type.__dict__ for _type in default_types]
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

            # To maintain back-compat, funnel filtered notifs through common variable
            if unread_only:
                user_notifications = unread_notifications
            else:
                user_notifications = all_user_notifications

            page = request.GET.get("page")
            if page:
                page = int(page)
                count_per_page = request.GET.get("items", 10)
                paginated_notifications = (
                    Paginator(user_notifications, count_per_page).page(page).object_list
                )
                total_count = user_notifications.count()
                paginator, pages = get_paginator(
                    request,
                    user_notifications,
                    total_count,
                    page,
                    count_per_page,
                )
                page = paginator.page(page)
                paginator_details = {
                    "current_page": page,
                    "has_next": page.has_next(),
                    "has_previous": page.has_previous(),
                    "has_other_pages": page.has_other_pages(),
                    "next_page_number": (
                        page.next_page_number() if page.has_next() else None
                    ),
                    "previous_page_number": (
                        page.previous_page_number() if page.has_previous() else None
                    ),
                    "start_index": page.start_index(),
                    "end_index": page.end_index(),
                    "pages": pages,
                }
                if unread_only:
                    paginator_details.update(
                        {
                            "total_notifications": all_user_notifications.count(),
                            "unread_notifications": total_count,
                        }
                    )
                else:
                    paginator_details.update(
                        {
                            "total_notifications": total_count,
                            "unread_notifications": unread_notifications.count(),
                        }
                    )
                response["paginator"] = paginator_details
                user_notifications = paginated_notifications

            # prefetch UserXNotificationType objects to avoid N+1 queries
            user_notification_type_overrides = (
                models.UserXNotificationType.objects.filter(
                    user=request.user, webnotify=False
                ).values_list("notiftype", flat=True)
            )

            notif_dict_list = []
            for user_notification in user_notifications:
                if (
                    user_notification.notif.notiftype
                    not in user_notification_type_overrides
                ):
                    notif = user_notification.__dict__
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
