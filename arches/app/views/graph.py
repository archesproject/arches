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

import itertools
import zipfile
import json
from django.conf import settings
from django.db import transaction
from django.shortcuts import render
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator, classonlymethod
from django.http import HttpResponseNotFound, QueryDict, HttpResponse
from django.views.generic import View, TemplateView
from arches.app.utils.decorators import group_required
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.models.graph import Graph, GraphValidationError
from arches.app.models.card import Card
from arches.app.models.concept import Concept
from arches.app.models import models
from arches.app.utils.data_management.resources.exporter import ResourceExporter
from arches.app.utils.data_management.resource_graphs.exporter import get_graphs_for_export, create_mapping_configuration_file
from arches.app.utils.data_management.resource_graphs import importer as GraphImporter
from arches.app.utils.data_management.arches_file_exporter import ArchesFileExporter
from arches.app.views.base import BaseManagerView
from tempfile import NamedTemporaryFile
from guardian.shortcuts import get_perms_for_model

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

class GraphBaseView(BaseManagerView):
    def get_context_data(self, **kwargs):
        context = super(GraphBaseView, self).get_context_data(**kwargs)
        try:
            context['graphid'] = self.graph.graphid
            context['graph'] = JSONSerializer().serializeToPython(self.graph)
            context['graph_json'] = JSONSerializer().serialize(self.graph)
            context['root_node'] = self.graph.node_set.get(istopnode=True)
        except:
            pass
        return context


@method_decorator(group_required('Graph Editor'), name='dispatch')
class GraphSettingsView(GraphBaseView):
    def get(self, request, graphid):
        self.graph = Graph.objects.get(graphid=graphid)
        icons = models.Icon.objects.order_by('name')
        resource_graphs = models.GraphModel.objects.filter(Q(isresource=True))
        resource_data = []
        node = models.Node.objects.get(graph_id=graphid, istopnode=True)
        relatable_resources = node.get_relatable_resources()
        for res in resource_graphs:
            if models.Node.objects.filter(graph=res, istopnode=True).count() > 0:
                node_model = models.Node.objects.get(graph=res, istopnode=True)
                resource_data.append({
                    'id': node_model.nodeid,
                    'graph': res,
                    'is_relatable': (node_model in relatable_resources)
                })

        ontologies = models.Ontology.objects.filter(parentontology=None)
        ontology_classes = models.OntologyClass.objects.values('source', 'ontology_id')

        context = self.get_context_data(
            main_script='views/graph/graph-settings',
            icons=JSONSerializer().serialize(icons),
            node_json=JSONSerializer().serialize(node),
            ontologies=JSONSerializer().serialize(ontologies),
            ontology_classes=JSONSerializer().serialize(ontology_classes),
            resource_data=JSONSerializer().serialize(resource_data),
            node_count=models.Node.objects.filter(graph=self.graph).count(),
        )

        context['nav']['title'] = self.graph.name
        context['nav']['menu'] = True
        context['nav']['help'] = ('Defining Settings','help/settings-help.htm')

        return render(request, 'views/graph/graph-settings.htm', context)

    def post(self, request, graphid):
        graph = Graph.objects.get(graphid=graphid)
        data = JSONDeserializer().deserialize(request.body)
        for key, value in data.get('graph').iteritems():
            if key in ['iconclass', 'name', 'author', 'description', 'isresource',
                'ontology_id', 'version',  'subtitle', 'isactive', 'mapfeaturecolor', 'mappointsize', 'maplinewidth']:
                setattr(graph, key, value)

        node = models.Node.objects.get(graph_id=graphid, istopnode=True)
        node.set_relatable_resources(data.get('relatable_resource_ids'))
        node.ontologyclass = data.get('ontology_class') if data.get('graph').get('ontology_id') is not None else None

        with transaction.atomic():
            graph.save()
            node.save()

        return JSONResponse({
            'success': True,
            'graph': graph,
            'relatable_resource_ids': [res.nodeid for res in node.get_relatable_resources()]
        })

