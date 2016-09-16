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


from django.http import HttpResponseNotFound
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from arches.app.models import models
from arches.app.views.base import BaseManagerView
from arches.app.utils.decorators import group_required


@method_decorator(group_required('edit'), name='dispatch')
class ResourceListView(BaseManagerView):
    def get(self, request, graphid=None, resourceid=None):
        context = self.get_context_data(
            main_script='views/resource'
        )
        return render(request, 'views/resource.htm', context)


@method_decorator(group_required('edit'), name='dispatch')
class ResourceEditorView(TemplateView):
    def get(self, request, graphid=None, resourceid=None):
        if graphid is not None:
            # self.graph = Graph.objects.get(graphid=graphid)
            resource_instance = models.ResourceInstance.objects.create(graph_id=graphid)
            return redirect('resource_editor', resourceid=resource_instance.pk)
        if resourceid is not None:
            resource_instance = models.ResourceInstance.objects.get(pk=resourceid)
            context = self.get_context_data(
                main_script='views/resource/editor',
                resource_type=resource_instance.graph.name, 
                iconclass=resource_instance.graph.iconclass
            )
            return render(request, 'views/resource/editor.htm', context)
        
        return HttpResponseNotFound()