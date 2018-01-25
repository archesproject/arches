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
import uuid
from django.db import transaction
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator, classonlymethod
from django.http import HttpResponseNotFound, QueryDict, HttpResponse
from django.views.generic import View, TemplateView
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from arches.app.utils.decorators import group_required
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.response import JSONResponse
from arches.app.models import models
from arches.app.models.graph import Graph, GraphValidationError
from arches.app.models.card import Card
from arches.app.models.concept import Concept
from arches.app.models.system_settings import settings
from arches.app.utils.data_management.resource_graphs.exporter import get_graphs_for_export, create_mapping_configuration_file
from arches.app.utils.data_management.resource_graphs import importer as GraphImporter
from arches.app.utils.system_metadata import system_metadata
from arches.app.views.base import BaseManagerView
from tempfile import NamedTemporaryFile
from guardian.shortcuts import get_perms_for_model, assign_perm, get_perms, remove_perm, get_group_perms, get_user_perms
from rdflib import Graph as RDFGraph, RDF, RDFS

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

def get_ontology_namespaces():
    ontology_namespaces = settings.ONTOLOGY_NAMESPACES
    g = RDFGraph()
    for ontology in models.Ontology.objects.all():
        g.parse(ontology.path.path)
    for namespace in g.namespaces():
        if str(namespace[1]) not in ontology_namespaces:
            ontology_namespaces[str(namespace[1])] = str(namespace[0])
    return ontology_namespaces


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
        resource_graphs = models.GraphModel.objects.filter(Q(isresource=True)).exclude(graphid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
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
            ontology_namespaces = get_ontology_namespaces()
        )

        context['nav']['title'] = self.graph.name
        context['nav']['menu'] = True
        context['nav']['help'] = (_('Defining Settings'),'help/base-help.htm')
        context['help'] = 'settings-help'

        return render(request, 'views/graph/graph-settings.htm', context)

    def post(self, request, graphid):
        graph = Graph.objects.get(graphid=graphid)
        data = JSONDeserializer().deserialize(request.body)
        for key, value in data.get('graph').iteritems():
            if key in ['iconclass', 'name', 'author', 'description', 'isresource',
                'ontology_id', 'version',  'subtitle', 'isactive']:
                setattr(graph, key, value)

        node = models.Node.objects.get(graph_id=graphid, istopnode=True)
        root_node_config = [graph_node['config'] for graph_node in data.get('graph').get('nodes') if graph_node['istopnode']==True][0]
        node.config = root_node_config
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
            context['nav']['help'] = (_('About the Arches Designer'),'help/base-help.htm')
            context['help'] = 'arches-designer-help'

            return render(request, 'views/graph.htm', context)

        self.graph = Graph.objects.get(graphid=graphid)
        datatypes = models.DDataType.objects.all()
        branch_graphs = Graph.objects.exclude(pk=graphid).exclude(isresource=True).exclude(isactive=False)
        if self.graph.ontology is not None:
            branch_graphs = branch_graphs.filter(ontology=self.graph.ontology)
        lang = request.GET.get('lang', settings.LANGUAGE_CODE)
        concept_collections = Concept().concept_tree(mode='collections', lang=lang)
        datatypes_json = JSONSerializer().serialize(datatypes, exclude=['iconclass','modulename','isgeometric'])
        context = self.get_context_data(
            main_script='views/graph/graph-manager',
            branches=JSONSerializer().serialize(branch_graphs, exclude=['cards','domain_connections', 'functions', 'cards', 'deploymentfile', 'deploymentdate']),
            datatypes_json=datatypes_json,
            datatypes=json.loads(datatypes_json),
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
            ontology_namespaces = get_ontology_namespaces()
        )
        context['nav']['title'] = self.graph.name
        context['nav']['help'] = (_('Using the Graph Manager'),'help/base-help.htm')
        context['nav']['menu'] = True
        context['help'] = 'graph-designer-help'

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
            graph['metadata'] = system_metadata()
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

        elif self.action == 'get_domain_connections':
            res = []
            graph = Graph.objects.get(graphid=graphid)
            ontology_class = request.GET.get('ontology_class', None)
            ret = graph.get_valid_domain_ontology_classes()
            for r in ret:
                res.append({'ontology_property': r['ontology_property'], 'ontology_classes':[c for c in r['ontology_classes'] if c == ontology_class]})
            return JSONResponse(res)

        else:
            graph = Graph.objects.get(graphid=graphid)
            if self.action == 'get_related_nodes':
                parent_nodeid = request.GET.get('parent_nodeid', None)
                ret = graph.get_valid_ontology_classes(nodeid=nodeid, parent_nodeid=parent_nodeid)

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

                elif self.action == 'update_node_layer':
                    nodeid = uuid.UUID(str(data.get('nodeid')))
                    node = graph.nodes[nodeid]
                    node.config = data['config']
                    ret = graph
                    node.save()

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
            try:
                graph = Graph.objects.get(graphid=graphid)
                graph.delete_node(node=data.get('nodeid', None))
                return JSONResponse({})
            except GraphValidationError as e:
                return JSONResponse({'status':'false','message':e.message, 'title':e.title}, status=500)

        return HttpResponseNotFound()


