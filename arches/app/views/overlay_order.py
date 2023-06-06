from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _

from arches.app.utils.decorators import can_edit_resource_instance
from arches.app.models.models import MapLayer, Node
from arches.app.views.base import BaseManagerView
from arches.app.utils.betterJSONSerializer import  JSONDeserializer
from django.http import HttpResponse

# Currently those who can edit resources can change overlay order
@method_decorator(can_edit_resource_instance, name="dispatch")
class OverlayOrder(BaseManagerView):
    def put(self, request):
        json = request.body
        data = JSONDeserializer().deserialize(json)
        maps = MapLayer.objects.all()
        for map in data['map_order']:
            try:
                temp = maps.get(maplayerid = map['maplayerid'])
            except MapLayer.DoesNotExist:
                # Try catch to suppress any errors in the front end 
                try:
                    temp = Node.objects.get(nodeid = map['maplayerid'])
                except Node.DoesNotExist:
                    temp = None
                else:
                    temp.overlaysortorder = map['overlaysortorder']
                    temp.save()
            else:
                temp.overlaysortorder = map['overlaysortorder']
                temp.save()

        return HttpResponse("OK")
