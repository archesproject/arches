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

import uuid
from django.db import transaction, connection
from django.db.models import Q
from django.http import (
    HttpResponse,
    HttpResponseNotFound,
    HttpResponseNotAllowed,
    HttpResponseServerError,
)
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _
from django.utils.translation import get_language
from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.models.concept import (
    Concept,
    ConceptValue,
    CORE_CONCEPTS,
    get_preflabel_from_valueid,
)
from arches.app.search.search_engine_factory import SearchEngineInstance as se
from arches.app.search.elasticsearch_dsl_builder import (
    Bool,
    Match,
    Query,
    Nested,
    Terms,
    GeoShape,
    Range,
    SimpleQueryString,
)
from arches.app.search.mappings import CONCEPTS_INDEX
from arches.app.utils.decorators import group_required
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.response import JSONResponse, JSONErrorResponse
from arches.app.utils.skos import SKOSWriter, SKOSReader
from arches.app.views.base import BaseManagerView


@method_decorator(group_required("RDM Administrator"), name="dispatch")
class RDMView(BaseManagerView):
    def get(self, request, conceptid):
        lang = request.GET.get("lang", request.LANGUAGE_CODE)

        languages = sort_languages(models.Language.objects.all(), lang)

        concept_schemes = []
        for concept in models.Concept.objects.filter(nodetype="ConceptScheme"):
            concept_schemes.append(
                Concept().get(id=concept.pk, include=["label"]).get_preflabel(lang=lang)
            )

        collections = []
        for concept in models.Concept.objects.filter(nodetype="Collection"):
            collections.append(
                Concept().get(id=concept.pk, include=["label"]).get_preflabel(lang=lang)
            )

        context = self.get_context_data(
            main_script="rdm",
            active_page="RDM",
            languages=languages,
            conceptid=conceptid,
            concept_schemes=concept_schemes,
            collections=collections,
            CORE_CONCEPTS=CORE_CONCEPTS,
        )

        context["nav"]["icon"] = "fa fa-align-left"
        context["nav"]["title"] = _("Reference Data Manager")
        context["nav"]["help"] = {
            "title": _("Using the RDM"),
            "templates": ["rdm-help"],
        }

        return render(request, "rdm.htm", context)


def get_sparql_providers(endpoint=None):
    sparql_providers = {}
    for provider in settings.SPARQL_ENDPOINT_PROVIDERS:
        provider_class = provider["SPARQL_ENDPOINT_PROVIDER"][settings.LANGUAGE_CODE][
            "value"
        ]
        Provider = import_string(provider_class)()
        sparql_providers[Provider.endpoint] = Provider

    if endpoint:
        return sparql_providers[endpoint]
    else:
        return sparql_providers


def sort_languages(languages, lang):
    """
    Sorts languages from the d_languages model by name. If there is more than one
    default language or no default language, the default language is defined by lang
    """

    if len([l for l in languages if l.isdefault == True]) != 1:
        for l in languages:
            if l.code == lang:
                l.isdefault = True
            else:
                l.isdefault = False

    return sorted(languages, key=lambda x: x.name)


