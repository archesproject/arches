from django.conf import settings
from django.contrib.auth.models import User, Group

class SetAnonymousUser(object):
    def process_request(self, request):
        if request.user.is_anonymous():
            request.user = User.objects.get(username='anonymous')
            request.user.user_groups = [group.name for group in request.user.groups.all()]
        else:
            request.user.user_groups = [group.name for group in request.user.groups.all()]