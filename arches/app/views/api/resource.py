import json
import logging
import sys
import traceback
import uuid
from collections import OrderedDict
from http import HTTPStatus

from django.core.cache import cache
from django.db import transaction
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import get_language, gettext as _
from django.views.decorators.csrf import csrf_exempt

from arches.app.models import models
from arches.app.models.card import Card as CardProxyModel
from arches.app.models.graph import Graph
from arches.app.models.resource import Resource
from arches.app.models.system_settings import settings
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.data_management.resources.exporter import ResourceExporter
from arches.app.utils.data_management.resources.formats.rdffile import JsonLdReader
from arches.app.utils.data_management.resources.formats.archesfile import (
    ArchesFileReader,
)
from arches.app.utils.permission_backend import (
    user_can_read_resource,
    user_can_edit_resource,
    user_can_delete_resource,
    get_nodegroups_by_perm,
)
from arches.app.utils.permission_backend import get_nodegroups_by_perm
from arches.app.utils.permission_backend import user_is_resource_reviewer
from arches.app.utils.response import JSONResponse, JSONErrorResponse
from arches.app.views.api import APIBase
from arches.app.views.resource import (
    RelatedResourcesView,
    get_resource_relationship_types,
)

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class Resources(APIBase):
    # context = [{
    #     "@context": {
    #         "id": "@id",
    #         "type": "@type",
    #         "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    #         "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    #         "crm": "http://www.cidoc-crm.org/cidoc-crm/",
    #         "la": "https://linked.art/ns/terms/",

    #         "Right": "crm:E30_Right",
    #         "LinguisticObject": "crm:E33_Linguistic_Object",
    #         "Name": "la:Name",
    #         "Identifier": "crm:E42_Identifier",
    #         "Language": "crm:E56_Language",
    #         "Type": "crm:E55_Type",

    #         "label": "rdfs:label",
    #         "value": "rdf:value",
    #         "classified_as": "crm:P2_has_type",
    #         "referred_to_by": "crm:P67i_is_referred_to_by",
    #         "language": "crm:P72_has_language",
    #         "includes": "crm:P106_is_composed_of",
    #         "identified_by": "crm:P1_is_identified_by"
    #     }
    # },{
    #     "@context": "https://linked.art/ns/v1/linked-art.json"
    # }]

    def get(self, request, resourceid=None, slug=None, graphid=None):
        try:
            resource = (
                Resource.objects.filter(pk=resourceid)
                .select_related(
                    "graph",
                    "resource_instance_lifecycle_state",
                )
                .get()
            )
        except Resource.DoesNotExist as dne:
            logger.error(
                _("The specified resource '{0}' does not exist. Export failed.").format(
                    resourceid
                )
            )
            return JSONErrorResponse(message=dne.args[0], status=HTTPStatus.NOT_FOUND)

        if not user_can_read_resource(user=request.user, resource=resource):
            return JSONResponse(status=403)

        allowed_formats = ["json", "json-ld", "arches-json"]
        format = request.GET.get("format", "json-ld")
        hide_hidden_nodes = bool(request.GET.get("hidden", "true").lower() == "false")
        user = request.user
        perm = "read_nodegroup"

        if format not in allowed_formats:
            return JSONResponse(
                status=406,
                reason="incorrect format specified, only %s formats allowed"
                % allowed_formats,
            )

        indent = request.GET.get("indent")
        if indent and str.isdigit(indent):
            indent = int(indent)
        else:
            indent = None

        if resourceid:
            if format == "json":
                version = request.GET.get("v", None)
                compact = bool(
                    request.GET.get("compact", "true").lower() == "true"
                )  # default True
                hide_empty_nodes = bool(
                    request.GET.get("hide_empty_nodes", "false").lower() == "true"
                )  # default False

                if version == "beta":
                    out = resource.to_json(
                        compact=compact,
                        hide_empty_nodes=hide_empty_nodes,
                        user=user,
                        perm=perm,
                        version=version,
                        hide_hidden_nodes=hide_hidden_nodes,
                    )
                else:
                    out = {
                        "resource": resource.to_json(
                            compact=compact,
                            hide_empty_nodes=hide_empty_nodes,
                            user=user,
                            perm=perm,
                            version=version,
                            hide_hidden_nodes=hide_hidden_nodes,
                        ),
                        "displaydescription": resource.displaydescription(),
                        "displayname": resource.displayname(),
                        "graph_id": resource.graph_id,
                        "legacyid": resource.legacyid,
                        "map_popup": resource.map_popup(),
                        "resourceinstanceid": resource.resourceinstanceid,
                    }

            elif format == "arches-json":
                out = resource
                include_tiles = bool(
                    request.GET.get("includetiles", "true").lower() == "true"
                )  # default True

                if include_tiles:
                    out.load_tiles(user, perm)

            elif format == "json-ld":
                if not resource.graph.ontology_id:
                    return JSONErrorResponse(
                        message=_(
                            "The graph '{0}' does not have an ontology. JSON-LD requires one."
                        ).format(resource.graph.name),
                        status=400,
                    )
                exporter = ResourceExporter(format=format)
                output = exporter.writer.write_resources(
                    resourceinstanceids=[resourceid],
                    indent=indent,
                    user=request.user,
                )
                out = output[0]["outputfile"].getvalue()

        else:
            #
            # The following commented code would be what you would use if you wanted to use the rdflib module,
            # the problem with using this is that items in the "ldp:contains" array don't maintain a consistent order
            #

            # archesproject = Namespace(settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT)
            # ldp = Namespace('https://www.w3.org/ns/ldp/')

            # g = Graph()
            # g.bind('archesproject', archesproject, False)
            # g.add((archesproject['resources'], RDF.type, ldp['BasicContainer']))

            # base_url = "%s%s" % (settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT, reverse('resources',args=['']).lstrip('/'))
            # for resourceid in list(Resource.objects.values_list('pk', flat=True).order_by('pk')[:10]):
            #     g.add((archesproject['resources'], ldp['contains'], URIRef("%s%s") % (base_url, resourceid) ))

            # value = g.serialize(format='nt')
            # out = from_rdf(str(value), options={format:'application/nquads'})
            # framing = {
            #     "@omitDefault": True
            # }

            # out = frame(out, framing)
            # context = {
            #     "@context": {
            #         'ldp': 'https://www.w3.org/ns/ldp/',
            #         'arches': settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT
            #     }
            # }
            # out = compact(out, context, options={'skipExpansion':False, 'compactArrays': False})

            page_size = settings.API_MAX_PAGE_SIZE

            try:
                page = int(request.GET.get("page", None))
            except Exception:
                page = 1

            start = (page - 1) * page_size
            end = start + page_size

            base_url = "%s%s" % (
                settings.ARCHES_NAMESPACE_FOR_DATA_EXPORT,
                reverse("resources", args=[""]).lstrip("/"),
            )
            out = {
                "@context": "https://www.w3.org/ns/ldp/",
                "@id": "",
                "@type": "ldp:BasicContainer",
                # Here we actually mean the name
                # "label": str(model.name),
                "ldp:contains": [
                    "%s%s" % (base_url, resourceid)
                    for resourceid in list(
                        Resource.objects.values_list("pk", flat=True)
                        .exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_ID)
                        .order_by("pk")[start:end]
                    )
                ],
            }

        return JSONResponse(out, indent=indent)

    def put(self, request, resourceid, slug=None, graphid=None):
        allowed_formats = ["arches-json", "json-ld"]
        indent = request.GET.get("indent", None)
        format = request.GET.get("format", "json-ld")

        if format not in allowed_formats:
            return JSONResponse(
                status=406,
                reason="incorrect format specified, only %s formats allowed"
                % allowed_formats,
            )

        if format == "json-ld" and slug is None and graphid is None:
            return JSONResponse(
                {
                    "error": "Need to supply either a graph id or slug in the request url.  See the API reference in the developer documentation at https://arches.readthedocs.io for more details"
                },
                status=400,
            )

        if not user_can_edit_resource(user=request.user, resourceid=resourceid):
            return JSONErrorResponse(status=403)
        else:
            with transaction.atomic():
                try:
                    if format == "json-ld":
                        data = JSONDeserializer().deserialize(request.body)
                        reader = JsonLdReader()
                        if slug is not None:
                            graphid = models.GraphModel.objects.get(
                                slug=slug, source_identifier=None
                            ).pk
                        reader.read_resource(
                            data, resourceid=resourceid, graphid=graphid
                        )
                        if reader.errors:
                            response = []
                            for value in reader.errors.values():
                                response.append(value.message)
                            return JSONResponse(
                                {"error": response}, indent=indent, status=400
                            )
                        else:
                            response = []
                            for resource in reader.resources:
                                with transaction.atomic():
                                    try:
                                        # DELETE
                                        resource_instance = Resource.objects.get(
                                            pk=resource.pk
                                        )
                                        resource_instance.delete()
                                    except models.ResourceInstance.DoesNotExist:
                                        pass
                                    resource.save(request=request)
                                response.append(
                                    JSONDeserializer().deserialize(
                                        self.get(
                                            request, resource.resourceinstanceid
                                        ).content
                                    )
                                )
                            return JSONResponse(response, indent=indent, status=201)

                    elif format == "arches-json":
                        reader = ArchesFileReader()
                        archesresource = JSONDeserializer().deserialize(request.body)

                        # IF a resource id is supplied in the url it should match the resource ids in the body of the request.
                        if resourceid != archesresource["resourceinstanceid"]:
                            return JSONResponse(
                                {
                                    "error": "Resource id in the URI does not match the resourceinstanceid supplied in the document"
                                },
                                indent=indent,
                                status=400,
                            )

                        #  Resource id's in the request body take precedence over the id supplied in the url.
                        resource = {
                            "resourceinstance": {
                                "graph_id": archesresource["graph_id"],
                                "resourceinstanceid": archesresource[
                                    "resourceinstanceid"
                                ],
                                "legacyid": archesresource["legacyid"],
                            },
                            "tiles": archesresource["tiles"],
                        }

                        reader.import_business_data({"resources": [resource]})

                        if reader.errors:
                            response = []
                            for value in reader.errors.values():
                                response.append(value.message)
                            return JSONResponse(
                                {"error": response}, indent=indent, status=400
                            )
                        else:
                            response = []
                            response.append(
                                JSONDeserializer().deserialize(
                                    self.get(
                                        request, archesresource["resourceinstanceid"]
                                    ).content
                                )
                            )
                            return JSONResponse(response, indent=indent, status=201)

                except models.ResourceInstance.DoesNotExist:
                    return JSONResponse(status=404)
                except Exception as e:
                    return JSONResponse(
                        {"error": "resource data could not be saved"},
                        status=500,
                        reason=e,
                    )

    def post(self, request, resourceid=None, slug=None, graphid=None):
        allowed_formats = ["arches-json", "json-ld"]
        indent = request.POST.get("indent", None)
        format = request.GET.get("format", "json-ld")

        if format not in allowed_formats:
            return JSONResponse(
                status=406,
                reason="incorrect format specified, only %s formats allowed"
                % allowed_formats,
            )

        if format == "json-ld" and slug is None and graphid is None:
            return JSONResponse(
                {
                    "error": "Need to supply either a graph id or slug in the request url.  See the API reference in the developer documentation at https://arches.readthedocs.io for more details"
                },
                status=400,
            )

        try:
            if user_can_edit_resource(user=request.user, resourceid=resourceid):
                if format == "json-ld":
                    data = JSONDeserializer().deserialize(request.body)
                    reader = JsonLdReader()
                    if slug is not None:
                        graphid = models.GraphModel.objects.get(
                            slug=slug, source_identifier=None
                        ).pk
                    reader.read_resource(data, graphid=graphid)
                    if reader.errors:
                        response = []
                        for value in reader.errors.values():
                            response.append(value.message)
                        return JSONResponse(
                            {"error": response}, indent=indent, status=400
                        )
                    else:
                        response = []
                        for resource in reader.resources:
                            with transaction.atomic():
                                resource.save(request=request)
                            response.append(
                                JSONDeserializer().deserialize(
                                    self.get(
                                        request, resource.resourceinstanceid
                                    ).content
                                )
                            )
                        return JSONResponse(response, indent=indent, status=201)

                elif format == "arches-json":
                    reader = ArchesFileReader()
                    archesresource = JSONDeserializer().deserialize(request.body)

                    nascent_resourceinstanceid = str(uuid.uuid4())

                    resource = {
                        "resourceinstance": {
                            "graph_id": archesresource["graph_id"],
                            "resourceinstanceid": nascent_resourceinstanceid,
                            "legacyid": archesresource["legacyid"],
                        },
                        "tiles": archesresource["tiles"],
                    }

                    reader.import_business_data({"resources": [resource]})

                    if reader.errors:
                        response = []
                        for value in reader.errors.values():
                            response.append(value.message)
                        return JSONResponse(
                            {"error": response}, indent=indent, status=400
                        )
                    else:
                        response = []
                        response.append(
                            JSONDeserializer().deserialize(
                                self.get(request, nascent_resourceinstanceid).content
                            )
                        )
                        return JSONResponse(response, indent=indent, status=201)

            else:
                return JSONResponse(status=403)
        except Exception as e:
            if settings.DEBUG is True:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                formatted = traceback.format_exception(
                    exc_type, exc_value, exc_traceback
                )
                if len(formatted):
                    for message in formatted:
                        print(message)
            return JSONResponse(
                {"error": "resource data could not be saved: %s" % e},
                status=500,
                reason=e,
            )

    def delete(self, request, resourceid, slug=None, graphid=None):
        try:
            resource_instance = Resource.objects.get(pk=resourceid)
        except Resource.DoesNotExist as dne:
            return JSONErrorResponse(message=dne.args[0], status=404)
        if user_can_edit_resource(
            user=request.user, resource=resource_instance
        ) and user_can_delete_resource(user=request.user, resource=resource_instance):
            resource_instance.delete()
        else:
            return JSONResponse(status=500)

        return JSONResponse(status=200)


