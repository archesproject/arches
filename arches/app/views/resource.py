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

import uuid
import json
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic import View
from django.forms.models import model_to_dict
from django.template.loader import render_to_string
from arches.app.models import models
from arches.app.models.card import Card
from arches.app.models.graph import Graph
from arches.app.models.tile import Tile
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from arches.app.utils.pagination import get_paginator
from arches.app.utils.decorators import can_edit_resource_instance
from arches.app.utils.decorators import can_read_resource_instance
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.response import JSONResponse
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Query, Terms
from arches.app.views.base import BaseManagerView, MapBaseManagerView
from arches.app.views.concept import Concept
from arches.app.datatypes.datatypes import DataTypeFactory
from elasticsearch import Elasticsearch


@method_decorator(can_edit_resource_instance(), name='dispatch')
class ResourceListView(BaseManagerView):

    def get(self, request, graphid=None, resourceid=None):
        context = self.get_context_data(
            main_script='views/resource',
        )

        context['nav']['icon'] = "fa fa-bookmark"
        context['nav']['title'] = _("Resource Manager")
        context['nav']['login'] = True
        context['nav']['help'] = {
            'title': _('Creating Resources'),
            'template': 'resource-editor-landing-help',
        }

        return render(request, 'views/resource.htm', context)


def get_resource_relationship_types():
    resource_relationship_types = Concept().get_child_collections('00000000-0000-0000-0000-000000000005')
    default_relationshiptype_valueid = None
    for relationship_type in resource_relationship_types:
        if relationship_type[0] == '00000000-0000-0000-0000-000000000007':
            default_relationshiptype_valueid = relationship_type[2]
    relationship_type_values = {'values': [{'id': str(c[2]), 'text':str(
        c[1])} for c in resource_relationship_types], 'default': str(default_relationshiptype_valueid)}
    return relationship_type_values


