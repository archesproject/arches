"""
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
"""

import os
import zipfile
import json
import uuid
import logging
from django.db import transaction
from django.shortcuts import redirect, render
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.http import HttpResponseNotFound, HttpResponse
from django.views.generic import View, TemplateView
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from arches.app.utils.decorators import group_required
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.response import JSONResponse, JSONErrorResponse
from arches.app.models import models
from arches.app.models.graph import Graph, GraphValidationError
from arches.app.models.card import Card
from arches.app.models.concept import Concept
from arches.app.models.system_settings import settings
from arches.app.models.resource import ModelInactiveError
from arches.app.utils.data_management.resource_graphs.exporter import get_graphs_for_export, create_mapping_configuration_file
from arches.app.utils.data_management.resource_graphs import importer as GraphImporter
from arches.app.utils.system_metadata import system_metadata
from arches.app.views.base import BaseManagerView
from guardian.shortcuts import assign_perm, get_perms, remove_perm, get_group_perms, get_user_perms
from io import BytesIO
from elasticsearch.exceptions import RequestError
from django.core.cache import cache

logger = logging.getLogger(__name__)


class GraphBaseView(BaseManagerView):
    def get_context_data(self, **kwargs):
        context = super(GraphBaseView, self).get_context_data(**kwargs)
        try:
            context["graphid"] = self.graph.graphid
            context["graph"] = JSONSerializer().serializeToPython(self.graph)
            context["graph_json"] = JSONSerializer().serialize(self.graph)
            context["root_node"] = self.graph.node_set.get(istopnode=True)
        except Exception:
            pass
        return context


