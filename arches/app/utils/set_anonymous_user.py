from django.contrib.auth.models import User, Group
from django.utils.deprecation import MiddlewareMixin

class SetAnonymousUser(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_anonymous():
            try:
                request.user = User.objects.get(username='anonymous')
            except:
                pass
            
        request.user.user_groups = [group.name for group in request.user.groups.all()]
