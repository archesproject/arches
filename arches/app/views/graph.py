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
import json
from django.conf import settings as app_settings
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
from arches.app.models.graph import Graph
from arches.app.models.card import Card
from arches.app.models import models
from arches.app.utils.data_management.resource_graphs.exporter import get_graphs_for_export
from arches.app.views.base import BaseNiftyView
from tempfile import NamedTemporaryFile
from guardian.shortcuts import get_perms_for_model


class GraphBaseView(BaseNiftyView):
    def get_context_data(self, **kwargs):
        context = super(GraphBaseView, self).get_context_data(**kwargs)
        try:
            context['graphid'] = self.graph.graphid
            context['graph'] = JSONSerializer().serializeToPython(self.graph)
            context['graph_json'] = JSONSerializer().serialize(self.graph)
        except:
            pass
        return context


@method_decorator(group_required('edit'), name='dispatch')
class GraphSettingsView(GraphBaseView):
    def get(self, request, graphid):
        self.graph = Graph.objects.get(graphid=graphid)
        icons = models.Icon.objects.order_by('name')
        resource_graphs = models.GraphModel.objects.filter(Q(isresource=True), ~Q(graphid=graphid))
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
            node_count=models.Node.objects.filter(graph=self.graph).count()
        )
        return render(request, 'views/graph/graph-settings.htm', context)

    def post(self, request, graphid):
        graph = Graph.objects.get(graphid=graphid)
        data = JSONDeserializer().deserialize(request.body)
        for key, value in data.get('graph').iteritems():
            if key in ['iconclass', 'name', 'author', 'description', 'isresource',
                'ontology_id', 'version',  'subtitle', 'isactive']:
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




@method_decorator(group_required('edit'), name='dispatch')
class GraphManagerView(GraphBaseView):
    def get(self, request, graphid):
        if graphid is None or graphid == '':
            context = self.get_context_data(
                main_script='views/graph',
            )
            return render(request, 'views/graph.htm', context)

        self.graph = Graph.objects.get(graphid=graphid)
        datatypes = models.DDataType.objects.all()
        branch_graphs = Graph.objects.exclude(pk=graphid).exclude(isresource=True).exclude(isactive=False)
        if self.graph.ontology is not None:
            branch_graphs = branch_graphs.filter(ontology=self.graph.ontology)

        context = self.get_context_data(
            main_script='views/graph/graph-manager',
            functions=JSONSerializer().serialize(models.Function.objects.all()),
            branches=JSONSerializer().serialize(branch_graphs),
            datatypes_json=JSONSerializer().serialize(datatypes),
            datatypes=datatypes,
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
            }
        )

        return render(request, 'views/graph/graph-manager.htm', context)

    def delete(self, request, graphid):
        graph = Graph.objects.get(graphid=graphid)
        graph.delete()
        return JSONResponse({'succces':True})


@method_decorator(group_required('edit'), name='dispatch')
class GraphDataView(View):

    action = 'update_node'

    def get(self, request, graphid, nodeid=None):
        if self.action == 'export_graph':
            graph = get_graphs_for_export([graphid])
            f = JSONSerializer().serialize(graph)
            graph_name = JSONDeserializer().deserialize(f)['graph'][0]['name']

            response = HttpResponse(f, content_type='json/plain')
            response['Content-Disposition'] = 'attachment; filename="%s export.json"' %(graph_name)
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
        if self.action == 'import_graph':
            graph_file = request.FILES.get('importedGraph').read()
            graphs = JSONDeserializer().deserialize(graph_file)['graph']
            for graph in graphs:
                new_graph = Graph(graph)
                new_graph.save()
                ret = new_graph
        else:
            if graphid is not None:
                graph = Graph.objects.get(graphid=graphid)
            data = JSONDeserializer().deserialize(request.body)

            if self.action == 'new_graph':
                isresource = data['isresource'] if 'isresource' in data else False
                name = _('New Resource') if isresource else _('New Graph')
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
                ret = graph.copy()
                ret.save()

        return JSONResponse(ret)

    def delete(self, request, graphid):
        data = JSONDeserializer().deserialize(request.body)
        if data and self.action == 'delete_node':
            graph = Graph.objects.get(graphid=graphid)
            graph.delete_node(node=data.get('nodeid', None))
            return JSONResponse({})

        return HttpResponseNotFound()