@method_decorator(group_required('Graph Editor'), name='dispatch')
class GraphManagerView(GraphBaseView):
    def get(self, request, graphid):
        if graphid is None or graphid == '':
            root_nodes = models.Node.objects.filter(istopnode=True)
            context = self.get_context_data(
                main_script='views/graph',
                root_nodes=JSONSerializer().serialize(root_nodes),
            )

            context['nav']['title'] = 'Arches Designer'
            context['nav']['icon'] = 'fa-bookmark'
            context['nav']['help'] = ('About the Arches Designer','help/arches-designer-help.htm')

            return render(request, 'views/graph.htm', context)

        self.graph = Graph.objects.get(graphid=graphid)
        datatypes = models.DDataType.objects.all()
        branch_graphs = Graph.objects.exclude(pk=graphid).exclude(isresource=True).exclude(isactive=False)
        if self.graph.ontology is not None:
            branch_graphs = branch_graphs.filter(ontology=self.graph.ontology)
        lang = request.GET.get('lang', settings.LANGUAGE_CODE)
        concept_collections = Concept().concept_tree(mode='collections', lang=lang)

        context = self.get_context_data(
            main_script='views/graph/graph-manager',
            branches=JSONSerializer().serialize(branch_graphs),
            datatypes_json=JSONSerializer().serialize(datatypes),
            datatypes=datatypes,
            concept_collections=concept_collections,
            node_list={
                'title': _('Node List'),
                'search_placeholder': _('Find a node...')
            },
            permissions_list={
                'title': _('Permissions'),
                'search_placeholder': _('Find a group or user account')
            },
            branch_list={
                'title': _('Branch Library'),
                'search_placeholder': _('Find a graph branch')
            },
        )

        context['nav']['title'] = self.graph.name
        context['nav']['help'] = ('Using the Graph Manager','help/graph-designer-help.htm')
        context['nav']['menu'] = True

        return render(request, 'views/graph/graph-manager.htm', context)

    def delete(self, request, graphid):
        graph = Graph.objects.get(graphid=graphid)
        graph.delete()
        return JSONResponse({'succces':True})


@method_decorator(group_required('Graph Editor'), name='dispatch')
class GraphDataView(View):

    action = 'update_node'

    def get(self, request, graphid, nodeid=None):
        if self.action == 'export_graph':
            graph = get_graphs_for_export([graphid])
            graph['metadata'] = ArchesFileExporter().export_metadata()
            f = JSONSerializer().serialize(graph, indent=4)
            graph_name = JSONDeserializer().deserialize(f)['graph'][0]['name']

            response = HttpResponse(f, content_type='json/plain')
            response['Content-Disposition'] = 'attachment; filename="%s.json"' %(graph_name)
            return response
        elif self.action == 'export_mapping_file':
            files_for_export = create_mapping_configuration_file(graphid)
            file_name = Graph.objects.get(graphid=graphid).name

            buffer = StringIO()

            with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip:
                for f in files_for_export:
                    f['outputfile'].seek(0)
                    zip.writestr(f['name'], f['outputfile'].read())

            zip.close()
            buffer.flush()
            zip_stream = buffer.getvalue()
            buffer.close()

            response = HttpResponse()
            response['Content-Disposition'] = 'attachment; filename=' + file_name + '.zip'
            response['Content-length'] = str(len(zip_stream))
            response['Content-Type'] = 'application/zip'
            response.write(zip_stream)
            return response

        else:
            graph = Graph.objects.get(graphid=graphid)
            if self.action == 'get_related_nodes':
                ret = graph.get_valid_ontology_classes(nodeid=nodeid)

            elif self.action == 'get_valid_domain_nodes':
                ret = graph.get_valid_domain_ontology_classes(nodeid=nodeid)

            return JSONResponse(ret)

        return HttpResponseNotFound()

    def post(self, request, graphid=None):
        ret = {}

        try:
            if self.action == 'import_graph':
                graph_file = request.FILES.get('importedGraph').read()
                graphs = JSONDeserializer().deserialize(graph_file)['graph']
                ret = GraphImporter.import_graph(graphs)
            else:
                if graphid is not None:
                    graph = Graph.objects.get(graphid=graphid)
                data = JSONDeserializer().deserialize(request.body)

                if self.action == 'new_graph':
                    isresource = data['isresource'] if 'isresource' in data else False
                    name = _('New Resource Model') if isresource else _('New Branch')
                    author = request.user.first_name + ' ' + request.user.last_name
                    ret = Graph.new(name=name,is_resource=isresource,author=author)

                elif self.action == 'update_node':
                    graph.update_node(data)
                    ret = graph
                    graph.save()

                elif self.action == 'append_branch':
                    ret = graph.append_branch(data['property'], nodeid=data['nodeid'], graphid=data['graphid'])
                    graph.save()

                elif self.action == 'move_node':
                    ret = graph.move_node(data['nodeid'], data['property'], data['newparentnodeid'])
                    graph.save()

                elif self.action == 'clone_graph':
                    clone_data = graph.copy()
                    ret = clone_data['copy']
                    ret.save()
                    ret.copy_functions(graph, [clone_data['nodes'], clone_data['nodegroups']])
                    form_map = ret.copy_forms(graph, clone_data['cards'])
                    ret.copy_reports(graph, [form_map, clone_data['cards'], clone_data['nodes']])

            return JSONResponse(ret)
        except GraphValidationError as e:
            return JSONResponse({'status':'false','message':e.message, 'title':e.title}, status=500)

    def delete(self, request, graphid):
        data = JSONDeserializer().deserialize(request.body)
        if data and self.action == 'delete_node':
            graph = Graph.objects.get(graphid=graphid)
            graph.delete_node(node=data.get('nodeid', None))
            return JSONResponse({})

        return HttpResponseNotFound()