@method_decorator(can_edit_resource_instance(), name='dispatch')
class NewResourceEditorView(MapBaseManagerView):
    action = None

    def get(self, request, graphid=None, resourceid=None, view_template='views/resource/new-editor.htm', main_script='views/resource/new-editor', nav_menu=True):
        if self.action == 'copy':
            return self.copy(request, resourceid)

        if resourceid is None:
            resource_instance = None
            graph = models.GraphModel.objects.get(pk=graphid)
            resourceid = ''
        else:
            resource_instance = Resource.objects.get(pk=resourceid)
            graph = resource_instance.graph
        nodes = graph.node_set.all()
        resource_graphs = models.GraphModel.objects.exclude(
            pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID).exclude(isresource=False).exclude(isactive=False)
        ontologyclass = [node for node in nodes if node.istopnode is True][0].ontologyclass
        relationship_type_values = get_resource_relationship_types()

        nodegroups = []
        editable_nodegroups = []
        for node in nodes:
            if node.is_collector:
                added = False
                if request.user.has_perm('write_nodegroup', node.nodegroup):
                    editable_nodegroups.append(node.nodegroup)
                    nodegroups.append(node.nodegroup)
                    added = True
                if not added and request.user.has_perm('read_nodegroup', node.nodegroup):
                    nodegroups.append(node.nodegroup)

        nodes = nodes.filter(nodegroup__in=nodegroups)
        cards = graph.cardmodel_set.order_by('sortorder').filter(
            nodegroup__in=nodegroups).prefetch_related('cardxnodexwidget_set')
        cardwidgets = [widget for widgets in [card.cardxnodexwidget_set.order_by(
            'sortorder').all() for card in cards] for widget in widgets]
        widgets = models.Widget.objects.all()
        card_components = models.CardComponent.objects.all()
        datatypes = models.DDataType.objects.all()
        user_is_reviewer = request.user.groups.filter(name='Resource Reviewer').exists()
        is_system_settings = False

        if resource_instance is None:
            tiles = []
            displayname = _('New Resource')
        else:
            displayname = resource_instance.displayname
            if displayname == 'undefined':
                displayname = _('Unnamed Resource')
            if str(resource_instance.graph_id) == settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID:
                is_system_settings = True
                displayname = _("System Settings")

            tiles = resource_instance.tilemodel_set.order_by('sortorder').filter(nodegroup__in=nodegroups)

            provisionaltiles = []
            for tile in tiles:
                append_tile = True
                isfullyprovisional = False
                if tile.provisionaledits is not None:
                    if len(tile.data) == 0:
                        isfullyprovisional = True
                    if user_is_reviewer == False:
                        if str(request.user.id) in tile.provisionaledits:
                            tile.provisionaledits = {str(request.user.id): tile.provisionaledits[str(request.user.id)]}
                            tile.data = tile.provisionaledits[str(request.user.id)]['value']
                        else:
                            if isfullyprovisional == True:
                                # if the tile IS fully provisional and the current user is not the owner,
                                # we don't send that tile back to the client.
                                append_tile = False
                            else:
                                # if the tile has authoritaive data and the current user is not the owner,
                                # we don't send the provisional data of other users back to the client.
                                tile.provisionaledits = None
                if append_tile == True:
                    provisionaltiles.append(tile)
            tiles = provisionaltiles

        map_layers = models.MapLayer.objects.all()
        map_markers = models.MapMarker.objects.all()
        map_sources = models.MapSource.objects.all()
        geocoding_providers = models.Geocoder.objects.all()
        templates = models.ReportTemplate.objects.all()

        cards = JSONSerializer().serializeToPython(cards)
        editable_nodegroup_ids = [str(nodegroup.pk) for nodegroup in editable_nodegroups]
        for card in cards:
            card['is_writable'] = False
            if str(card['nodegroup_id']) in editable_nodegroup_ids:
                card['is_writable'] = True

        context = self.get_context_data(
            main_script=main_script,
            resourceid=resourceid,
            displayname=displayname,
            graphid=graph.graphid,
            graphiconclass=graph.iconclass,
            graphname=graph.name,
            ontologyclass=ontologyclass,
            resource_graphs=resource_graphs,
            relationship_types=relationship_type_values,
            widgets=widgets,
            widgets_json=JSONSerializer().serialize(widgets),
            card_components=card_components,
            card_components_json=JSONSerializer().serialize(card_components),
            tiles=JSONSerializer().serialize(tiles),
            cards=JSONSerializer().serialize(cards),
            nodegroups=JSONSerializer().serialize(nodegroups),
            nodes=JSONSerializer().serialize(nodes),
            cardwidgets=JSONSerializer().serialize(cardwidgets),
            datatypes_json=JSONSerializer().serialize(datatypes, exclude=['iconclass', 'modulename', 'classname']),
            map_layers=map_layers,
            map_markers=map_markers,
            map_sources=map_sources,
            geocoding_providers=geocoding_providers,
            user_is_reviewer=json.dumps(user_is_reviewer),
            report_templates=templates,
            templates_json=JSONSerializer().serialize(templates, sort_keys=False, exclude=['name', 'description']),
            graph_json=JSONSerializer().serialize(graph),
            is_system_settings=is_system_settings
        )

        context['nav']['title'] = ''
        context['nav']['menu'] = nav_menu
        if resourceid == settings.RESOURCE_INSTANCE_ID:
            context['nav']['help'] = {
                'title': _('Managing System Settings'),
                'template': 'system-settings-help',
            }
        else:
            context['nav']['help'] = {
                'title': _('Using the Resource Editor'),
                'template': 'resource-editor-help',
            }

        return render(request, view_template, context)

    def delete(self, request, resourceid=None):
        if resourceid is not None:
            ret = Resource.objects.get(pk=resourceid)
            ret.delete(user=request.user)
            return JSONResponse(ret)
        return HttpResponseNotFound()

    def copy(self, request, resourceid=None):
        resource_instance = Resource.objects.get(pk=resourceid)
        return JSONResponse(resource_instance.copy())


