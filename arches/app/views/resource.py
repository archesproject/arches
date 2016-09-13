'''
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''


from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from arches.app.views.base import BaseNiftyView
from arches.app.utils.decorators import group_required


@method_decorator(group_required('edit'), name='dispatch')
class ResourceManagerView(BaseNiftyView):
    def get(self, request, graphid=None, resourceid=None):
        if graphid is not None:
            # self.graph = Graph.objects.get(graphid=graphid)
            return redirect('resource_editor', resourceid=graphid)
        if resourceid is not None:
            # object = MyModel.objects.get(...)
            return render(request, 'views/resource/editor.htm')
        
        context = self.get_context_data(
            main_script='views/resource'
        )
        return render(request, 'views/resource.htm', context)