@method_decorator(group_required('Graph Editor'), name='dispatch')
class CardManagerView(GraphBaseView):
    def get(self, request, graphid):
        self.graph = Graph.objects.get(graphid=graphid)
        branch_graphs = Graph.objects.exclude(pk=graphid).exclude(isresource=True).exclude(isactive=False)
        if self.graph.ontology is not None:
            branch_graphs = branch_graphs.filter(ontology=self.graph.ontology)

        context = self.get_context_data(
            main_script='views/graph/card-manager',
            branches=JSONSerializer().serialize(branch_graphs),
        )

        context['nav']['title'] = self.graph.name
        context['nav']['menu'] = True
        context['nav']['help'] = ('Managing Cards','help/card-manager-help.htm')

        return render(request, 'views/graph/card-manager.htm', context)


@method_decorator(group_required('Graph Editor'), name='dispatch')
class CardView(GraphBaseView):
    def get(self, request, cardid):
        try:
            card = Card.objects.get(cardid=cardid)
        except(Card.DoesNotExist):
            # assume this is a graph id
            card = Card.objects.get(cardid=Graph.objects.get(graphid=cardid).get_root_card().cardid)
        self.graph = Graph.objects.get(graphid=card.graph_id)

        datatypes = models.DDataType.objects.all()
        widgets = models.Widget.objects.all()
        map_layers = models.MapLayers.objects.all()
        map_sources = models.MapSources.objects.all()
        resource_graphs = Graph.objects.exclude(pk=card.graph_id).exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID).exclude(isresource=False).exclude(isactive=False)
        lang = request.GET.get('lang', settings.LANGUAGE_CODE)
        concept_collections = Concept().concept_tree(mode='collections', lang=lang)

        ontology_properties = []
        parent_node = self.graph.get_parent_node(card.nodegroup_id)
        for item in self.graph.get_valid_ontology_classes(nodeid=card.nodegroup_id):
            if parent_node.ontologyclass in item['ontology_classes']:
                ontology_properties.append(item['ontology_property'])
        ontology_properties = sorted(ontology_properties, key=lambda item: item)

        context = self.get_context_data(
            main_script='views/graph/card-configuration-manager',
            graph_id=self.graph.pk,
            card=JSONSerializer().serialize(card),
            permissions=JSONSerializer().serialize([{'codename': permission.codename, 'name': permission.name} for permission in get_perms_for_model(card.nodegroup)]),
            datatypes_json=JSONSerializer().serialize(datatypes),
            datatypes=datatypes,
            widgets=widgets,
            widgets_json=JSONSerializer().serialize(widgets),
            map_layers=map_layers,
            map_sources=map_sources,
            resource_graphs=resource_graphs,
            concept_collections=concept_collections,
            ontology_properties=JSONSerializer().serialize(ontology_properties),
        )

        context['nav']['title'] = self.graph.name
        context['nav']['menu'] = True
        context['nav']['help'] = ('Configuring Cards and Widgets','help/card-designer-help.htm')

        return render(request, 'views/graph/card-configuration-manager.htm', context)

    def post(self, request, cardid):
        data = JSONDeserializer().deserialize(request.body)
        if data:
            card = Card(data)
            card.save()
            return JSONResponse(card)

        return HttpResponseNotFound()