@group_required("RDM Administrator")
def concept(request, conceptid):
    f = request.GET.get("f", "json")
    mode = request.GET.get("mode", "")
    lang = request.GET.get("lang", request.LANGUAGE_CODE)
    pretty = request.GET.get("pretty", False)

    if request.method == "GET":
        include_subconcepts = request.GET.get("include_subconcepts", "true") == "true"
        include_parentconcepts = (
            request.GET.get("include_parentconcepts", "true") == "true"
        )
        include_relatedconcepts = (
            request.GET.get("include_relatedconcepts", "true") == "true"
        )
        emulate_elastic_search = (
            request.GET.get("emulate_elastic_search", "false") == "true"
        )
        depth_limit = request.GET.get("depth_limit", None)

        depth_limit = 1
        if not conceptid:
            return render(
                request,
                "views/rdm/concept-report.htm",
                {
                    "lang": lang,
                    "concept_count": models.Concept.objects.filter(
                        nodetype="Concept"
                    ).count(),
                    "collection_count": models.Concept.objects.filter(
                        nodetype="Collection"
                    ).count(),
                    "scheme_count": models.Concept.objects.filter(
                        nodetype="ConceptScheme"
                    ).count(),
                    "entitytype_count": models.Concept.objects.filter(
                        nodetype="EntityType"
                    ).count(),
                    "default_report": True,
                },
            )

        labels = []

        concept_graph = Concept().get(
            id=conceptid,
            include_subconcepts=include_subconcepts,
            include_parentconcepts=include_parentconcepts,
            include_relatedconcepts=include_relatedconcepts,
            depth_limit=depth_limit,
            up_depth_limit=None,
            lang=lang,
            semantic=(mode == "semantic" or mode == ""),
        )

        languages = sort_languages(models.Language.objects.all(), lang)

        valuetypes = models.DValueType.objects.all()
        relationtypes = models.DRelationType.objects.all()
        prefLabel = concept_graph.get_preflabel(lang=lang)
        for subconcept in concept_graph.subconcepts:
            subconcept.prefLabel = subconcept.get_preflabel(lang=lang)
        for relatedconcept in concept_graph.relatedconcepts:
            relatedconcept.prefLabel = relatedconcept.get_preflabel(lang=lang)
        for value in concept_graph.values:
            if value.category == "label":
                labels.append(value)
            if value.type == "image":
                value.full_image_url = (
                    (
                        settings.FORCE_SCRIPT_NAME
                        if settings.FORCE_SCRIPT_NAME is not None
                        else ""
                    )
                    + settings.MEDIA_URL
                    + value.value
                ).replace("//", "/")

        if (mode == "semantic" or mode == "") and (
            concept_graph.nodetype == "Concept"
            or concept_graph.nodetype == "ConceptScheme"
            or concept_graph.nodetype == "EntityType"
        ):
            if concept_graph.nodetype == "ConceptScheme":
                parent_relations = relationtypes.filter(category="Properties")
            else:
                parent_relations = (
                    relationtypes.filter(category="Semantic Relations")
                    .exclude(relationtype="related")
                    .exclude(relationtype="broader")
                    .exclude(relationtype="broaderTransitive")
                )
            return render(
                request,
                "views/rdm/concept-report.htm",
                {
                    "FORCE_SCRIPT_NAME": settings.FORCE_SCRIPT_NAME,
                    "lang": lang,
                    "prefLabel": prefLabel,
                    "labels": labels,
                    "concept": concept_graph,
                    "languages": languages,
                    "sparql_providers": get_sparql_providers(),
                    "valuetype_labels": valuetypes.filter(category="label"),
                    "valuetype_notes": valuetypes.filter(category="note"),
                    "valuetype_related_values": valuetypes.filter(
                        category__in=["undefined", "identifiers"]
                    ),
                    "parent_relations": parent_relations,
                    "related_relations": relationtypes.filter(
                        Q(category="Mapping Properties") | Q(relationtype="related")
                    ),
                    "concept_paths": concept_graph.get_paths(lang=lang),
                    "graph_json": JSONSerializer().serialize(
                        concept_graph.get_node_and_links(lang=lang)
                    ),
                    "direct_parents": [
                        parent.get_preflabel(lang=lang)
                        for parent in concept_graph.parentconcepts
                    ],
                },
            )
        elif mode == "collections":
            return render(
                request,
                "views/rdm/entitytype-report.htm",
                {
                    "lang": lang,
                    "prefLabel": prefLabel,
                    "labels": labels,
                    "concept": concept_graph,
                    "languages": languages,
                    "valuetype_labels": valuetypes.filter(category="label"),
                    "valuetype_notes": valuetypes.filter(category="note"),
                    "valuetype_related_values": valuetypes.filter(
                        category__in=["undefined", "identifiers"]
                    ),
                    "related_relations": relationtypes.filter(relationtype="member"),
                    "concept_paths": concept_graph.get_paths(lang=lang),
                },
            )

    if request.method == "POST":

        if len(request.FILES) > 0:
            skosfile = request.FILES.get("skosfile", None)
            imagefile = request.FILES.get("file", None)

            if imagefile:
                value = models.FileValue(
                    valueid=str(uuid.uuid4()),
                    value=request.FILES.get("file", None),
                    concept_id=conceptid,
                    valuetype_id="image",
                    language_id=lang,
                )
                value.save()
                return JSONResponse(value)

            elif skosfile:
                overwrite_options = request.POST.get("overwrite_options", None)
                staging_options = request.POST.get("staging_options", None)
                skos = SKOSReader()
                try:
                    rdf = skos.read_file(skosfile)
                    ret = skos.save_concepts_from_skos(
                        rdf, overwrite_options, staging_options
                    )
                    return JSONResponse(ret)
                except Exception as e:
                    return JSONErrorResponse(
                        _("Unable to Load SKOS File"),
                        _(
                            "There was an issue saving the contents of the file to Arches. "
                        )
                        + str(e),
                    )

        else:
            data = JSONDeserializer().deserialize(request.body)
            if data:
                with transaction.atomic():
                    concept = Concept(data)
                    concept.save()
                    concept.index()

                    return JSONResponse(concept)

    if request.method == "DELETE":
        data = JSONDeserializer().deserialize(request.body)
        if data:
            with transaction.atomic():
                concept = Concept(data)
                delete_self = data["delete_self"] if "delete_self" in data else False
                if not (delete_self and concept.id in CORE_CONCEPTS):
                    if concept.nodetype == "Collection":
                        concept.delete(delete_self=delete_self)
                    else:
                        in_use = False
                        if delete_self:
                            check_concept = Concept().get(
                                data["id"], include_subconcepts=True
                            )
                            in_use = check_concept.check_if_concept_in_use()
                        if "subconcepts" in data:
                            for subconcept in data["subconcepts"]:
                                if in_use == False:
                                    check_concept = Concept().get(
                                        subconcept["id"], include_subconcepts=True
                                    )
                                    in_use = check_concept.check_if_concept_in_use()

                        if in_use == False:
                            concept.delete_index(delete_self=delete_self)
                            concept.delete(delete_self=delete_self)
                        else:
                            return JSONErrorResponse(
                                _("Unable to Delete"),
                                _(
                                    "This concept or one of it's subconcepts is already in use by an existing resource."
                                ),
                                {"in_use": in_use},
                            )

                return JSONResponse(concept)

    return HttpResponseNotFound()


