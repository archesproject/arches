from django.http import HttpResponseNotFound
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

@method_decorator(never_cache, name='dispatch')
class SignupView(View):
    def get(self, request):
        return HttpResponseNotFound()

@method_decorator(never_cache, name='dispatch')
class ConfirmSignupView(View):
    def get(self, request):
        return HttpResponseNotFound()