@method_decorator(can_edit_resource_instance(), name='dispatch')
class ResourceEditorView(MapBaseManagerView):
    action = None

    def get(self, request, graphid=None, resourceid=None, view_template='views/resource/editor.htm', main_script='views/resource/editor', nav_menu=True):
        if self.action == 'copy':
            return self.copy(request, resourceid)

        resource_instance_exists = False

        try:
            resource_instance = Resource.objects.get(pk=resourceid)
            resource_instance_exists = True
            graphid = resource_instance.graph_id

        except ObjectDoesNotExist:
            resource_instance = Resource()
            resource_instance.resourceinstanceid = resourceid
            resource_instance.graph_id = graphid

        if resourceid is not None:

            if request.is_ajax() and request.GET.get('search') == 'true':
                html = render_to_string('views/search/search-base-manager.htm', {}, request)
                return HttpResponse(html)

            resource_graphs = models.GraphModel.objects.exclude(
                pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID).exclude(isresource=False).exclude(isactive=False)
            graph = Graph.objects.get(graphid=graphid)
            relationship_type_values = get_resource_relationship_types()
            datatypes = models.DDataType.objects.all()
            widgets = models.Widget.objects.all()
            map_layers = models.MapLayer.objects.all()
            map_markers = models.MapMarker.objects.all()
            map_sources = models.MapSource.objects.all()
            geocoding_providers = models.Geocoder.objects.all()
            required_widgets = []

            widget_datatypes = [v.datatype for k, v in graph.nodes.iteritems()]
            widgets = widgets.filter(datatype__in=widget_datatypes)

            if resource_instance_exists == True:
                displayname = Resource.objects.get(pk=resourceid).displayname
                if displayname == 'undefined':
                    displayname = 'Unnamed Resource'
            else:
                displayname = 'Unnamed Resource'

            date_nodes = models.Node.objects.filter(datatype='date', graph__isresource=True, graph__isactive=True)
            searchable_datatypes = [d.pk for d in models.DDataType.objects.filter(issearchable=True)]
            searchable_nodes = models.Node.objects.filter(
                graph__isresource=True, graph__isactive=True, datatype__in=searchable_datatypes, issearchable=True)
            resource_cards = models.CardModel.objects.filter(graph__isresource=True, graph__isactive=True)
            context = self.get_context_data(
                main_script=main_script,
                resource_type=graph.name,
                relationship_types=relationship_type_values,
                iconclass=graph.iconclass,
                datatypes_json=JSONSerializer().serialize(datatypes, exclude=['iconclass', 'modulename', 'classname']),
                datatypes=datatypes,
                widgets=widgets,
                date_nodes=date_nodes,
                map_layers=map_layers,
                map_markers=map_markers,
                map_sources=map_sources,
                geocoding_providers=geocoding_providers,
                widgets_json=JSONSerializer().serialize(widgets),
                resourceid=resourceid,
                resource_graphs=resource_graphs,
                graph_json=JSONSerializer().serialize(graph, exclude=['iconclass', 'functions', 'functions_x_graphs', 'name', 'description',
                                                                      'deploymentfile', 'author', 'deploymentdate', 'version', 'isresource', 'isactive', 'iconclass', 'ontology']),
                displayname=displayname,
                resource_cards=JSONSerializer().serialize(resource_cards, exclude=[
                    'description', 'instructions', 'active', 'isvisible']),
                searchable_nodes=JSONSerializer().serialize(searchable_nodes, exclude=[
                    'description', 'ontologyclass', 'isrequired', 'issearchable', 'istopnode']),
                saved_searches=JSONSerializer().serialize(settings.SAVED_SEARCHES),
                resource_instance_exists=resource_instance_exists,
                user_is_reviewer=json.dumps(request.user.groups.filter(name='Resource Reviewer').exists()),
                userid=request.user.id
            )

            if graph.iconclass:
                context['nav']['icon'] = graph.iconclass
            context['nav']['title'] = graph.name
            context['nav']['menu'] = nav_menu
            if resourceid == settings.RESOURCE_INSTANCE_ID:
                context['nav']['help'] = (_('Managing System Settings'), 'help/base-help.htm')
                context['help'] = 'system-settings-help'
            else:
                context['nav']['help'] = (_('Using the Resource Editor'), 'help/base-help.htm')
                context['help'] = 'resource-editor-help'

            return render(request, view_template, context)

        return HttpResponseNotFound()

    def delete(self, request, resourceid=None):

        if resourceid is not None:
            ret = Resource.objects.get(pk=resourceid)
            ret.delete(user=request.user)
            return JSONResponse(ret)
        return HttpResponseNotFound()

    def copy(self, request, resourceid=None):
        resource_instance = Resource.objects.get(pk=resourceid)
        return JSONResponse(resource_instance.copy())