@method_decorator(group_required('Graph Editor'), name='dispatch')
class FormManagerView(GraphBaseView):
    action = 'add_form'

    def get(self, request, graphid):
        self.graph = Graph.objects.get(graphid=graphid)
        context = self.get_context_data(
            main_script='views/graph/form-manager',
            forms=JSONSerializer().serialize(self.graph.form_set.all().order_by('sortorder')),
			cards=JSONSerializer().serialize(models.CardModel.objects.filter(graph=self.graph)),
            forms_x_cards=JSONSerializer().serialize(models.FormXCard.objects.filter(form__in=self.graph.form_set.all()).order_by('sortorder')),
        )

        context['nav']['title'] = self.graph.name
        context['nav']['menu'] = True
        context['nav']['help'] = ('Using the Menu Manager','help/menu-manager-help.htm')

        return render(request, 'views/graph/form-manager.htm', context)

    def post(self, request, graphid):
        graph = models.GraphModel.objects.get(graphid=graphid)
        ret = None
        with transaction.atomic():
            if self.action == 'reorder_forms':
                data = JSONDeserializer().deserialize(request.body)
                for i, form in enumerate(data['forms']):
                    formModel = models.Form.objects.get(formid=form['formid'])
                    formModel.sortorder = i
                    formModel.save()
                ret = data['forms']
            if self.action == 'add_form':
                form = models.Form(title=_('New Menu'), graph=graph)
                form.save()
                ret = form
        return JSONResponse(ret)

@method_decorator(group_required('Graph Editor'), name='dispatch')
class FormView(GraphBaseView):
    def get(self, request, formid):
        form = models.Form.objects.get(formid=formid)
        self.graph = Graph.objects.get(graphid=form.graph.pk)
        icons = models.Icon.objects.order_by('name')
        cards = models.CardModel.objects.filter(nodegroup__parentnodegroup=None, graph=self.graph)

        context = self.get_context_data(
            main_script='views/graph/form-configuration',
            graph_id=self.graph.pk,
            icons=JSONSerializer().serialize(icons),
            form=JSONSerializer().serialize(form),
            forms=JSONSerializer().serialize(self.graph.form_set.all()),
            cards=JSONSerializer().serialize(cards),
            forms_x_cards=JSONSerializer().serialize(models.FormXCard.objects.filter(form=form).order_by('sortorder')),
        )

        context['nav']['title'] = self.graph.name
        context['nav']['menu'] = True
        context['nav']['help'] = ('Configuring Menus','help/menu-designer-help.htm')

        return render(request, 'views/graph/form-configuration.htm', context)

    def post(self, request, formid):
        data = JSONDeserializer().deserialize(request.body)
        form = models.Form.objects.get(formid=formid)
        form.title = data['title']
        form.subtitle = data['subtitle']
        form.iconclass = data['iconclass']
        form.visible = data['visible']
        forms_x_cards = models.FormXCard.objects.filter(form=form)
        with transaction.atomic():
            forms_x_cards.delete()
            for sortorder, card in enumerate(data['cards']):
                form_x_card = models.FormXCard(
                    form=form,
                    card_id=card['cardid'],
                    sortorder=sortorder
                )
                form_x_card.save()
            form.save()
        return JSONResponse(data)

    def delete(self, request, formid):
        form = models.Form.objects.get(formid=formid)
        form.delete()
        return JSONResponse({'succces':True})

class DatatypeTemplateView(TemplateView):
    def get(sefl, request, template='text'):
        return render(request, 'views/graph/datatypes/%s.htm' % template)

@method_decorator(group_required('Graph Editor'), name='dispatch')
class ReportManagerView(GraphBaseView):
    def get(self, request, graphid):
        self.graph = Graph.objects.get(graphid=graphid)
        forms = models.Form.objects.filter(graph=self.graph, visible=True)
        forms_x_cards = models.FormXCard.objects.filter(form__in=forms).order_by('sortorder')
        cards = Card.objects.filter(nodegroup__parentnodegroup=None, graph=self.graph)
        datatypes = models.DDataType.objects.all()
        widgets = models.Widget.objects.all()
        context = self.get_context_data(
            main_script='views/graph/report-manager',
            reports=JSONSerializer().serialize(self.graph.report_set.all()),
            templates_json=JSONSerializer().serialize(models.ReportTemplate.objects.all()),
            forms=JSONSerializer().serialize(forms),
            forms_x_cards=JSONSerializer().serialize(forms_x_cards),
            cards=JSONSerializer().serialize(cards),
            datatypes_json=JSONSerializer().serialize(datatypes),
            widgets=widgets,
         )

        context['nav']['title'] = self.graph.name
        context['nav']['menu'] = True
        context['nav']['help'] = ('Managing Reports','help/report-manager-help.htm')

        return render(request, 'views/graph/report-manager.htm', context)

    def post(self, request, graphid):
        data = JSONDeserializer().deserialize(request.body)
        graph = models.GraphModel.objects.get(graphid=graphid)
        template = models.ReportTemplate.objects.get(templateid=data['template_id'])
        report = models.Report(name=_('New Report'), graph=graph, template=template, config=template.defaultconfig)
        report.save()
        return JSONResponse(report)