class ResourceInstanceLifecycleStates(APIBase):
    def get(self, request):
        return JSONResponse(models.ResourceInstanceLifecycleState.objects.all())


class ResourceInstanceLifecycleState(APIBase):
    def get(self, request, resourceid):
        resource_instance = models.ResourceInstance.objects.get(pk=resourceid)
        return JSONResponse(resource_instance.resource_instance_lifecycle_state)

    def post(self, request, resourceid):
        if not user_is_resource_reviewer(request.user):
            return JSONErrorResponse(
                _("Request Failed"), _("Permission Denied"), status=403
            )
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JSONErrorResponse(str(e), status=400)

        try:
            resource = Resource.objects.get(pk=resourceid)
            resource_instance_lifecycle_state = (
                models.ResourceInstanceLifecycleState.objects.get(pk=data)
            )
        except Exception as e:
            return JSONErrorResponse(str(e), status=404)

        try:
            original_resource_instance_lifecycle_state = (
                resource.resource_instance_lifecycle_state
            )

            current_resource_instance_lifecycle_state = (
                resource.update_resource_instance_lifecycle_state(
                    user=request.user,
                    resource_instance_lifecycle_state=resource_instance_lifecycle_state,
                )
            )
        except ValueError as e:
            return JSONErrorResponse(str(e), status=400)

        return JSONResponse(
            {
                "original_resource_instance_lifecycle_state": original_resource_instance_lifecycle_state,
                "current_resource_instance_lifecycle_state": current_resource_instance_lifecycle_state,
            }
        )