@method_decorator(group_required('Graph Editor'), name='dispatch')
class CardManagerView(GraphBaseView):
    def get(self, request, graphid):
        self.graph = Graph.objects.get(graphid=graphid)
        if self.graph.isresource == False:
            card = Card.objects.get(cardid=Graph.objects.get(graphid=graphid).get_root_card().cardid)
            cardid = card.cardid
            return redirect('card', cardid=cardid)

        branch_graphs = Graph.objects.exclude(pk=graphid).exclude(isresource=True).exclude(isactive=False)
        if self.graph.ontology is not None:
            branch_graphs = branch_graphs.filter(ontology=self.graph.ontology)

        context = self.get_context_data(
            main_script='views/graph/card-manager',
            branches=JSONSerializer().serialize(branch_graphs, exclude=['functions', 'relatable_resource_model_ids', 'domain_connections', 'nodes', 'edges']),
        )
        context['nav']['title'] = self.graph.name
        context['nav']['menu'] = True
        context['nav']['help'] = (_('Managing Cards'),'help/base-help.htm')
        context['help'] = 'card-manager-help'

        return render(request, 'views/graph/card-manager.htm', context)


@method_decorator(group_required('Graph Editor'), name='dispatch')
class CardView(GraphBaseView):
    def get(self, request, cardid):
        try:
            card = Card.objects.get(cardid=cardid)
            self.graph = Graph.objects.get(graphid=card.graph_id)
        except(Card.DoesNotExist):
            # assume the cardid is actually a graph id
            card = Card.objects.get(cardid=Graph.objects.get(graphid=cardid).get_root_card().cardid)
            self.graph = Graph.objects.get(graphid=card.graph_id)
            if self.graph.isresource == True:
                return redirect('card_manager', graphid=cardid)

        card.confirm_enabled_state(request.user, card.nodegroup)
        for c in card.cards:
            c.confirm_enabled_state(request.user, c.nodegroup)

        datatypes = models.DDataType.objects.all()
        widgets = models.Widget.objects.all()
        geocoding_providers = models.Geocoder.objects.all()
        map_layers = models.MapLayer.objects.all()
        map_sources = models.MapSource.objects.all()
        resource_graphs = Graph.objects.exclude(pk=card.graph_id).exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID).exclude(isresource=False).exclude(isactive=False)
        lang = request.GET.get('lang', settings.LANGUAGE_CODE)
        concept_collections = Concept().concept_tree(mode='collections', lang=lang)
        ontology_properties = []
        card_root_node = models.Node.objects.get(nodeid=card.nodegroup_id)
        for item in self.graph.get_valid_ontology_classes(nodeid=card.nodegroup_id):
            if card_root_node.ontologyclass in item['ontology_classes']:
                ontology_properties.append(item['ontology_property'])
        ontology_properties = sorted(ontology_properties, key=lambda item: item)

        context = self.get_context_data(
            main_script='views/graph/card-configuration-manager',
            graph_id=self.graph.pk,
            card=JSONSerializer().serialize(card),
            datatypes_json=JSONSerializer().serialize(datatypes),
            geocoding_providers=geocoding_providers,
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
        context['nav']['help'] = (_('Configuring Cards and Widgets'),'help/base-help.htm')
        context['help'] = 'card-designer-help'

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

        if self.graph.isresource == True:
            context = self.get_context_data(
                main_script='views/graph/form-manager',
                forms=JSONSerializer().serialize(self.graph.form_set.all().order_by('sortorder')),
    			cards=JSONSerializer().serialize(models.CardModel.objects.filter(graph=self.graph)),
                forms_x_cards=JSONSerializer().serialize(models.FormXCard.objects.filter(form__in=self.graph.form_set.all()).order_by('sortorder')),
            )

            context['nav']['title'] = self.graph.name
            context['nav']['menu'] = True
            context['nav']['help'] = (_('Using the Menu Manager'),'help/base-help.htm')
            context['help'] = 'menu-manager-help'

            return render(request, 'views/graph/form-manager.htm', context)
        else:
            return redirect('graph_settings', graphid=graphid)

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
                form.sortorder = len(graph.form_set.all())
                form.save()
                ret = form

        return JSONResponse(ret)

@method_decorator(group_required('Graph Editor'), name='dispatch')
class FormView(GraphBaseView):
    def get(self, request, formid):

        try:
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
            context['nav']['help'] = (_('Configuring Menus'),'help/base-help.htm')
            context['help'] = 'menu-designer-help'

            return render(request, 'views/graph/form-configuration.htm', context)

        except(models.Form.DoesNotExist):
            # assume the formid is a graph id
            graph = Graph.objects.get(graphid=formid)
            if graph.isresource == False:
                return redirect('graph_settings', graphid=graph.graphid)
            else:
                return redirect('form_manager', graphid=graph.graphid)


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
        return render(request, 'views/components/datatypes/%s.htm' % template)


@method_decorator(group_required('Graph Editor'), name='dispatch')
class ReportManagerView(GraphBaseView):
    def get(self, request, graphid):
        self.graph = Graph.objects.get(graphid=graphid)
        if self.graph.isresource:
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
            context['nav']['help'] = (_('Managing Reports'),'help/base-help.htm')
            context['help'] = 'report-manager-help'

            return render(request, 'views/graph/report-manager.htm', context)

        else:
            return redirect('graph_settings', graphid=graphid)

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
        try:
            report = models.Report.objects.get(reportid=reportid)
            self.graph = Graph.objects.get(graphid=report.graph.pk)
            forms = models.Form.objects.filter(graph=self.graph, visible=True)
            forms_x_cards = models.FormXCard.objects.filter(form__in=forms).order_by('sortorder')
            cards = Card.objects.filter(nodegroup__parentnodegroup=None, graph=self.graph)
            map_layers = models.MapLayer.objects.all()
            map_sources = models.MapSource.objects.all()
            resource_graphs = Graph.objects.exclude(pk=report.graph.pk).exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID).exclude(isresource=False).exclude(isactive=False)
            datatypes = models.DDataType.objects.all()
            widgets = models.Widget.objects.all()
            geocoding_providers = models.Geocoder.objects.all()
            templates = models.ReportTemplate.objects.all()
            map_sources = models.MapSource.objects.all()

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
                map_layers=map_layers,
                map_sources=map_sources,
                geocoding_providers=geocoding_providers,
                resource_graphs=resource_graphs,
                widgets=widgets,
                graph_id=self.graph.pk,
             )

            context['nav']['title'] = self.graph.name
            context['nav']['menu'] = True
            context['nav']['help'] = (_('Designing Reports'),'help/base-help.htm')
            context['help'] = 'report-designer-help'

            return render(request, 'views/graph/report-editor.htm', context)

        except(models.Report.DoesNotExist):
            # assume the reportid is a graph id
            graph = Graph.objects.get(graphid=reportid)
            if graph.isresource == False:
                return redirect('graph_settings', graphid=graph.graphid)
            else:
                return redirect('report_manager', graphid=graph.graphid)


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

        if self.graph.isresource:
            context = self.get_context_data(
                main_script='views/graph/function-manager',
                functions=JSONSerializer().serialize(models.Function.objects.all()),
                applied_functions=JSONSerializer().serialize(models.FunctionXGraph.objects.filter(graph=self.graph)),
                function_templates=models.Function.objects.exclude(component__isnull=True),
            )

            context['nav']['title'] = self.graph.name
            context['nav']['menu'] = True
            context['nav']['help'] = (_('Managing Functions'),'help/base-help.htm')
            context['help'] = 'function-help'

            return render(request, 'views/graph/function-manager.htm', context)
        else:
            return redirect('graph_settings', graphid=graphid)

    def post(self, request, graphid):
        data = JSONDeserializer().deserialize(request.body)
        self.graph = Graph.objects.get(graphid=graphid)
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

                # run post function save hook
                func = functionXgraph.function.get_class_module()()
                try:
                    func.after_function_save(functionXgraph, request)
                except NotImplementedError:
                    pass

        return JSONResponse(data)


    def delete(self, request, graphid):
        data = JSONDeserializer().deserialize(request.body)
        self.graph = Graph.objects.get(graphid=graphid)
        with transaction.atomic():
            for item in data:
                functionXgraph = models.FunctionXGraph.objects.get(pk=item['id'])
                functionXgraph.delete()

        return JSONResponse(data)