@method_decorator(group_required('Graph Editor'), name='dispatch')
class ReportEditorView(GraphBaseView):
    def get(self, request, reportid):
        report = models.Report.objects.get(reportid=reportid)
        self.graph = Graph.objects.get(graphid=report.graph.pk)
        forms = models.Form.objects.filter(graph=self.graph, visible=True)
        forms_x_cards = models.FormXCard.objects.filter(form__in=forms).order_by('sortorder')
        cards = Card.objects.filter(nodegroup__parentnodegroup=None, graph=self.graph)
        resource_graphs = Graph.objects.exclude(pk=report.graph.pk).exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID).exclude(isresource=False).exclude(isactive=False)
        datatypes = models.DDataType.objects.all()
        widgets = models.Widget.objects.all()
        templates = models.ReportTemplate.objects.all()
        map_layers = models.MapLayers.objects.all()
        map_sources = models.MapSources.objects.all()

        context = self.get_context_data(
            main_script='views/graph/report-editor',
            report=JSONSerializer().serialize(report),
            reports=JSONSerializer().serialize(self.graph.report_set.all()),
            report_templates=templates,
            templates_json=JSONSerializer().serialize(templates),
            forms=JSONSerializer().serialize(forms),
            forms_x_cards=JSONSerializer().serialize(forms_x_cards),
            cards=JSONSerializer().serialize(cards),
            datatypes_json=JSONSerializer().serialize(datatypes),
            resource_graphs=resource_graphs,
            widgets=widgets,
            graph_id=self.graph.pk,
            map_layers=map_layers,
            map_sources=map_sources,
         )

        context['nav']['title'] = self.graph.name
        context['nav']['menu'] = True
        context['nav']['help'] = ('Designing Reports','help/report-designer-help.htm')

        return render(request, 'views/graph/report-editor.htm', context)

    def post(self, request, reportid):
        data = JSONDeserializer().deserialize(request.body)
        report = models.Report.objects.get(reportid=reportid)
        graph = Graph.objects.get(graphid=report.graph.pk)
        report.name = data['name']
        report.config = data['config']
        report.formsconfig = data['formsconfig']
        report.active = data['active']
        with transaction.atomic():
            if report.active:
                graph.report_set.exclude(reportid=reportid).update(active=False)
            report.save()
        return JSONResponse(report)

    def delete(self, request, reportid):
        report = models.Report.objects.get(reportid=reportid)
        report.delete()
        return JSONResponse({'succces':True})


@method_decorator(group_required('Graph Editor'), name='dispatch')
class FunctionManagerView(GraphBaseView):
    action = ''

    def get(self, request, graphid):
        self.graph = Graph.objects.get(graphid=graphid)

        context = self.get_context_data(
            main_script='views/graph/function-manager',
            functions=JSONSerializer().serialize(models.Function.objects.all()),
            applied_functions=JSONSerializer().serialize(models.FunctionXGraph.objects.filter(graph=self.graph)),
            function_templates=models.Function.objects.exclude(component__isnull=True),
        )

        context['nav']['title'] = self.graph.name
        context['nav']['menu'] = True
        context['nav']['help'] = ('Managing Functions','help/function-help.htm')

        return render(request, 'views/graph/function-manager.htm', context)

    def post(self, request, graphid):
        data = JSONDeserializer().deserialize(request.body)

        with transaction.atomic():
            for item in data:
                functionXgraph, created = models.FunctionXGraph.objects.update_or_create(
                    pk=item['id'],
                    defaults = {
                        'function_id': item['function_id'],
                        'graph_id': graphid,
                        'config': item['config']
                    }
                )
                item['id'] = functionXgraph.pk

        return JSONResponse(data)

    def delete(self, request, graphid):
        data = JSONDeserializer().deserialize(request.body)

        with transaction.atomic():
            for item in data:
                functionXgraph = models.FunctionXGraph.objects.get(pk=item['id'])
                functionXgraph.delete()

        return JSONResponse(data)
