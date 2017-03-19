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


from django.conf import settings
from django.http import HttpResponseNotFound
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
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
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Query, Terms
from arches.app.views.concept import Concept
from elasticsearch import Elasticsearch



@method_decorator(group_required('Resource Editor'), name='dispatch')
class ResourceListView(BaseManagerView):
    def get(self, request, graphid=None, resourceid=None):
        context = self.get_context_data(
            main_script='views/resource',
        )

        context['nav']['icon'] = "fa fa-bookmark"
        context['nav']['title'] = "Resource Manager"
        context['nav']['edit_history'] = True
        context['nav']['login'] = True
        context['nav']['help'] = (_('Creating and Editing Resources'),'')

        return render(request, 'views/resource.htm', context)


@method_decorator(group_required('Resource Editor'), name='dispatch')
class ResourceEditorView(BaseManagerView):
    def get(self, request, graphid=None, resourceid=None):
        if graphid is not None:
            # self.graph = Graph.objects.get(graphid=graphid)
            resource_instance = Resource.objects.create(graph_id=graphid)
            resource_instance.index()
            return redirect('resource_editor', resourceid=resource_instance.pk)
        if resourceid is not None:
            resource_instance = models.ResourceInstance.objects.get(pk=resourceid)
            resource_graphs = Graph.objects.exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID).exclude(isresource=False).exclude(isactive=False)
            graph = Graph.objects.get(graphid=resource_instance.graph.pk)
            resource_relationship_types = Concept().get_child_concepts('00000000-0000-0000-0000-000000000005', ['member', 'hasTopConcept'], ['prefLabel'], 'prefLabel')
            default_relationshiptype_valueid = None
            for relationship_type in resource_relationship_types:
                if relationship_type[1] == '00000000-0000-0000-0000-000000000007':
                    default_relationshiptype_valueid = relationship_type[5]
            relationship_type_values = {'values':[{'id':str(c[5]), 'text':str(c[3])} for c in resource_relationship_types], 'default': str(default_relationshiptype_valueid)}
            form = Form(resource_instance.pk)
            datatypes = models.DDataType.objects.all()
            widgets = models.Widget.objects.all()
            map_layers = models.MapLayers.objects.all()
            map_sources = models.MapSources.objects.all()
            forms = resource_instance.graph.form_set.filter(visible=True)
            forms_x_cards = models.FormXCard.objects.filter(form__in=forms)
            forms_w_cards = [form_x_card.form for form_x_card in forms_x_cards]
            displayname = Resource.objects.get(pk=resourceid).displayname
            if displayname == 'undefined':
                displayname = 'Unnamed Resource' 

            context = self.get_context_data(
                main_script='views/resource/editor',
                resource_type=resource_instance.graph.name,
                relationship_types=relationship_type_values,
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
                displayname=displayname,
            )

            if graph.iconclass:
                context['nav']['icon'] = graph.iconclass
            context['nav']['title'] = graph.name
            context['nav']['menu'] = True
            context['nav']['edit_history'] = True
            context['nav']['help'] = (_('Creating and Editing Resources'),'')

            return render(request, 'views/resource/editor.htm', context)

        return HttpResponseNotFound()

    def delete(self, request, resourceid=None):
        if resourceid is not None:
            ret = Resource.objects.get(pk=resourceid)
            ret.delete()
            return JSONResponse(ret)
        return HttpResponseNotFound()


@method_decorator(group_required('Resource Editor'), name='dispatch')
class ResourceData(View):
    def get(self, request, resourceid=None, formid=None):
        if formid is not None:
            form = Form(resourceid=resourceid, formid=formid)
            return JSONResponse(form)

        return HttpResponseNotFound()


class ResourceDescriptors(View):
    def get(self, request, resourceid=None):
        if resourceid is not None:
            resource = Resource.objects.get(pk=resourceid)
            return JSONResponse({
                'graphid': resource.graph.pk,
                'graph_name': resource.graph.name,
                'displaydescription': resource.displaydescription,
                'map_popup': resource.map_popup,
                'displayname': resource.displayname,
            })

        return HttpResponseNotFound()

@method_decorator(group_required('Resource Editor'), name='dispatch')
class ResourceReportView(BaseManagerView):
    def get(self, request, resourceid=None):
        resource_instance = models.ResourceInstance.objects.get(pk=resourceid)
        tiles = models.TileModel.objects.filter(resourceinstance=resource_instance)
        try:
           report = models.Report.objects.get(graph=resource_instance.graph, active=True)
        except models.Report.DoesNotExist:
           report = None
        graph = Graph.objects.get(graphid=resource_instance.graph.pk)
        resource_graphs = Graph.objects.exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID).exclude(isresource=False).exclude(isactive=False)
        forms = resource_instance.graph.form_set.filter(visible=True)
        forms_x_cards = models.FormXCard.objects.filter(form__in=forms).order_by('sortorder')
        cards = Card.objects.filter(nodegroup__parentnodegroup=None, graph=resource_instance.graph)
        datatypes = models.DDataType.objects.all()
        widgets = models.Widget.objects.all()
        map_layers = models.MapLayers.objects.all()
        map_sources = models.MapSources.objects.all()
        templates = models.ReportTemplate.objects.all()
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
            resourceid=resourceid,
         )

        if graph.iconclass:
            context['nav']['icon'] = graph.iconclass
        context['nav']['title'] = graph.name
        context['nav']['res_edit'] = True
        context['nav']['print'] = True
        context['nav']['print'] = True

        return render(request, 'views/resource/report.htm', context)

