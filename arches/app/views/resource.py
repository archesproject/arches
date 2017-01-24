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
from django.views.generic import View
from arches.app.models import models
from arches.app.models.forms import Form
from arches.app.models.card import Card
from arches.app.models.graph import Graph
from arches.app.models.resource import Resource
from arches.app.views.base import BaseManagerView
from arches.app.utils.decorators import group_required
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.JSONResponse import JSONResponse


@method_decorator(group_required('edit'), name='dispatch')
class ResourceListView(BaseManagerView):
    def get(self, request, graphid=None, resourceid=None):
        instance_summaries = []
        for resource_instance in Resource.objects.all():
            instance_summaries.append({
                'id': resource_instance.pk,
                'name': resource_instance.primaryname,
                'type': resource_instance.graph.name,
                'last_edited': '',
                'qc': '',
                'public': '',
                'editor': ''
            })

        nav = self.get_default_nav()
        nav['page_title'] = "Resource Editor"
        nav['edit_history'] = True
        nav['login'] = True
        nav['help_title'] = 'Creating and Editing Resources'

        context = self.get_context_data(
            main_script='views/resource',
            instance_summaries=instance_summaries,
            nav=nav,
        )
        return render(request, 'views/resource.htm', context)


@method_decorator(group_required('edit'), name='dispatch')
class ResourceEditorView(BaseManagerView):
    def get(self, request, graphid=None, resourceid=None):
        if graphid is not None:
            # self.graph = Graph.objects.get(graphid=graphid)
            resource_instance = models.ResourceInstance.objects.create(graph_id=graphid)
            return redirect('resource_editor', resourceid=resource_instance.pk)
        if resourceid is not None:
            resource_instance = models.ResourceInstance.objects.get(pk=resourceid)
            resource_graphs = Graph.objects.exclude(pk=resource_instance.graph.pk).exclude(pk='22000000-0000-0000-0000-000000000002').exclude(isresource=False).exclude(isactive=False)
            graph = Graph.objects.get(graphid=resource_instance.graph.pk)
            form = Form(resource_instance.pk)
            datatypes = models.DDataType.objects.all()
            widgets = models.Widget.objects.all()
            map_layers = models.MapLayers.objects.all()
            map_sources = models.MapSources.objects.all()
            forms = resource_instance.graph.form_set.filter(visible=True)
            forms_x_cards = models.FormXCard.objects.filter(form__in=forms)
            forms_w_cards = [form_x_card.form for form_x_card in forms_x_cards]
 
            nav = self.get_default_nav()
            nav['page_title'] = graph.name
            nav['menu'] = True
            nav['edit_history'] = True
            nav['help_title'] = 'Creating and Editing Resources'

            context = self.get_context_data(
                main_script='views/resource/editor',
                resource_type=resource_instance.graph.name,
                iconclass=resource_instance.graph.iconclass,
                form=JSONSerializer().serialize(form),
                forms=JSONSerializer().serialize(forms_w_cards),
                datatypes_json=JSONSerializer().serialize(datatypes),
                widgets=widgets,
                map_layers=map_layers,
                map_sources=map_sources,
                widgets_json=JSONSerializer().serialize(widgets),
                resourceid=resourceid,
                resource_graphs=resource_graphs,
                graph_json=JSONSerializer().serialize(graph),
                nav=nav,
            )
            return render(request, 'views/resource/editor.htm', context)

        return HttpResponseNotFound()

    def delete(self, request, resourceid=None):
        if resourceid is not None:
            ret = models.ResourceInstance.objects.get(pk=resourceid).delete()
            return JSONResponse(ret)

        return HttpResponseNotFound()


@method_decorator(group_required('edit'), name='dispatch')
class ResourceData(View):
    def get(self, request, resourceid=None, formid=None):
        if formid is not None:
            form = Form(resourceid=resourceid, formid=formid)
            return JSONResponse(form)

        return HttpResponseNotFound()


@method_decorator(group_required('edit'), name='dispatch')
class ResourceReportView(BaseManagerView):
    def get(self, request, resourceid=None):
        resource_instance = models.ResourceInstance.objects.get(pk=resourceid)
        tiles = models.TileModel.objects.filter(resourceinstance=resource_instance)
        try:
           report = models.Report.objects.get(graph=resource_instance.graph, active=True)
        except models.Report.DoesNotExist:
           report = None
        graph = Graph.objects.get(graphid=resource_instance.graph.pk)
        resource_graphs = Graph.objects.exclude(pk=resource_instance.graph.pk).exclude(pk='22000000-0000-0000-0000-000000000002').exclude(isresource=False).exclude(isactive=False)
        forms = resource_instance.graph.form_set.filter(visible=True)
        forms_x_cards = models.FormXCard.objects.filter(form__in=forms).order_by('sortorder')
        cards = Card.objects.filter(nodegroup__parentnodegroup=None, graph=resource_instance.graph)
        datatypes = models.DDataType.objects.all()
        widgets = models.Widget.objects.all()
        map_layers = models.MapLayers.objects.all()
        map_sources = models.MapSources.objects.all()
        templates = models.ReportTemplate.objects.all()

        nav = self.get_default_nav()
        nav['page_title'] = graph.name
        nav['edit_resource'] = True
        nav['print'] = True

        context = self.get_context_data(
            main_script='views/resource/report',
            report=JSONSerializer().serialize(report),
            report_templates=templates,
            templates_json=JSONSerializer().serialize(templates),
            forms=JSONSerializer().serialize(forms),
            tiles=JSONSerializer().serialize(tiles),
            forms_x_cards=JSONSerializer().serialize(forms_x_cards),
            cards=JSONSerializer().serialize(cards),
            datatypes_json=JSONSerializer().serialize(datatypes),
            widgets=widgets,
            map_layers=map_layers,
            map_sources=map_sources,
            resource_graphs=resource_graphs,
            graph_id=resource_instance.graph.pk,
            graph_name=resource_instance.graph.name,
            graph_json = JSONSerializer().serialize(graph),
            nav=nav,
         )

        return render(request, 'views/resource/report.htm', context)
