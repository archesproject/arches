from django.views.generic import View
from arches.app.utils.response import JSONResponse
from arches.app.models import models


class NotificationView(View):
    action = ""

    def get(self, request):
        if request.user.is_authenticated:
            notifications = models.Notification.objects.filter(recipient_id=request.user.id)
            return JSONResponse({"success": True, "notifications": notifications}, status=200)

        return JSONResponse({"error": "User not authenticated. Access denied."}, status=401)