def export(request, conceptid):
    concept_graphs = [
        Concept().get(
            id=conceptid,
            include_subconcepts=True,
            include_parentconcepts=False,
            include_relatedconcepts=True,
            depth_limit=None,
            up_depth_limit=None,
        )
    ]

    skos = SKOSWriter()
    return HttpResponse(
        skos.write(concept_graphs, format="pretty-xml"), content_type="application/xml"
    )


def export_collections(request):
    concept_graphs = []
    for concept in models.Concept.objects.filter(nodetype_id="Collection"):
        concept_graphs.append(
            Concept().get(
                id=concept.pk,
                include_subconcepts=True,
                include_parentconcepts=False,
                include_relatedconcepts=False,
                depth_limit=None,
                up_depth_limit=None,
                semantic=False,
            )
        )

    skos = SKOSWriter()
    return HttpResponse(
        skos.write(concept_graphs, format="pretty-xml"), content_type="application/xml"
    )


def get_concept_collections(request):
    lang = request.GET.get("lang", request.LANGUAGE_CODE)
    concept_collections = Concept().concept_tree(mode="collections", lang=lang)
    return JSONResponse(concept_collections)


@group_required("RDM Administrator")
def make_collection(request, conceptid):
    concept = Concept().get(id=conceptid, values=[])
    try:
        collection_concept = concept.make_collection()
        return JSONResponse(
            {
                "collection": collection_concept,
                "title": _("Success"),
                "message": _(
                    "Collection successfully created from the selected concept"
                ),
            }
        )
    except:
        return JSONErrorResponse(
            _("Unable to Make Collection"),
            _("Unable to make a collection from the selected concept."),
        )