@method_decorator(group_required('Resource Editor'), name='dispatch')
class RelatedResourcesView(BaseManagerView):
    def get(self, request, resourceid=None):
        # lang = request.GET.get('lang', settings.LANGUAGE_CODE)
        start = request.GET.get('start', 0)
        resource = Resource.objects.get(pk=resourceid)
        related_resources = resource.get_related_resources(lang="en-US", start=start, limit=15)
        return JSONResponse(related_resources, indent=4)

    def delete(self, request, resourceid=None):
        es = Elasticsearch()
        se = SearchEngineFactory().create()
        req = dict(request.GET)
        ids_to_delete = req['resourcexids[]']
        root_resourceinstanceid = req['root_resourceinstanceid']
        for resourcexid in ids_to_delete:
            try:
                ret = models.ResourceXResource.objects.get(pk=resourcexid).delete()
            except:
                print 'resource relation does not exist'
        start = request.GET.get('start', 0)
        es.indices.refresh(index="resource_relations")
        resource = Resource.objects.get(pk=root_resourceinstanceid[0])
        related_resources = resource.get_related_resources(lang="en-US", start=start, limit=15)
        return JSONResponse(related_resources, indent=4)

    def post(self, request, resourceid=None):
        es = Elasticsearch()
        se = SearchEngineFactory().create()
        res = dict(request.POST)
        relationship_type = res['relationship_properties[relationship_type]'][0]
        datefrom = res['relationship_properties[datefrom]'][0]
        dateto = res['relationship_properties[dateto]'][0]
        dateto = None if dateto == '' else dateto
        datefrom = None if datefrom == '' else datefrom
        notes = res['relationship_properties[notes]'][0]
        root_resourceinstanceid = res['root_resourceinstanceid']
        instances_to_relate = []
        relationships_to_update = []
        if 'instances_to_relate[]' in res:
            instances_to_relate = res['instances_to_relate[]']
        if 'relationship_ids[]' in res:
            relationships_to_update = res['relationship_ids[]']

        def get_relatable_resources(graphid):
            """
            Takes the graphid of a resource, finds the graphs root node, and returns the relatable graphids
            """
            nodes = models.Node.objects.filter(graph_id=graphid)
            top_node = [node for node in nodes if node.istopnode==True][0]
            relatable_resources = [str(node.graph.graphid) for node in top_node.get_relatable_resources()]
            return relatable_resources

        def confirm_relationship_permitted(to_id, from_id):
            resource_instance_to = models.ResourceInstance.objects.filter(resourceinstanceid=to_id)[0]
            resource_instance_from = models.ResourceInstance.objects.filter(resourceinstanceid=from_id)[0]
            relatable_to = get_relatable_resources(resource_instance_to.graph.graphid)
            relatable_from = get_relatable_resources(resource_instance_from.graph.graphid)
            relatable_to_is_valid = str(resource_instance_to.graph.graphid) in relatable_from
            relatable_from_is_valid = str(resource_instance_from.graph.graphid) in relatable_to
            return (relatable_to_is_valid == True and relatable_from_is_valid == True)

        for instanceid in instances_to_relate:
            permitted = confirm_relationship_permitted(instanceid, root_resourceinstanceid[0])
            if permitted == True:
                rr = models.ResourceXResource(
                    resourceinstanceidfrom = Resource(root_resourceinstanceid[0]),
                    resourceinstanceidto = Resource(instanceid),
                    notes = notes,
                    relationshiptype = models.Value(relationship_type),
                    datestarted = datefrom,
                    dateended = dateto
                )
                rr.save()
            else:
                print 'relationship not permitted'

        for relationshipid in relationships_to_update:
            rr = models.ResourceXResource.objects.get(pk=relationshipid)
            rr.notes = notes
            rr.relationshiptype = models.Value(relationship_type)
            rr.datestarted = datefrom
            rr.dateended = dateto
            rr.save()

        start = request.GET.get('start', 0)
        es.indices.refresh(index="resource_relations")
        resource = Resource.objects.get(pk=root_resourceinstanceid[0])
        related_resources = resource.get_related_resources(lang="en-US", start=start, limit=15)
        return JSONResponse(related_resources, indent=4)