@method_decorator(group_required('Graph Editor'), name='dispatch')
class PermissionManagerView(GraphBaseView):
    action = ''

    def get(self, request, graphid):
        self.graph = Graph.objects.get(graphid=graphid)

        if self.graph.isresource:
            identities = []
            for group in Group.objects.all():
                identities.append({'name': group.name, 'type': 'group', 'id': group.pk, 'default_permissions': group.permissions.all()})
            for user in User.objects.filter(is_superuser=False):
                groups = []
                default_perms = []
                for group in user.groups.all():
                    groups.append(group.name)
                    default_perms = default_perms + list(group.permissions.all())
                identities.append({'name': user.email or user.username, 'groups': ', '.join(groups), 'type': 'user', 'id': user.pk, 'default_permissions': set(default_perms)})

            cards = Card.objects.filter(nodegroup__parentnodegroup=None, graph=self.graph)

            root = {'children': []}
            def extract_card_info(cards, root):
                for card in cards:
                    d = {
                        'name': card.name,
                        'nodegroup': card.nodegroup_id,
                        'children': [],
                        'type': 'card_container' if len(card.cards) > 0 else 'card',
                        'type_label': _('Card Container') if len(card.cards) > 0 else _('Card')
                    }
                    if len(card.cards) > 0:
                        extract_card_info(card.cards, d)
                    else:
                        for node in card.nodegroup.node_set.all():
                            if node.datatype != 'semantic':
                                d['children'].append({'name': node.name, 'datatype': node.datatype, 'children': [], 'type_label': _('Node'), 'type': 'node'})
                    root['children'].append(d)

            extract_card_info(cards, root)
            #return JSONResponse(root)

            content_type = ContentType.objects.get_for_model(models.NodeGroup)
            nodegroupPermissions = Permission.objects.filter(content_type=content_type)

            context = self.get_context_data(
                main_script='views/graph/permission-manager',
                identities=JSONSerializer().serialize(identities),
                cards=JSONSerializer().serialize(root),
                datatypes=JSONSerializer().serialize(models.DDataType.objects.all()),
                nodegroupPermissions=JSONSerializer().serialize(nodegroupPermissions) #JSONSerializer().serialize([{'codename': permission.codename, 'name': permission.name} for permission in get_perms_for_model(card.nodegroup)])
            )

            context['nav']['title'] = self.graph.name
            context['nav']['menu'] = True
            context['nav']['help'] = (_('Managing Permissions'),'help/base-help.htm')
            context['help'] = 'permissions-manager-help'

            return render(request, 'views/graph/permission-manager.htm', context)
        else:
            return redirect('graph_settings', graphid=graphid)


