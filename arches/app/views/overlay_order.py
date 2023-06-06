#Django
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _

#Core Arches
from arches.app.utils.decorators import can_edit_resource_instance
from arches.app.models.models import MapLayer, Node
from arches.app.views.base import BaseManagerView
from arches.app.utils.betterJSONSerializer import  JSONDeserializer
from django.http import HttpResponse

#Decorators
@method_decorator(can_edit_resource_instance, name="dispatch")
class OverlayOrder(BaseManagerView):
    def put(self, request):

        json = request.body
        data = JSONDeserializer().deserialize(json)
        maps = MapLayer.objects.all()
        for map in data['map_order']:
            print(map)
            try:
                temp = maps.get(maplayerid = map['maplayerid'])
                print(temp)
            except MapLayer.DoesNotExist:
                #Just to suppress any errors in the front end if stuff fails
                try:
                    temp = Node.objects.get(nodeid = map['maplayerid'])
                except Node.DoesNotExist:
                    temp = None
                else:
                    temp.overlaysortorder = map['overlaysortorder']
                    temp.save()
                    print(vars(temp))
            else:
                temp.sortorder = map['sortorder']
                temp.save()


        return HttpResponse("OK")