class ResourceReport(APIBase):
    def get(self, request, resourceid):
        exclude = request.GET.get("exclude", [])
        uncompacted_value = request.GET.get("uncompacted")
        version = request.GET.get("v")
        compact = True
        if uncompacted_value == "true":
            compact = False
        perm = "read_nodegroup"

        resource = Resource.objects.get(pk=resourceid)
        published_graph = models.PublishedGraph.objects.get(
            publication=resource.graph_publication, language=get_language()
        )
        graph = Graph(published_graph.serialized_graph)
        template = models.ReportTemplate.objects.get(pk=graph.template_id)
        graph_has_different_publication = bool(
            resource.graph.publication_id != published_graph.publication_id
        )

        # if a user is viewing a report for a resource that does not have the same publication as the current graph publication
        # ( and therefore is out-of-date ) only allow them to access report details if they have Graph Editor permissions or higher.
        if (
            graph_has_different_publication
            and not request.user.groups.filter(
                name__in=[
                    "Graph Editor",
                    "RDM Administrator",
                    "Application Administrator",
                    "System Administrator",
                ]
            ).exists()
        ):
            return JSONResponse(
                {
                    "displayname": resource.displayname(),
                    "resourceid": resourceid,
                    "hide_empty_nodes": settings.HIDE_EMPTY_NODES_IN_REPORT,
                    "template": template,
                    "graph": graph,
                }
            )

        if not template.preload_resource_data:
            return JSONResponse(
                {
                    "template": template,
                    "report_json": resource.to_json(
                        compact=compact, version=version, user=request.user, perm=perm
                    ),
                }
            )

        resp = {
            "datatypes": models.DDataType.objects.all(),
            "displayname": resource.displayname(),
            "resourceid": resourceid,
            "graph": graph,
            "hide_empty_nodes": settings.HIDE_EMPTY_NODES_IN_REPORT,
            # "report_json": resource.to_json(compact=compact, version=version),
        }

        if "template" not in exclude:
            resp["template"] = template

        if "related_resources" not in exclude:
            resource_models = (
                models.GraphModel.objects.filter(isresource=True)
                .exclude(is_active=False)
                .exclude(pk=settings.SYSTEM_SETTINGS_RESOURCE_MODEL_ID)
                .exclude(source_identifier__isnull=False)
            )

            get_params = request.GET.copy()
            get_params.update({"paginate": "false"})
            request.GET = get_params

            related_resources_response = RelatedResourcesView().get(
                request, resourceid, include_rr_count=False, graphs=resource_models
            )
            related_resources = json.loads(related_resources_response.content)

            related_resources_summary = self._generate_related_resources_summary(
                related_resources=related_resources["related_resources"],
                resource_relationships=related_resources["resource_relationships"],
                resource_models=resource_models,
            )

            resp["related_resources"] = related_resources_summary

        if "tiles" not in exclude:
            resource.load_tiles(user=request.user, perm=perm)
            permitted_tiles = resource.tiles

            resp["tiles"] = permitted_tiles

        if "cards" not in exclude:
            readable_nodegroup_ids = [
                nodegroup_id
                for nodegroup_id in get_nodegroups_by_perm(
                    request.user, perm, any_perm=True
                )
            ]
            writable_nodegroup_ids = [
                nodegroup_id
                for nodegroup_id in get_nodegroups_by_perm(
                    request.user,
                    "write_nodegroup",
                    any_perm=True,
                )
            ]

            permitted_cards = sorted(
                [
                    card
                    for card in graph.cards.values()
                    if card.nodegroup_id in readable_nodegroup_ids
                    and card.nodegroup_id in writable_nodegroup_ids
                ],
                key=lambda card: card.sortorder or 0,
            )

            permitted_card_ids = [card.pk for card in permitted_cards]
            cardwidgets = sorted(
                [
                    widget
                    for widget in graph.widgets
                    if widget["card_id"] in permitted_card_ids
                ],
                key=lambda widget: widget["sortorder"] or 0,
            )

            resp["cards"] = permitted_cards
            resp["cardwidgets"] = cardwidgets

        return JSONResponse(resp)

    def _generate_related_resources_summary(
        self, related_resources, resource_relationships, resource_models
    ):
        related_resource_summary = [
            {
                "graphid": str(resource_model.graphid),
                "name": resource_model.name,
                "resources": [],
            }
            for resource_model in resource_models
        ]

        resource_relationship_types = {
            resource_relationship_type["id"]: resource_relationship_type["text"]
            for resource_relationship_type in get_resource_relationship_types()[
                "values"
            ]
        }

        for related_resource in related_resources:
            for summary in related_resource_summary:
                if related_resource["graph_id"] == summary["graphid"]:
                    relationship_summary = []
                    for resource_relationship in resource_relationships:
                        if (
                            related_resource["resourceinstanceid"]
                            == resource_relationship["to_resource"]
                        ):
                            rr_type = (
                                resource_relationship_types[
                                    resource_relationship["relationshiptype"]
                                ]
                                if resource_relationship["relationshiptype"]
                                in resource_relationship_types
                                else resource_relationship["relationshiptype"]
                            )
                            relationship_summary.append(rr_type)
                        elif (
                            related_resource["resourceinstanceid"]
                            == resource_relationship["from_resource"]
                        ):
                            rr_type = (
                                resource_relationship_types[
                                    resource_relationship["inverserelationshiptype"]
                                ]
                                if resource_relationship["inverserelationshiptype"]
                                in resource_relationship_types
                                else resource_relationship["inverserelationshiptype"]
                            )
                            relationship_summary.append(rr_type)

                    summary["resources"].append(
                        {
                            "resourceinstanceid": related_resource[
                                "resourceinstanceid"
                            ],
                            "displayname": related_resource["displayname"],
                            "relationships": relationship_summary,
                        }
                    )

        return related_resource_summary