@method_decorator(group_required('Graph Editor'), name='dispatch')
class PermissionDataView(View):
    perm_cache = {}

    def get_perm_name(self, codename):
        if codename not in self.perm_cache:
            try:
                self.perm_cache[codename] = Permission.objects.get(codename=codename, content_type__app_label='models', content_type__model='nodegroup')
                return self.perm_cache[codename]
            except:
                return None
                # codename for nodegroup probably doesn't exist
        return self.perm_cache[codename]

    def get(self, request):
        nodegroup_ids = JSONDeserializer().deserialize(request.GET.get('nodegroupIds'))
        identityId = request.GET.get('identityId')
        identityType = request.GET.get('identityType')

        ret = []
        if identityType == 'group':
            identity = Group.objects.get(pk=identityId)
            for nodegroup_id in nodegroup_ids:
                nodegroup = models.NodeGroup.objects.get(pk=nodegroup_id)
                perms = [{'codename': codename, 'name': self.get_perm_name(codename).name} for codename in get_group_perms(identity, nodegroup)]
                ret.append({'perms': perms, 'nodegroup_id': nodegroup_id})
        else:
            identity = User.objects.get(pk=identityId)
            for nodegroup_id in nodegroup_ids:
                nodegroup = models.NodeGroup.objects.get(pk=nodegroup_id)
                perms = [{'codename': codename, 'name': self.get_perm_name(codename).name} for codename in get_user_perms(identity, nodegroup)]

                # only get the group perms ("defaults") if no user defined object settings have been saved
                if len(perms) == 0:
                    perms = [{'codename': codename, 'name': self.get_perm_name(codename).name} for codename in set(get_group_perms(identity, nodegroup))]
                ret.append({'perms': perms, 'nodegroup_id': nodegroup_id})

        return JSONResponse(ret)

    def post(self, request):
        data = JSONDeserializer().deserialize(request.body)
        self.apply_permissions(data)
        return JSONResponse(data)

    def delete(self, request):
        data = JSONDeserializer().deserialize(request.body)
        self.apply_permissions(data, revert=True)
        return JSONResponse(data)

    def apply_permissions(self, data, revert=False):
        with transaction.atomic():
            for identity in data['selectedIdentities']:
                if identity['type'] == 'group':
                    identityModel = Group.objects.get(pk=identity['id'])
                else:
                    identityModel = User.objects.get(pk=identity['id'])

                for card in data['selectedCards']:
                    nodegroup = models.NodeGroup.objects.get(pk=card['nodegroup'])

                    # first remove all the current permissions
                    for perm in get_perms(identityModel, nodegroup):
                        remove_perm(perm, identityModel, nodegroup)

                    if not revert:
                        # then add the new permissions
                        for perm in data['selectedPermissions']:
                            assign_perm(perm['codename'], identityModel, nodegroup)