@method_decorator(group_required('edit'), name='dispatch')
class CardManagerView(GraphBaseView):
    def get(self, request, graphid):
        self.graph = Graph.objects.get(graphid=graphid)
        branch_graphs = Graph.objects.exclude(pk=graphid).exclude(isresource=True).exclude(isactive=False)
        if self.graph.ontology is not None:
            branch_graphs = branch_graphs.filter(ontology=self.graph.ontology)

        context = self.get_context_data(
            main_script='views/graph/card-manager',
            branches=JSONSerializer().serialize(branch_graphs)
        )

        return render(request, 'views/graph/card-manager.htm', context)


@method_decorator(group_required('edit'), name='dispatch')
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

        context = self.get_context_data(
            main_script='views/graph/card-configuration-manager',
            card=JSONSerializer().serialize(card),
            permissions=JSONSerializer().serialize([{'codename': permission.codename, 'name': permission.name} for permission in get_perms_for_model(card.nodegroup)]),
            datatypes_json=JSONSerializer().serialize(datatypes),
            datatypes=datatypes,
            widgets=widgets,
            widgets_json=JSONSerializer().serialize(widgets),
            functions=JSONSerializer().serialize(models.Function.objects.all()),
        )

        return render(request, 'views/graph/card-configuration-manager.htm', context)

    def post(self, request, cardid):
        data = JSONDeserializer().deserialize(request.body)
        if data:
            card = Card(data)
            card.save()
            return JSONResponse(card)

        return HttpResponseNotFound()


@method_decorator(group_required('edit'), name='dispatch')
class FormManagerView(GraphBaseView):
    def get(self, request, graphid):
        self.graph = Graph.objects.get(graphid=graphid)

        context = self.get_context_data(
            main_script='views/graph/form-manager',
            forms=JSONSerializer().serialize(self.graph.form_set.all()),
			cards=JSONSerializer().serialize(models.CardModel.objects.filter(graph=self.graph)),
            forms_x_cards=JSONSerializer().serialize(models.FormXCard.objects.filter(form__in=self.graph.form_set.all()).order_by('sortorder')),
        )

        return render(request, 'views/graph/form-manager.htm', context)

    def post(self, request, graphid):
        graph = models.GraphModel.objects.get(graphid=graphid)
        form = models.Form(title=_('New Form'), graph=graph)
        form.save()
        return JSONResponse(form)

@method_decorator(group_required('edit'), name='dispatch')
class FormView(GraphBaseView):
    def get(self, request, formid):
        form = models.Form.objects.get(formid=formid)
        self.graph = Graph.objects.get(graphid=form.graph.pk)
        icons = models.Icon.objects.order_by('name')
        cards = models.CardModel.objects.filter(nodegroup__parentnodegroup=None, graph=self.graph)

        context = self.get_context_data(
            main_script='views/graph/form-configuration',
            icons=JSONSerializer().serialize(icons),
            form=JSONSerializer().serialize(form),
            forms=JSONSerializer().serialize(self.graph.form_set.all()),
            cards=JSONSerializer().serialize(cards),
            forms_x_cards=JSONSerializer().serialize(models.FormXCard.objects.filter(form=form).order_by('sortorder')),
        )

        return render(request, 'views/graph/form-configuration.htm', context)

    def post(self, request, formid):
        data = JSONDeserializer().deserialize(request.body)
        form = models.Form.objects.get(formid=formid)
        form.title = data['title']
        form.subtitle = data['subtitle']
        form.iconclass = data['iconclass']
        form.status = data['status']
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

class DatatypeTemplateView(TemplateView):
    def get(sefl, request, template='text'):
        return render(request, 'views/graph/datatypes/%s.htm' % template)