@group_required("RDM Administrator")
def manage_parents(request, conceptid):
    if request.method == "POST":
        json = request.body
        if json is not None:
            data = JSONDeserializer().deserialize(json)

            with transaction.atomic():
                if len(data["deleted"]) > 0:
                    concept = Concept().get(id=conceptid, include=None)
                    for deleted in data["deleted"]:
                        concept.addparent(deleted)

                    concept.delete()
                    concept.bulk_index()

                if len(data["added"]) > 0:
                    concept = Concept().get(id=conceptid)
                    for added in data["added"]:
                        concept.addparent(added)

                    concept.save()
                    concept.bulk_index()

            return JSONResponse(data)

    else:
        return HttpResponseNotAllowed(["POST"])

    return HttpResponseNotFound()


def confirm_delete(request, conceptid):
    lang = request.GET.get("lang", request.LANGUAGE_CODE)
    concept = Concept().get(id=conceptid)
    concepts_to_delete = [
        concept.get_preflabel(lang=lang).value
        for key, concept in Concept.gather_concepts_to_delete(
            concept, lang=lang
        ).items()
    ]
    # return HttpResponse('<div>Showing only 50 of
    # %s concepts</div><ul><li>%s</ul>' % (len(concepts_to_delete), '<li>'.join(concepts_to_delete[:50]) + ''))
    return HttpResponse("<ul><li>%s</ul>" % ("<li>".join(concepts_to_delete) + ""))


def dropdown(request):
    conceptid = request.GET.get("conceptid")
    results = Concept().get_e55_domain(conceptid)
    return JSONResponse(results)


def paged_dropdown(request):
    conceptid = request.GET.get("conceptid")
    query = request.GET.get("query", "")
    page = int(request.GET.get("page", 1))
    lang = request.GET.get("lang", None)
    limit = 50
    offset = (page - 1) * limit

    results = Concept().get_child_collections_hierarchically(
        conceptid, offset=offset, limit=limit, query=query, languageid=lang
    )
    total_count = results[0][3] if len(results) > 0 else 0
    data = [dict(list(zip(["valueto", "depth", "collector"], d))) for d in results]
    data = [
        dict(
            list(
                zip(
                    ["id", "text", "conceptid", "language", "type"],
                    d["valueto"].values(),
                )
            ),
            depth=d["depth"],
            collector=d["collector"],
        )
        for d in data
    ]

    return JSONResponse({"results": data, "more": offset + limit < total_count})


def get_pref_label(request):
    valueid = request.GET.get("valueid")
    label = get_preflabel_from_valueid(valueid, request.LANGUAGE_CODE)
    return JSONResponse(label)


