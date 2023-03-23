from django.http import JsonResponse
from django.views.generic import View

class Foo(View):
    def get(self, request):
        return JsonResponse({'foo': 'bar'})