@method_decorator(can_edit_resource_instance(), name='dispatch')
class ResourceEditLogView(BaseManagerView):

    def getEditConceptValue(self, values):
        if values != None:
            for k, v in values.iteritems():
                try:
                    uuid.UUID(v)
                    v = models.Value.objects.get(pk=v).value
                    values[k] = v
                except Exception as e:
                    pass
                try:
                    display_values = []
                    for val in v:
                        uuid.UUID(val)
                        display_value = models.Value.objects.get(pk=val).value
                        display_values.append(display_value)
                    values[k] = display_values
                except Exception as e:
                    pass

    def get(self, request, resourceid=None, view_template='views/resource/edit-log.htm'):
        if resourceid is None:
            recent_edits = models.EditLog.objects.all().exclude(
                resourceclassid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID).order_by('-timestamp')[:100]
            edited_ids = list(set([edit.resourceinstanceid for edit in recent_edits]))
            resources = Resource.objects.filter(resourceinstanceid__in=edited_ids)
            edit_type_lookup = {
                'create': _('Resource Created'),
                'delete': _('Resource Deleted'),
                'tile delete': _('Tile Deleted'),
                'tile create': _('Tile Created'),
                'tile edit': _('Tile Updated'),
                'delete edit': _('Edit Deleted')
            }
            deleted_instances = [e.resourceinstanceid for e in recent_edits if e.edittype == 'delete']
            graph_name_lookup = {str(r.resourceinstanceid): r.graph.name for r in resources}
            for edit in recent_edits:
                edit.friendly_edittype = edit_type_lookup[edit.edittype]
                edit.resource_model_name = None
                edit.deleted = edit.resourceinstanceid in deleted_instances
                if edit.resourceinstanceid in graph_name_lookup:
                    edit.resource_model_name = graph_name_lookup[edit.resourceinstanceid]
                edit.displayname = edit.note
                if edit.resource_model_name is None:
                    try:
                        edit.resource_model_name = models.GraphModel.objects.get(pk=edit.resourceclassid).name
                    except:
                        pass

            context = self.get_context_data(
                main_script='views/edit-history',
                recent_edits=recent_edits
            )

            context['nav']['title'] = _('Recent Edits')

            return render(request, 'views/edit-history.htm', context)
        else:
            resource_instance = models.ResourceInstance.objects.get(pk=resourceid)
            edits = models.EditLog.objects.filter(resourceinstanceid=resourceid)
            permitted_edits = []
            for edit in edits:
                if edit.nodegroupid != None:
                    nodegroup = models.NodeGroup.objects.get(pk=edit.nodegroupid)
                    if request.user.has_perm('read_nodegroup', edit.nodegroupid):
                        if edit.newvalue != None:
                            self.getEditConceptValue(edit.newvalue)
                        if edit.oldvalue != None:
                            self.getEditConceptValue(edit.oldvalue)
                        permitted_edits.append(edit)
                else:
                    permitted_edits.append(edit)

            resource = Resource.objects.get(pk=resourceid)
            displayname = resource.displayname
            displaydescription = resource.displaydescription
            cards = Card.objects.filter(nodegroup__parentnodegroup=None, graph=resource_instance.graph)
            graph_name = resource_instance.graph.name
            if displayname == 'undefined':
                displayname = _('Unnamed Resource')

            context = self.get_context_data(
                main_script='views/resource/edit-log',
                cards=JSONSerializer().serialize(cards),
                resource_type=graph_name,
                resource_description=displaydescription,
                iconclass=resource_instance.graph.iconclass,
                edits=JSONSerializer().serialize(permitted_edits),
                resourceid=resourceid,
                displayname=displayname,
            )

            context['nav']['res_edit'] = True
            context['nav']['icon'] = resource_instance.graph.iconclass
            context['nav']['title'] = graph_name

            return render(request, view_template, context)

        return HttpResponseNotFound()


@method_decorator(can_edit_resource_instance(), name='dispatch')
class ResourceData(View):

    def get(self, request, resourceid=None, formid=None):
        if formid is not None:
            form = Form(resourceid=resourceid, formid=formid, user=request.user)
            return JSONResponse(form)

        return HttpResponseNotFound()

