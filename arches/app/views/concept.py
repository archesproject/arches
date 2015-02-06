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
from django.conf import settings
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from arches.app.models import models
from arches.app.models.concept import Concept, ConceptValue, CORE_CONCEPTS
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Nested, Terms, GeoShape, Range, SimpleQueryString
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.utils.skos import SKOSWriter, SKOSReader

@login_required
def rdm(request, conceptid):
    lang = request.GET.get('lang', 'en-us')    
    
    languages = models.DLanguages.objects.all()

    concept_scheme_groups = []
    for concept in models.Concepts.objects.filter(nodetype = 'ConceptSchemeGroup'):
        concept_scheme_groups.append(Concept().get(id=concept.pk, include=['label']).get_preflabel(lang=lang))

    concept_schemes = []
    for concept in models.Concepts.objects.filter(nodetype = 'ConceptScheme'):
        scheme = Concept().get(id=concept.pk, include_parentconcepts=True, up_depth_limit=1, include=['label'])
        group = []
        for parent in scheme.parentconcepts:
            if parent.nodetype == 'ConceptSchemeGroup':
                group.append(parent.get_preflabel(lang=lang).value)
        concept_schemes.append({'scheme': scheme.get_preflabel(lang=lang), 'group': ','.join(group)})

    return render_to_response('rdm.htm', {
            'main_script': 'rdm',
            'active_page': 'RDM',
            'languages': languages,
            'conceptid': conceptid,
            'concept_schemes': concept_schemes,
            'concept_scheme_groups': concept_scheme_groups
        }, context_instance=RequestContext(request))