class BulkResourceReport(APIBase):
    def get(self, request):
        graph_ids = request.GET.get("graph_ids").split(",")
        exclude = request.GET.get("exclude", [])

        if not graph_ids:
            raise Exception()

        exclusions_querystring = request.GET.get("exclude", None)

        if exclusions_querystring is not None:
            exclusions = list(map(str.strip, exclude.split(",")))
        else:
            exclusions = []

        graph_ids_set = set(graph_ids)  # calls set to delete dups
        graph_ids_not_in_cache = []

        graph_lookup = {}

        for graph_id in graph_ids_set:
            graph = cache.get("serialized_graph_{}".format(graph_id))

            if graph:
                graph_lookup[graph["graphid"]] = graph
            else:
                graph_ids_not_in_cache.append(graph_id)

        if graph_ids_not_in_cache:
            graphs_from_database = list(
                Graph.objects.filter(pk__in=graph_ids_not_in_cache)
            )

            for graph in graphs_from_database:
                serialized_graph = JSONSerializer().serializeToPython(
                    graph, sort_keys=False, exclude=["functions"] + exclusions
                )
                cache.set("serialized_graph_{}".format(graph.pk), serialized_graph)
                graph_lookup[str(graph.pk)] = serialized_graph

        graph_ids_with_templates_that_preload_resource_data = []
        graph_ids_with_templates_that_do_not_preload_resource_data = []

        for graph in graph_lookup.values():
            template = models.ReportTemplate.objects.get(pk=graph["template_id"])

            if template.preload_resource_data:
                graph_ids_with_templates_that_preload_resource_data.append(
                    graph["graphid"]
                )
            else:
                graph_ids_with_templates_that_do_not_preload_resource_data.append(
                    graph["graphid"]
                )

        permitted_cards = []

        if "cards" not in exclude:
            cards = (
                CardProxyModel.objects.filter(
                    graph_id__in=graph_ids_with_templates_that_preload_resource_data
                )
                .select_related("nodegroup")
                .prefetch_related("cardxnodexwidget_set")
            )

            perm = "read_nodegroup"
            permitted_cards = []

            for card in cards:
                if request.user.has_perm(perm, card.nodegroup):
                    card.filter_by_perm(request.user, perm)
                    permitted_cards.append(card)

        if "datatypes" not in exclude:
            datatypes = list(models.DDataType.objects.all())

        resp = {}

        for graph_id in graph_ids_with_templates_that_preload_resource_data:
            graph = graph_lookup[graph_id]

            graph_cards = [
                card
                for card in permitted_cards
                if str(card.graph_id) == graph["graphid"]
            ]

            cardwidgets = [
                widget
                for widgets in [card.cardxnodexwidget_set.all() for card in graph_cards]
                for widget in widgets
            ]

            resp[graph_id] = {
                "graph": graph,
                "cards": JSONSerializer().serializeToPython(
                    graph_cards, sort_keys=False
                ),
                "cardwidgets": cardwidgets,
            }

            if "datatypes" not in exclude:
                resp[graph_id]["datatypes"] = datatypes

        for graph_id in graph_ids_with_templates_that_do_not_preload_resource_data:
            graph = graph_lookup[graph_id]
            resp[graph_id] = {"template_id": graph["template_id"]}

        return JSONResponse(resp)