@method_decorator(group_required("Graph Editor"), name="dispatch")
class GraphSettingsView(GraphBaseView):
    def get(self, request, graphid):
        self.graph = models.GraphModel.objects.get(graphid=graphid)
        icons = models.Icon.objects.order_by("name")
        resource_graphs = models.GraphModel.objects.filter(Q(isresource=True)).exclude(graphid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
        resource_data = []
        node = models.Node.objects.get(graph_id=graphid, istopnode=True)
        relatable_resources = node.get_relatable_resources()
        for res in resource_graphs:
            if models.Node.objects.filter(graph=res, istopnode=True).count() > 0:
                node_model = models.Node.objects.get(graph=res, istopnode=True)
                resource_data.append({"id": node_model.nodeid, "graph": res, "is_relatable": (node_model in relatable_resources)})
        data = {
            "icons": JSONSerializer().serializeToPython(icons),
            "node_count": models.Node.objects.filter(graph=self.graph).count(),
            "resources": JSONSerializer().serializeToPython(resource_data),
        }
        return JSONResponse(data)

    def post(self, request, graphid):
        graph = Graph.objects.get(graphid=graphid)
        data = JSONDeserializer().deserialize(request.body)
        for key, value in data.get("graph").items():
            if key in [
                "iconclass",
                "name",
                "author",
                "description",
                "isresource",
                "ontology_id",
                "version",
                "subtitle",
                "isactive",
                "color",
                "jsonldcontext",
                "slug",
                "config",
                "template_id",
            ]:
                setattr(graph, key, value)

        node = models.Node.objects.get(graph_id=graphid, istopnode=True)
        node.set_relatable_resources(data.get("relatable_resource_ids"))
        try:
            node.datatype = data["graph"]["root"]["datatype"]
        except KeyError as e:
            print(e, "Cannot find root node datatype")
        node.ontologyclass = data.get("ontology_class") if data.get("graph").get("ontology_id") is not None else None
        node.name = graph.name
        graph.root.name = node.name

        if graph.isresource is False and "root" in data["graph"]:
            node.config = data["graph"]["root"]["config"]

        try:
            with transaction.atomic():
                graph.save()
                node.save()

            return JSONResponse(
                {"success": True, "graph": graph, "relatable_resource_ids": [res.nodeid for res in node.get_relatable_resources()]}
            )

        except GraphValidationError as e:
            return JSONErrorResponse(e.title, e.message)


@method_decorator(group_required("Graph Editor"), name="dispatch")
class GraphManagerView(GraphBaseView):
    def get(self, request, graphid):
        if graphid is None or graphid == "":
            root_nodes = models.Node.objects.filter(istopnode=True)
            context = self.get_context_data(main_script="views/graph", root_nodes=JSONSerializer().serialize(root_nodes))
            context["graph_models"] = models.GraphModel.objects.all().exclude(graphid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
            context["graphs"] = JSONSerializer().serialize(context["graph_models"], exclude=["functions"])
            context["nav"]["title"] = _("Arches Designer")
            context["nav"]["icon"] = "fa-bookmark"

            context["nav"]["help"] = {"title": _("Using the Arches Designer"), "template": "arches-designer-help"}
            return render(request, "views/graph.htm", context)


@method_decorator(group_required("Graph Editor"), name="dispatch")
class GraphDesignerView(GraphBaseView):
    def get_ontology_namespaces(self):
        ontology_namespaces = settings.ONTOLOGY_NAMESPACES
        for ontology in models.Ontology.objects.all():
            try:
                namespace_keys = ontology.namespaces.keys()
                for k in namespace_keys:
                    if k not in ontology_namespaces:
                        ontology_namespaces[k] = ontology.namespaces[k]
            except AttributeError as e:
                logger.info(
                    _(
                        "No namespaces appear to be associated with {ontology.ontologyid} in the ontologies table."
                        " This is not a problem as long as all necessary namespaces are included in the"
                        " ONTOLOGY_NAMESPACES setting."
                    ).format(**locals())
                )
        return ontology_namespaces

    def get(self, request, graphid):
        self.graph = Graph.objects.get(graphid=graphid)
        ontologies = models.Ontology.objects.filter(parentontology=None)
        ontology_classes = models.OntologyClass.objects.values("source", "ontology_id")
        datatypes = models.DDataType.objects.all()
        datatypes_json = JSONSerializer().serialize(datatypes, exclude=["modulename", "isgeometric"])
        branch_graphs = Graph.objects.exclude(pk=graphid).exclude(isresource=True)
        applied_functions = JSONSerializer().serialize(models.FunctionXGraph.objects.filter(graph=self.graph))
        cards = self.graph.cardmodel_set.order_by("sortorder").prefetch_related("cardxnodexwidget_set")
        constraints = []
        for card in cards:
            if models.ConstraintModel.objects.filter(card=card).count() > 0:
                constraints += models.ConstraintModel.objects.filter(card=card)

        cardwidgets = [
            widget for widgets in [card.cardxnodexwidget_set.order_by("sortorder").all() for card in cards] for widget in widgets
        ]
        widgets = models.Widget.objects.all()
        nodegroups = cards.values_list("nodegroup_id", flat=True)

        if settings.OVERRIDE_RESOURCE_MODEL_LOCK:
            restricted_nodegroups = []
        else:
            restricted_nodegroups = (
                models.TileModel.objects.filter(nodegroup__in=nodegroups).values_list("nodegroup_id", flat=True).distinct()
            )

        card_components = models.CardComponent.objects.all()
        map_layers = models.MapLayer.objects.all()
        map_markers = models.MapMarker.objects.all()
        map_sources = models.MapSource.objects.all()
        templates = models.ReportTemplate.objects.all()
        card_components = models.CardComponent.objects.all()
        geocoding_providers = models.Geocoder.objects.all()
        if self.graph.ontology is not None:
            branch_graphs = branch_graphs.filter(ontology=self.graph.ontology)
        context = self.get_context_data(
            main_script="views/graph-designer",
            datatypes_json=datatypes_json,
            datatypes=datatypes,
            ontology_namespaces=self.get_ontology_namespaces(),
            branches=JSONSerializer().serialize(
                branch_graphs, exclude=["cards", "domain_connections", "functions", "cards", "deploymentfile", "deploymentdate"]
            ),
            branch_list={"title": _("Branch Library"), "search_placeholder": _("Find a graph branch")},
            widgets=widgets,
            widgets_json=JSONSerializer().serialize(widgets),
            card_components=card_components,
            card_components_json=JSONSerializer().serialize(card_components),
            cards=JSONSerializer().serialize(cards),
            cardwidgets=JSONSerializer().serialize(cardwidgets),
            map_layers=map_layers,
            map_markers=map_markers,
            map_sources=map_sources,
            applied_functions=applied_functions,
            geocoding_providers=geocoding_providers,
            report_templates=templates,
            restricted_nodegroups=[str(nodegroup) for nodegroup in restricted_nodegroups],
        )
        context["ontologies"] = JSONSerializer().serialize(ontologies, exclude=["version", "path"])
        context["ontology_classes"] = JSONSerializer().serialize(ontology_classes)
        context["graph"] = JSONSerializer().serialize(
            self.graph, exclude=["functions", "cards", "deploymentfile", "deploymentdate", "_nodegroups_to_delete", "_functions"]
        )
        context["graph_models"] = models.GraphModel.objects.all().exclude(graphid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
        context["graphs"] = JSONSerializer().serialize(context["graph_models"], exclude=["functions"])
        context["nav"]["title"] = self.graph.name
        context["nav"]["menu"] = True

        help_title = _("Designing a Resource Model")
        if not self.graph.isresource:
            help_title = _("Designing a Branch")

        context["nav"]["help"] = {"title": help_title, "template": "graph-tab-help"}
        context["constraints"] = JSONSerializer().serialize(constraints)

        return render(request, "views/graph-designer.htm", context)


class GraphDataView(View):

    action = "update_node"
    def get(self, request, graphid, nodeid=None):
        if self.action == "export_graph":
            graph = get_graphs_for_export([graphid])
            graph["metadata"] = system_metadata()
            f = JSONSerializer().serialize(graph, indent=4)
            graph_name = JSONDeserializer().deserialize(f)["graph"][0]["name"]

            response = HttpResponse(f, content_type="json/plain")
            response["Content-Disposition"] = 'attachment; filename="%s.json"' % (graph_name)
            return response
        elif self.action == "export_mapping_file":
            files_for_export = create_mapping_configuration_file(graphid, True)
            file_name = Graph.objects.get(graphid=graphid).name

            buffer = BytesIO()

            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip:
                for f in files_for_export:
                    f["outputfile"].seek(0)
                    zip.writestr(f["name"], f["outputfile"].read())

            zip.close()
            buffer.flush()
            zip_stream = buffer.getvalue()
            buffer.close()

            response = HttpResponse()
            response["Content-Disposition"] = "attachment; filename=" + file_name + ".zip"
            response["Content-length"] = str(len(zip_stream))
            response["Content-Type"] = "application/zip"
            response.write(zip_stream)
            return response

        elif self.action == "get_domain_connections":
            res = []
            graph = Graph.objects.get(graphid=graphid)
            ret = graph.get_valid_domain_ontology_classes()
            for r in ret:
                res.append({"ontology_property": r["ontology_property"], "ontology_classes": [c for c in r["ontology_classes"]]})
            return JSONResponse(res)

        elif self.action == "get_nodes":
            graph = Graph.objects.get(graphid=graphid)
            return JSONResponse(graph.nodes)

        elif self.action == "get_related_nodes":
            parent_nodeid = request.GET.get("parent_nodeid", None)
            graph = Graph.objects.get(graphid=graphid)
            ret = graph.get_valid_ontology_classes(nodeid=nodeid, parent_nodeid=parent_nodeid)
            return JSONResponse(ret)

        elif self.action == "get_valid_domain_nodes":
            graph = Graph.objects.get(graphid=graphid)
            if nodeid == "":
                nodeid = None
            ret = graph.get_valid_domain_ontology_classes(nodeid=nodeid)
            return JSONResponse(ret)

        return HttpResponseNotFound()

    @method_decorator(group_required("Graph Editor"), name="dispatch")
    def post(self, request, graphid=None):
        ret = {}
        try:
            if self.action == "import_graph":
                graph_file = request.FILES.get("importedGraph").read()
                graphs = JSONDeserializer().deserialize(graph_file)["graph"]
                ret = GraphImporter.import_graph(graphs)
            else:
                if graphid is not None:
                    graph = Graph.objects.get(graphid=graphid)
                data = JSONDeserializer().deserialize(request.body)

                if self.action == "new_graph":
                    isresource = data["isresource"] if "isresource" in data else False
                    name = _("New Resource Model") if isresource else _("New Branch")
                    author = request.user.first_name + " " + request.user.last_name
                    ret = Graph.new(name=name, is_resource=isresource, author=author)

                elif self.action == "update_node":
                    old_node_data = graph.nodes.get(uuid.UUID(data["nodeid"]))
                    nodegroup_changed = str(old_node_data.nodegroup_id) != data["nodegroup_id"]
                    updated_values = graph.update_node(data)
                    if "nodeid" in data and nodegroup_changed is False:
                        graph.save(nodeid=data["nodeid"])
                    else:
                        graph.save()
                    ret = JSONSerializer().serializeToPython(graph)
                    ret["updated_values"] = updated_values
                    ret["default_card_name"] = graph.temp_node_name

                elif self.action == "update_node_layer":
                    nodeid = uuid.UUID(str(data.get("nodeid")))
                    node = graph.nodes[nodeid]
                    node.config = data["config"]
                    ret = graph
                    node.save()

                elif self.action == "append_branch":
                    ret = graph.append_branch(data["property"], nodeid=data["nodeid"], graphid=data["graphid"])
                    ret = ret.serialize()
                    ret["nodegroups"] = graph.get_nodegroups()
                    ret["cards"] = graph.get_cards()
                    ret["widgets"] = graph.get_widgets()
                    graph.save()

                elif self.action == "append_node":
                    ret = graph.append_node(nodeid=data["nodeid"])
                    graph.save()

                elif self.action == "move_node":
                    ret = graph.move_node(data["nodeid"], data["property"], data["newparentnodeid"])
                    graph.save()

                elif self.action == "export_branch":
                    clone_data = graph.copy(root=data)
                    clone_data["copy"].slug = None
                    clone_data["copy"].save()
                    ret = {"success": True, "graphid": clone_data["copy"].pk}

                elif self.action == "clone_graph":
                    clone_data = graph.copy()
                    ret = clone_data["copy"]
                    ret.slug = None
                    ret.save()
                    ret.copy_functions(graph, [clone_data["nodes"], clone_data["nodegroups"]])

                elif self.action == "reorder_nodes":
                    json = request.body
                    if json is not None:
                        data = JSONDeserializer().deserialize(json)

                        if "nodes" in data and len(data["nodes"]) > 0:
                            sortorder = 0
                            with transaction.atomic():
                                for node in data["nodes"]:
                                    no = models.Node.objects.get(pk=node["nodeid"])
                                    no.sortorder = sortorder
                                    no.save()
                                    sortorder = sortorder + 1
                            ret = data

            return JSONResponse(ret)
        except GraphValidationError as e:
            return JSONErrorResponse(e.title, e.message, {"status": "Failed"})
        except ModelInactiveError as e:
            return JSONErrorResponse(e.title, e.message)
        except RequestError as e:
            return JSONErrorResponse(
                _("Elasticsearch indexing error"),
                _(
                    """If you want to change the datatype of an existing node.  
                    Delete and then re-create the node, or export the branch then edit the datatype and re-import the branch."""
                ),
            )

    @method_decorator(group_required("Graph Editor"), name="dispatch")
    def delete(self, request, graphid):
        if self.action == "delete_node":
            data = JSONDeserializer().deserialize(request.body)
            try:
                graph = Graph.objects.get(graphid=graphid)
                graph.delete_node(node=data.get("nodeid", None))
                return JSONResponse({})
            except GraphValidationError as e:
                return JSONErrorResponse(e.title, e.message)
        elif self.action == "delete_instances":
            try:
                graph = Graph.objects.get(graphid=graphid)
                graph.delete_instances()
                return JSONResponse(
                    {
                        "success": True,
                        "message": "All the resources associated with the Model '{0}' have been successfully deleted.".format(graph.name),
                        "title": "Resources Successfully Deleted.",
                    }
                )
            except GraphValidationError as e:
                return JSONErrorResponse(e.title, e.message)
            except ModelInactiveError as e:
                return JSONErrorResponse(e.title, e.message)
        elif self.action == "delete_graph":
            try:
                graph = Graph.objects.get(graphid=graphid)
                if graph.isresource:
                    graph.delete_instances()
                    graph.isactive = False
                    graph.save(validate=False)
                graph.delete()
                return JSONResponse({"success": True})
            except GraphValidationError as e:
                return JSONErrorResponse(e.title, e.message)

        return HttpResponseNotFound()


@method_decorator(group_required("Graph Editor"), name="dispatch")
class CardView(GraphBaseView):
    action = "update_card"

    def post(self, request, cardid=None):
        data = JSONDeserializer().deserialize(request.body)
        if self.action == "update_card":
            if data:
                card = Card(data)
                card.save()
                return JSONResponse(card)

        if self.action == "reorder_cards":
            if "cards" in data and len(data["cards"]) > 0:
                with transaction.atomic():
                    for card_data in data["cards"]:
                        card = models.CardModel.objects.get(pk=card_data["id"])
                        card.sortorder = card_data["sortorder"]
                        card.save()
                return JSONResponse(data["cards"])

        return HttpResponseNotFound()


class DatatypeTemplateView(TemplateView):
    def get(sefl, request, template="text"):
        return render(request, "views/components/datatypes/%s.htm" % template)


@method_decorator(group_required("Graph Editor"), name="dispatch")
class FunctionManagerView(GraphBaseView):
    action = ""

    def get(self, request, graphid):
        self.graph = Graph.objects.get(graphid=graphid)

        if self.graph.isresource:
            context = self.get_context_data(
                main_script="views/graph/function-manager",
                functions=JSONSerializer().serialize(models.Function.objects.all()),
                applied_functions=JSONSerializer().serialize(models.FunctionXGraph.objects.filter(graph=self.graph)),
                function_templates=models.Function.objects.exclude(component__isnull=True),
            )

            context["graphs"] = JSONSerializer().serialize(
                models.GraphModel.objects.all().exclude(graphid=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID), exclude=["functions"]
            )
            context["nav"]["title"] = self.graph.name
            context["nav"]["menu"] = True
            context["nav"]["help"] = {"title": _("Managing Functions"), "template": "function-help"}

            return render(request, "views/graph/function-manager.htm", context)
        else:
            return redirect("graph_designer", graphid=graphid)

    def post(self, request, graphid):
        data = JSONDeserializer().deserialize(request.body)
        self.graph = Graph.objects.get(graphid=graphid)
        with transaction.atomic():
            for item in data:
                functionXgraph, created = models.FunctionXGraph.objects.update_or_create(
                    pk=item["id"], defaults={"function_id": item["function_id"], "graph_id": graphid, "config": item["config"]}
                )
                item["id"] = functionXgraph.pk

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
                functionXgraph = models.FunctionXGraph.objects.get(pk=item["id"])
                functionXgraph.delete()

        return JSONResponse(data)


@method_decorator(group_required("Graph Editor"), name="dispatch")
class PermissionDataView(View):
    perm_cache = {}
    action = None

    def get_perm_name(self, codename):
        if codename not in self.perm_cache:
            try:
                self.perm_cache[codename] = Permission.objects.get(
                    codename=codename, content_type__app_label="models", content_type__model="nodegroup"
                )
                return self.perm_cache[codename]
            except:
                return None
                # codename for nodegroup probably doesn't exist
        return self.perm_cache[codename]

    def get(self, request):
        if self.action == "get_permission_manager_data":
            identities = []
            for group in Group.objects.all():
                identities.append({"name": group.name, "type": "group", "id": group.pk, "default_permissions": group.permissions.all()})
            for user in User.objects.filter(is_superuser=False):
                groups = []
                default_perms = []
                for group in user.groups.all():
                    groups.append(group.name)
                    default_perms = default_perms + list(group.permissions.all())
                identities.append(
                    {
                        "name": user.email or user.username,
                        "groups": ", ".join(groups),
                        "type": "user",
                        "id": user.pk,
                        "default_permissions": set(default_perms),
                    }
                )

            content_type = ContentType.objects.get_for_model(models.NodeGroup)
            nodegroup_permissions = Permission.objects.filter(content_type=content_type)
            ret = {"identities": identities, "permissions": nodegroup_permissions}
            return JSONResponse(ret)

        nodegroup_ids = JSONDeserializer().deserialize(request.GET.get("nodegroupIds"))
        identityId = request.GET.get("identityId")
        identityType = request.GET.get("identityType")

        ret = []
        if identityType == "group":
            identity = Group.objects.get(pk=identityId)
            for nodegroup_id in nodegroup_ids:
                nodegroup = models.NodeGroup.objects.get(pk=nodegroup_id)
                perms = [
                    {"codename": codename, "name": self.get_perm_name(codename).name} for codename in get_group_perms(identity, nodegroup)
                ]
                ret.append({"perms": perms, "nodegroup_id": nodegroup_id})
        else:
            identity = User.objects.get(pk=identityId)
            for nodegroup_id in nodegroup_ids:
                nodegroup = models.NodeGroup.objects.get(pk=nodegroup_id)
                perms = [
                    {"codename": codename, "name": self.get_perm_name(codename).name} for codename in get_user_perms(identity, nodegroup)
                ]

                # only get the group perms ("defaults") if no user defined object settings have been saved
                if len(perms) == 0:
                    perms = [
                        {"codename": codename, "name": self.get_perm_name(codename).name}
                        for codename in set(get_group_perms(identity, nodegroup))
                    ]
                ret.append({"perms": perms, "nodegroup_id": nodegroup_id})

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
            for identity in data["selectedIdentities"]:
                if identity["type"] == "group":
                    identityModel = Group.objects.get(pk=identity["id"])
                else:
                    identityModel = User.objects.get(pk=identity["id"])

                for card in data["selectedCards"]:
                    # TODO The following try block is here because the key for the nodegroupid in the new permission manager
                    # is 'nodegroupid' where it was 'nodegroup' in the old permission manager. Once the old permission manager is deleted
                    # we can replace it with `nodegroupid = card['nodegroupid']`
                    try:
                        nodegroupid = card["nodegroupid"]
                    except KeyError:
                        nodegroupid = card["nodegroup"]
                    nodegroup = models.NodeGroup.objects.get(pk=nodegroupid)

                    # first remove all the current permissions
                    for perm in get_perms(identityModel, nodegroup):
                        remove_perm(perm, identityModel, nodegroup)

                    if not revert:
                        # then add the new permissions
                        for perm in data["selectedPermissions"]:
                            assign_perm(perm["codename"], identityModel, nodegroup)


class IconDataView(View):
    def get(self, request):
        icons = models.Icon.objects.order_by("name")
        data = {"icons": JSONSerializer().serializeToPython(icons)}
        return JSONResponse(data)


class NodegroupView(View):
    action = "exportable"

    def get(self, request):
        nodegroupid = None
        try:
            nodegroupid = uuid.UUID(str(request.GET.get("nodegroupid")))
        except Exception as e:
            print(e)
        if self.action == "exportable":
            res = []
            if nodegroupid is not None:
                nodegroup = models.NodeGroup.objects.get(nodegroupid=nodegroupid)
                exportable = False if nodegroup.exportable is None else nodegroup.exportable
                res.append({"exportable": exportable})
                return JSONResponse(res)
            else:
                return HttpResponseNotFound()

    def post(self, request):
        nodegroupid = None
        try:
            nodegroupid = uuid.UUID(str(request.POST.get("nodegroupid")))
        except Exception as e:
            print(e)
        if self.action == "exportable" and nodegroupid is not None:
            exportable = json.loads(request.POST.get("exportable"))

            nodegroup = models.NodeGroup.objects.select_for_update().filter(nodegroupid=nodegroupid)
            with transaction.atomic():
                for ng in nodegroup:
                    ng.exportable = exportable
                    ng.save()

            return JSONResponse({"nodegroup": nodegroupid, "status": "success"})

        return HttpResponseNotFound()