@method_decorator(can_read_resource_instance(), name='dispatch')
class ResourceTiles(View):

    def get(self, request, resourceid=None, include_display_values=True):
        datatype_factory = DataTypeFactory()
        nodeid = request.GET.get('nodeid', None)
        permitted_tiles = []
        perm = 'read_nodegroup'
        tiles = models.TileModel.objects.filter(resourceinstance_id=resourceid)
        if nodeid is not None:
            node = models.Node.objects.get(pk=nodeid)
            tiles = tiles.filter(nodegroup=node.nodegroup)

        for tile in tiles:
            if request.user.has_perm(perm, tile.nodegroup):
                tile = Tile.objects.get(pk=tile.tileid)
                tile.filter_by_perm(request.user, perm)
                tile_dict = model_to_dict(tile)
                if include_display_values:
                    tile_dict['display_values'] = []
                    for node in models.Node.objects.filter(nodegroup=tile.nodegroup):
                        if str(node.nodeid) in tile.data:
                            datatype = datatype_factory.get_instance(node.datatype)
                            tile_dict['display_values'].append({
                                'value': datatype.get_display_value(tile, node),
                                'label': node.name,
                                'nodeid': node.nodeid
                            })
                permitted_tiles.append(tile_dict)

        return JSONResponse({'tiles': permitted_tiles})


@method_decorator(can_read_resource_instance(), name='dispatch')
class ResourceCards(View):

    def get(self, request, resourceid=None):
        cards = []
        if resourceid != None:
            graph = models.GraphModel.objects.get(graphid=resourceid)
            cards = [Card.objects.get(pk=card.cardid) for card in models.CardModel.objects.filter(graph=graph)]
        return JSONResponse({'success': True, 'cards': cards})


class ResourceDescriptors(View):

    def get(self, request, resourceid=None):
        if resourceid is not None:
            se = SearchEngineFactory().create()
            document = se.search(index='resource', doc_type='_all', id=resourceid)
            resource = Resource.objects.get(pk=resourceid)
            return JSONResponse({
                'graphid': document['_source']['graph_id'],
                'graph_name': resource.graph.name,
                'displaydescription': document['_source']['displaydescription'],
                'map_popup': document['_source']['map_popup'],
                'displayname': document['_source']['displayname'],
                'geometries': document['_source']['geometries'],
            })

        return HttpResponseNotFound()