@login_required
@csrf_exempt
def concept(request, conceptid):
    f = request.GET.get('f', 'json')
    lang = request.GET.get('lang', 'en-us')
    pretty = request.GET.get('pretty', False)

    if request.method == 'GET':

        include_subconcepts = request.GET.get('include_subconcepts', 'true') == 'true'
        include_parentconcepts = request.GET.get('include_parentconcepts', 'true') == 'true'
        include_relatedconcepts = request.GET.get('include_relatedconcepts', 'true') == 'true'
        emulate_elastic_search = request.GET.get('emulate_elastic_search', 'false') == 'true'
        depth_limit = request.GET.get('depth_limit', None)
        mode = request.GET.get('mode', 'scheme')

        if f == 'html':
            depth_limit = 1
            if not conceptid:
                return render_to_response('views/rdm/concept-report.htm', {
                    'lang': lang,
                    'concept_count': models.Concepts.objects.filter(nodetype='Concept').count(),
                    'collection_count': models.Concepts.objects.filter(nodetype='Collection').count(),
                    'scheme_count': models.Concepts.objects.filter(nodetype='ConceptScheme').count(),
                    'entitytype_count': models.Concepts.objects.filter(nodetype='EntityType').count(),
                    'default_report': True
                }, context_instance=RequestContext(request))

        if f == 'skos':
            include_parentconcepts = False
            include_subconcepts = True
            depth_limit = None

        ret = []
        labels = []
        concept_graph = Concept().get(id=conceptid, include_subconcepts=include_subconcepts, 
            include_parentconcepts=include_parentconcepts, include_relatedconcepts=include_relatedconcepts,
            depth_limit=depth_limit, up_depth_limit=None, lang=lang)

        if f == 'html':
            if concept_graph.nodetype == 'Concept' or concept_graph.nodetype == 'ConceptSchemeGroup' or concept_graph.nodetype == 'ConceptScheme' or concept_graph.nodetype == 'EntityType':
                languages = models.DLanguages.objects.all()
                valuetypes = models.ValueTypes.objects.all()
                relationtypes = models.DRelationtypes.objects.all()
                prefLabel = concept_graph.get_preflabel(lang=lang).value
                for subconcept in concept_graph.subconcepts:
                    subconcept.prefLabel = subconcept.get_preflabel(lang=lang) 
                for relatedconcept in concept_graph.relatedconcepts:
                    relatedconcept.prefLabel = relatedconcept.get_preflabel(lang=lang) 
                for value in concept_graph.values:
                    if value.category == 'label':
                        labels.append(value)
                direct_parents = [parent.get_preflabel(lang=lang) for parent in concept_graph.parentconcepts]
                return render_to_response('views/rdm/concept-report.htm', {
                    'lang': lang,
                    'prefLabel': prefLabel,
                    'labels': labels,
                    'concept': concept_graph,
                    'languages': languages,
                    'valuetype_labels': valuetypes.filter(category='label'),
                    'valuetype_notes': valuetypes.filter(category='note'),
                    'valuetype_related_values': valuetypes.filter(category='undefined'),
                    'parent_relations': relationtypes.filter(category='Semantic Relations').exclude(relationtype = 'related').exclude(relationtype='broader').exclude(relationtype='broaderTransitive'),
                    'related_relations': relationtypes.filter(Q(category='Mapping Properties') | Q(relationtype = 'related')),
                    'concept_paths': concept_graph.get_paths(lang=lang),
                    'graph_json': JSONSerializer().serialize(concept_graph.get_node_and_links(lang=lang)),
                    'direct_parents': direct_parents,
                    'in_scheme_id': concept_graph.get_context()
                }, context_instance=RequestContext(request))

            else:
                languages = models.DLanguages.objects.all()
                valuetypes = models.ValueTypes.objects.all()
                relationtypes = models.DRelationtypes.objects.filter(relationtype = 'member')
                prefLabel = concept_graph.get_preflabel(lang=lang).value
                for value in concept_graph.values:
                    if value.category == 'label':
                        labels.append(value)
                direct_parents = [parent.get_preflabel(lang=lang) for parent in concept_graph.parentconcepts]
                return render_to_response('views/rdm/entitytype-report.htm', {
                    'lang': lang,
                    'prefLabel': prefLabel,
                    'labels': labels,
                    'concept': concept_graph,
                    'languages': languages,
                    'valuetype_labels': valuetypes.filter(category='label'),
                    'valuetype_notes': valuetypes.filter(category='note'),
                    'valuetype_related_values': valuetypes.filter(category='undefined'),
                    'parent_relations': relationtypes.filter(category='Semantic Relations').exclude(relationtype='related'),
                    'related_relations': relationtypes.filter(relationtype = 'member'),
                    'concept_paths': concept_graph.get_paths(lang=lang),
                    'graph_json': JSONSerializer().serialize(concept_graph.get_node_and_links(lang=lang)),
                    'direct_parents': direct_parents
                }, context_instance=RequestContext(request))

        if f == 'skos':
            skos = SKOSWriter()
            return HttpResponse(skos.write(concept_graph, format="pretty-xml"), content_type="application/xml")

        if emulate_elastic_search:
            ret.append({'_type': id, '_source': concept_graph})
        else:
            ret.append(concept_graph)       

        if emulate_elastic_search:
            ret = {'hits':{'hits':ret}} 

        return JSONResponse(ret, indent=4 if pretty else None)   

    if request.method == 'POST': 

        if len(request.FILES) > 0:
            skosfile = request.FILES.get('skosfile', None)
            imagefile = request.FILES.get('file', None)

            if imagefile:
                value = models.FileValues(valueid = str(uuid.uuid4()), value = request.FILES.get('file', None), conceptid_id = conceptid, valuetype_id = 'image', datatype = 'text', languageid_id = 'en-us')
                value.save()
                return JSONResponse(value)

            elif skosfile:
                data = JSONDeserializer().deserialize(request.POST.get('data', None))
                if data:
                    concept = Concept(data)
                    concept.save()
                    skos = SKOSReader()
                    rdf = skos.read_file(skosfile)
                    ret = skos.save_concepts_from_skos(rdf, concept_scheme_group=concept.id)
                    return JSONResponse(ret)
            
        else:
            data = JSONDeserializer().deserialize(request.body) 
            if data:
                with transaction.atomic():
                    concept = Concept(data)
                    concept.save()

                    if conceptid not in CORE_CONCEPTS:
                        concept.index()

                    return JSONResponse(concept)


    if request.method == 'DELETE':
        data = JSONDeserializer().deserialize(request.body) 

        if data:
            with transaction.atomic():
                concept = Concept(data)

                if concept.id not in CORE_CONCEPTS:
                    concept.delete_index()                
                concept.delete()

                return JSONResponse(concept)

    return HttpResponseNotFound()