class BulkDisambiguatedResourceInstance(APIBase):
    def get(self, request):
        resource_ids = request.GET.get("resource_ids").split(",")
        version = request.GET.get("v")
        hide_hidden_nodes = bool(request.GET.get("hidden", "true").lower() == "false")
        compact = bool(request.GET.get("uncompacted", "false").lower() == "false")
        user = request.user
        perm = "read_nodegroup"

        disambiguated_resource_instances = OrderedDict().fromkeys(resource_ids)
        for resource in Resource.objects.filter(pk__in=resource_ids):
            disambiguated_resource_instances[str(resource.pk)] = resource.to_json(
                compact=compact,
                version=version,
                hide_hidden_nodes=hide_hidden_nodes,
                user=user,
                perm=perm,
            )

        return JSONResponse(disambiguated_resource_instances, sort_keys=False)


@method_decorator(csrf_exempt, name="dispatch")
class InstancePermission(APIBase):
    def get(self, request):
        user = request.user
        result = {}
        resourceinstanceid = request.GET.get("resourceinstanceid")
        try:
            resource = models.ResourceInstance.objects.get(pk=resourceinstanceid)
        except models.ResourceInstance.DoesNotExist as dne:
            return JSONErrorResponse(message=dne.args[0], status=HTTPStatus.NOT_FOUND)
        result["read"] = user_can_read_resource(user, resource=resource)
        result["edit"] = user_can_edit_resource(user, resource=resource)
        result["delete"] = user_can_delete_resource(user, resource=resource)
        return JSONResponse(result)