class ResourceReportView(MapBaseManagerView):

    def get(self, request, resourceid=None):
        lang = request.GET.get('lang', settings.LANGUAGE_CODE)
        resource = Resource.objects.get(pk=resourceid)
        displayname = resource.displayname
        resource_models = models.GraphModel.objects.filter(isresource=True).exclude(
            isactive=False).exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
        related_resource_summary = [
            {'graphid': str(g.graphid), 'name': g.name, 'resources': []} for g in resource_models]
        related_resources_search_results = resource.get_related_resources(lang=lang, start=0, limit=1000)
        related_resources = related_resources_search_results['related_resources']
        relationships = related_resources_search_results['resource_relationships']
        resource_relationship_type_values = {i['id']: i['text'] for i in get_resource_relationship_types()['values']}

        for rr in related_resources:
            for summary in related_resource_summary:
                if rr['graph_id'] == summary['graphid']:
                    relationship_summary = []
                    for relationship in relationships:
                        if rr['resourceinstanceid'] in (relationship['resourceinstanceidto'], relationship['resourceinstanceidfrom']):
                            rr_type = resource_relationship_type_values[relationship['relationshiptype']] if relationship[
                                'relationshiptype'] in resource_relationship_type_values else relationship['relationshiptype']
                            relationship_summary.append(rr_type)
                    summary['resources'].append({'instance_id': rr['resourceinstanceid'], 'displayname': rr[
                                                'displayname'], 'relationships': relationship_summary})

        tiles = Tile.objects.filter(resourceinstance=resource).order_by('sortorder')

        graph = Graph.objects.get(graphid=resource.graph_id)
        cards = Card.objects.filter(graph=graph).order_by('sortorder')
        permitted_cards = []
        permitted_tiles = []

        perm = 'read_nodegroup'

        for card in cards:
            if request.user.has_perm(perm, card.nodegroup):
                card.filter_by_perm(request.user, perm)
                permitted_cards.append(card)

        for tile in tiles:
            if request.user.has_perm(perm, tile.nodegroup):
                tile.filter_by_perm(request.user, perm)
                permitted_tiles.append(tile)


        try:
            map_layers = models.MapLayer.objects.all()
            map_markers = models.MapMarker.objects.all()
            map_sources = models.MapSource.objects.all()
            geocoding_providers = models.Geocoder.objects.all()
        except AttributeError:
            raise Http404(_("No active report template is available for this resource."))

        cardwidgets = [widget for widgets in [card.cardxnodexwidget_set.order_by(
            'sortorder').all() for card in permitted_cards] for widget in widgets]

        datatypes = models.DDataType.objects.all()
        widgets = models.Widget.objects.all()
        templates = models.ReportTemplate.objects.all()
        card_components = models.CardComponent.objects.all()

        context = self.get_context_data(
            main_script='views/resource/report',
            report_templates=templates,
            templates_json=JSONSerializer().serialize(templates, sort_keys=False, exclude=['name', 'description']),
            card_components=card_components,
            card_components_json=JSONSerializer().serialize(card_components),
            cardwidgets=JSONSerializer().serialize(cardwidgets),
            tiles=JSONSerializer().serialize(permitted_tiles, sort_keys=False),
            cards=JSONSerializer().serialize(permitted_cards, sort_keys=False, exclude=[
                'is_editable', 'description', 'instructions', 'helpenabled', 'helptext', 'helptitle', 'ontologyproperty']),
            datatypes_json=JSONSerializer().serialize(
                datatypes, exclude=['modulename', 'issearchable', 'configcomponent', 'configname', 'iconclass']),
            geocoding_providers=geocoding_providers,
            related_resources=JSONSerializer().serialize(related_resource_summary, sort_keys=False),
            widgets=widgets,
            map_layers=map_layers,
            map_markers=map_markers,
            map_sources=map_sources,
            graph_id=graph.graphid,
            graph_name=graph.name,
            graph_json=JSONSerializer().serialize(graph, sort_keys=False, exclude=[
                'functions', 'relatable_resource_model_ids', 'domain_connections', 'edges', 'is_editable', 'description', 'iconclass', 'subtitle', 'author']),
            resourceid=resourceid,
            displayname=displayname,
        )

        if graph.iconclass:
            context['nav']['icon'] = graph.iconclass
        context['nav']['title'] = graph.name
        context['nav']['res_edit'] = True
        context['nav']['print'] = True
        context['nav']['print'] = True

        return render(request, 'views/resource/report.htm', context)