@csrf_exempt
def manage_parents(request, conceptid):
    #  need to check user credentials here

    if request.method == 'POST':
        json = request.body
        if json != None:
            data = JSONDeserializer().deserialize(json)
            
            with transaction.atomic():
                if len(data['deleted']) > 0:
                    concept = Concept({'id':conceptid})
                    for deleted in data['deleted']:
                        concept.addparent(deleted)  
    
                    concept.delete()
                
                if len(data['added']) > 0:
                    concept = Concept({'id':conceptid})
                    for added in data['added']:
                        concept.addparent(added)   
            
                    concept.save()

                return JSONResponse(data)

    else:
        HttpResponseNotAllowed(['POST'])

    return HttpResponseNotFound()

@csrf_exempt
def confirm_delete(request, conceptid):
    lang = request.GET.get('lang', 'en-us') 
    concept = Concept().get(id=conceptid)
    concepts_to_delete = [concept.value for key, concept in Concept.gather_concepts_to_delete(concept, lang=lang).iteritems()]
    #return HttpResponse('<div>Showing only 50 of %s concepts</div><ul><li>%s</ul>' % (len(concepts_to_delete), '<li>'.join(concepts_to_delete[:50]) + ''))
    return HttpResponse('<ul><li>%s</ul>' % ('<li>'.join(concepts_to_delete) + ''))

@csrf_exempt
def search(request):
    se = SearchEngineFactory().create()
    searchString = request.GET['q']
    removechildren = request.GET.get('removechildren', None)
    query = Query(se, start=0, limit=100)
    phrase = Match(field='value', query=searchString.lower(), type='phrase_prefix')
    query.add_query(phrase)
    results = query.search(index='concept_labels')

    ids = []
    if removechildren != None:
        concepts = Concept().get(id=removechildren, include_subconcepts=True, include=None)
        print concepts
        def get_children(concept):
            ids.append(concept.id)

        concepts.traverse(get_children)

    newresults = []
    cached_scheme_names = {}
    for result in results['hits']['hits']:
        if result['_source']['conceptid'] not in ids:
            # first look to see if we've already retrieved the scheme name
            # else look up the scheme name with ES and cache the result
            if result['_type'] in cached_scheme_names:
                result['in_scheme_name'] = cached_scheme_names[result['_type']]
            else:
                query = Query(se, start=0, limit=100)
                phrase = Match(field='conceptid', query=result['_type'], type='phrase')
                query.add_query(phrase)
                scheme = query.search(index='concept_labels')
                for label in scheme['hits']['hits']:
                    if label['_source']['type'] == 'prefLabel':
                        cached_scheme_names[result['_type']] = label['_source']['value']
                        result['in_scheme_name'] = label['_source']['value']

            newresults.append(result)
        else:
            print result['_source']['value']

    results['hits']['hits'] = newresults
    return JSONResponse(results)

def concept_tree(request):
    lang = request.GET.get('lang', 'en-us') 
    conceptid = request.GET.get('node', None)
    concepts = Concept({'id': conceptid}).concept_tree(lang=lang)
    return JSONResponse(concepts, indent=4)

def get_preflabel_from_valueid(valueid, lang):
    se = SearchEngineFactory().create()
    concept_label = se.search(index='concept_labels', id=valueid)
    if concept_label['found']:
        return get_preflabel_from_conceptid(get_concept_label_from_valueid(valueid)['conceptid'], lang)

def get_concept_label_from_valueid(valueid):
    se = SearchEngineFactory().create()
    concept_label = se.search(index='concept_labels', id=valueid)
    if concept_label['found']:
        return concept_label['_source']

def get_preflabel_from_conceptid(conceptid, lang):
    ret = None
    se = SearchEngineFactory().create()
    query = Query(se)
    terms = Terms(field='conceptid', terms=[conceptid])
    match = Match(field='type', query='preflabel', type='phrase')
    query.add_filter(terms)
    query.add_query(match)
    preflabels = query.search(index='concept_labels')['hits']['hits'] 
    for preflabel in preflabels:
        # get the label in the preferred language, otherwise get the label in the default language
        if preflabel['_source']['language'] == lang:
            return preflabel['_source']
        if preflabel['_source']['language'] == settings.LANGUAGE_CODE:
            ret = preflabel['_source']
    return ret