def search(request):
    searchString = request.GET["q"]
    removechildren = request.GET.get("removechildren", None)
    query = Query(se, start=0, limit=100)
    phrase = Match(
        field="value.folded", query=searchString.lower(), type="phrase_prefix"
    )
    query.add_query(phrase)
    results = query.search(index=CONCEPTS_INDEX)

    ids = []
    if removechildren is not None:
        ids = [
            concept[0]
            for concept in Concept().get_child_concepts(
                removechildren, columns="conceptidto::text"
            )
        ]
        ids.append(removechildren)

    newresults = []
    cached_scheme_names = {}
    for result in results["hits"]["hits"]:
        if result["_source"]["conceptid"] not in ids:
            # first look to see if we've already retrieved the top concept name
            # else look up the top concept name with ES and cache the result
            top_concept = result["_source"]["top_concept"]
            if top_concept in cached_scheme_names:
                result["in_scheme_name"] = cached_scheme_names[top_concept]
            else:
                query = Query(se, start=0, limit=100)
                phrase = Match(field="conceptid", query=top_concept, type="phrase")
                query.add_query(phrase)
                scheme = query.search(index=CONCEPTS_INDEX)
                for label in scheme["hits"]["hits"]:
                    if label["_source"]["type"] == "prefLabel":
                        cached_scheme_names[top_concept] = label["_source"]["value"]
                        result["in_scheme_name"] = label["_source"]["value"]

            newresults.append(result)

    # Use the db to get the concept context but this is SLOW
    # for result in results['hits']['hits']:
    #     if result['_source']['conceptid'] not in ids:
    #         concept = Concept().get(id=result['_source']['conceptid'], include_parentconcepts=True)
    #         pathlist = concept.get_paths()
    #         result['in_scheme_name'] = pathlist[0][0]['label']
    #         newresults.append(result)

    # def crawl(conceptid, path=[]):
    #     query = Query(se, start=0, limit=100)
    #     bool = Bool()
    #     bool.must(Match(field='conceptto', query=conceptid, type='phrase'))
    #     bool.must(Match(field='relationtype', query='narrower', type='phrase'))
    #     query.add_query(bool)
    #     relations = query.search(index='concept_relations')
    #     for relation in relations['hits']['hits']:
    #         path.insert(0, relation)
    #         crawl(relation['_source']['conceptfrom'], path=path)
    #     return path

    # for result in results['hits']['hits']:
    #     if result['_source']['conceptid'] not in ids:
    #         concept_relations = crawl(result['_source']['conceptid'], path=[])
    #         if len(concept_relations) > 0:
    #             conceptid = concept_relations[0]['_source']['conceptfrom']
    #             if conceptid in cached_scheme_names:
    #                 result['in_scheme_name'] = cached_scheme_names[conceptid]
    #             else:
    #                 result['in_scheme_name'] = get_preflabel_from_conceptid(conceptid, lang=request.LANGUAGE_CODE)['value']
    #                 cached_scheme_names[conceptid] = result['in_scheme_name']

    #         newresults.append(result)

    results["hits"]["hits"] = newresults
    return JSONResponse(results)


def add_concepts_from_sparql_endpoint(request, conceptid):
    if request.method == "POST":
        json = request.body
        if json is not None:
            data = JSONDeserializer().deserialize(json)

            parentconcept = Concept(
                {"id": conceptid, "nodetype": data["model"]["nodetype"]}
            )

            if parentconcept.nodetype == "Concept":
                relationshiptype = "narrower"
            elif parentconcept.nodetype == "ConceptScheme":
                relationshiptype = "hasTopConcept"

            provider = get_sparql_providers(data["endpoint"])
            try:
                parentconcept.subconcepts = provider.get_concepts(data["ids"])
            except Exception as e:
                return HttpResponseServerError(e.message)

            for subconcept in parentconcept.subconcepts:
                subconcept.relationshiptype = relationshiptype

            parentconcept.save()
            parentconcept.index()

            return JSONResponse(parentconcept, indent=4)

    else:
        return HttpResponseNotAllowed(["POST"])

    return HttpResponseNotFound()


def search_sparql_endpoint_for_concepts(request):
    provider = get_sparql_providers(request.GET.get("endpoint"))
    results = provider.search_for_concepts(request.GET.get("terms"))
    return JSONResponse(results)


def concept_tree(request, mode):
    lang = request.GET.get("lang", request.LANGUAGE_CODE)
    conceptid = request.GET.get("node", None)
    concepts = Concept({"id": conceptid}).concept_tree(lang=lang, mode=mode)
    return JSONResponse(concepts, indent=4)


def concept_value(request):
    if request.method == "DELETE":
        data = JSONDeserializer().deserialize(request.body)

        if data:
            with transaction.atomic():
                value = ConceptValue(data)
                value.delete_index()
                value.delete()
                return JSONResponse(value)
    if request.method == "GET":
        valueid = request.GET.get("valueid")
        value = models.Value.objects.get(pk=valueid)
        return JSONResponse(value)

    return HttpResponseNotFound()