@method_decorator(can_read_resource_instance(), name='dispatch')
class RelatedResourcesView(BaseManagerView):
    action = None

    def paginate_related_resources(self, related_resources, page, request):
        total = related_resources['total']
        paginator, pages = get_paginator(request, related_resources, total, page, settings.RELATED_RESOURCES_PER_PAGE)
        page = paginator.page(page)

        def parse_relationshiptype_label(relationship):
            if relationship['relationshiptype_label'].startswith('http'):
                relationship['relationshiptype_label'] = relationship['relationshiptype_label'].rsplit('/')[-1]
            return relationship

        related_resources['resource_relationships'] = [parse_relationshiptype_label(r) for r in related_resources[
            'resource_relationships']]

        ret = {}
        ret['related_resources'] = related_resources
        ret['paginator'] = {}
        ret['paginator']['current_page'] = page.number
        ret['paginator']['has_next'] = page.has_next()
        ret['paginator']['has_previous'] = page.has_previous()
        ret['paginator']['has_other_pages'] = page.has_other_pages()
        ret['paginator']['next_page_number'] = page.next_page_number() if page.has_next() else None
        ret['paginator']['previous_page_number'] = page.previous_page_number() if page.has_previous() else None
        ret['paginator']['start_index'] = page.start_index()
        ret['paginator']['end_index'] = page.end_index()
        ret['paginator']['pages'] = pages

        return ret

    def get(self, request, resourceid=None):
        if self.action == 'get_candidates':
            resourceids = json.loads(request.GET.get('resourceids', '[]'))
            resources = Resource.objects.filter(resourceinstanceid__in=resourceids)
            ret = []
            for rr in resources:
                res = JSONSerializer().serializeToPython(rr)
                res['ontologyclass'] = rr.get_root_ontology()
                ret.append(res)
            return JSONResponse(ret)

        if self.action == 'get_relatable_resources':
            graphid = request.GET.get('graphid', None)
            nodes = models.Node.objects.filter(graph=graphid).exclude(istopnode=False)[0].get_relatable_resources()
            ret = set([str(node.graph_id) for node in nodes])
            return JSONResponse(ret)

        lang = request.GET.get('lang', settings.LANGUAGE_CODE)
        start = request.GET.get('start', 0)
        ret = []
        try:
            resource = Resource.objects.get(pk=resourceid)
        except ObjectDoesNotExist:
            resource = Resource()
        page = 1 if request.GET.get('page') == '' else int(request.GET.get('page', 1))
        related_resources = resource.get_related_resources(lang=lang, start=start, limit=1000, page=page)

        if related_resources is not None:
            ret = self.paginate_related_resources(related_resources, page, request)

        return JSONResponse(ret)

    def delete(self, request, resourceid=None):
        lang = request.GET.get('lang', settings.LANGUAGE_CODE)
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
        se.es.indices.refresh(index=se._add_prefix("resource_relations"))
        resource = Resource.objects.get(pk=root_resourceinstanceid[0])
        page = 1 if request.GET.get('page') == '' else int(request.GET.get('page', 1))
        related_resources = resource.get_related_resources(lang=lang, start=start, limit=1000, page=page)
        ret = []

        if related_resources is not None:
            ret = self.paginate_related_resources(related_resources, page, request)

        return JSONResponse(ret, indent=4)

    def post(self, request, resourceid=None):
        lang = request.GET.get('lang', settings.LANGUAGE_CODE)
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
            top_node = [node for node in nodes if node.istopnode == True][0]
            relatable_resources = [str(node.graph_id) for node in top_node.get_relatable_resources()]
            return relatable_resources

        def confirm_relationship_permitted(to_id, from_id):
            resource_instance_to = models.ResourceInstance.objects.filter(resourceinstanceid=to_id)[0]
            resource_instance_from = models.ResourceInstance.objects.filter(resourceinstanceid=from_id)[0]
            relatable_to = get_relatable_resources(resource_instance_to.graph_id)
            relatable_from = get_relatable_resources(resource_instance_from.graph_id)
            relatable_to_is_valid = str(resource_instance_to.graph_id) in relatable_from
            relatable_from_is_valid = str(resource_instance_from.graph_id) in relatable_to
            return (relatable_to_is_valid == True and relatable_from_is_valid == True)

        for instanceid in instances_to_relate:
            permitted = confirm_relationship_permitted(instanceid, root_resourceinstanceid[0])
            if permitted == True:
                rr = models.ResourceXResource(
                    resourceinstanceidfrom=Resource(root_resourceinstanceid[0]),
                    resourceinstanceidto=Resource(instanceid),
                    notes=notes,
                    relationshiptype=relationship_type,
                    datestarted=datefrom,
                    dateended=dateto
                )
                rr.save()
            else:
                print 'relationship not permitted'

        for relationshipid in relationships_to_update:
            rr = models.ResourceXResource.objects.get(pk=relationshipid)
            rr.notes = notes
            rr.relationshiptype = relationship_type
            rr.datestarted = datefrom
            rr.dateended = dateto
            rr.save()

        start = request.GET.get('start', 0)
        se.es.indices.refresh(index=se._add_prefix("resource_relations"))
        resource = Resource.objects.get(pk=root_resourceinstanceid[0])
        page = 1 if request.GET.get('page') == '' else int(request.GET.get('page', 1))
        related_resources = resource.get_related_resources(lang=lang, start=start, limit=1000, page=page)
        ret = []

        if related_resources is not None:
            ret = self.paginate_related_resources(related_resources, page, request)

        return JSONResponse(ret, indent=4)
