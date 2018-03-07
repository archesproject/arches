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
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseNotAllowed, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import permission_required
from arches.app.models import models
from arches.app.models.concept import Concept, ConceptValue, CORE_CONCEPTS
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Nested, Terms, GeoShape, Range, SimpleQueryString
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.utils.skos import SKOSWriter, SKOSReader
from django.utils.module_loading import import_by_path


sparql_providers = {}
for provider in settings.SPARQL_ENDPOINT_PROVIDERS:
    Provider = import_by_path(provider)()
    sparql_providers[Provider.endpoint] = Provider

@permission_required('edit')
def rdm(request, conceptid):
    lang = request.GET.get('lang', request.LANGUAGE_CODE)    
    languages = models.DLanguages.objects.all()

    concept_schemes = []
    for concept in models.Concepts.objects.filter(nodetype = 'ConceptScheme'):
        concept_schemes.append(Concept().get(id=concept.pk, include=['label']).get_preflabel(lang=lang))

    return render_to_response('rdm.htm', {
            'main_script': 'rdm',
            'active_page': 'RDM',
            'languages': languages,
            'conceptid': conceptid,
            'concept_schemes': concept_schemes,
            'CORE_CONCEPTS': CORE_CONCEPTS
        }, context_instance=RequestContext(request))



@permission_required('edit')
@csrf_exempt
def concept(request, conceptid):
    f = request.GET.get('f', 'json')
    mode = request.GET.get('mode', '')
    lang = request.GET.get('lang', request.LANGUAGE_CODE)
    pretty = request.GET.get('pretty', False)

    if request.method == 'GET':

        include_subconcepts = request.GET.get('include_subconcepts', 'true') == 'true'
        include_parentconcepts = request.GET.get('include_parentconcepts', 'true') == 'true'
        include_relatedconcepts = request.GET.get('include_relatedconcepts', 'true') == 'true'
        emulate_elastic_search = request.GET.get('emulate_elastic_search', 'false') == 'true'
        depth_limit = request.GET.get('depth_limit', None)

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

        ret = []
        labels = []
        this_concept = Concept().get(id=conceptid)

        if f == 'html':
            if mode == '' and (this_concept.nodetype == 'Concept' or this_concept.nodetype == 'ConceptScheme' or this_concept.nodetype == 'EntityType'):
                concept_graph = Concept().get(id=conceptid, include_subconcepts=include_subconcepts, 
                    include_parentconcepts=include_parentconcepts, include_relatedconcepts=include_relatedconcepts,
                    depth_limit=depth_limit, up_depth_limit=None, lang=lang)
            else:
                concept_graph = Concept().get(id=conceptid, include_subconcepts=include_subconcepts, 
                    include_parentconcepts=include_parentconcepts, include_relatedconcepts=include_relatedconcepts,
                    depth_limit=depth_limit, up_depth_limit=None, lang=lang, semantic=False)
            
            languages = models.DLanguages.objects.all()
            valuetypes = models.ValueTypes.objects.all()
            relationtypes = models.DRelationtypes.objects.all()
            prefLabel = concept_graph.get_preflabel(lang=lang)
            for subconcept in concept_graph.subconcepts:
                subconcept.prefLabel = subconcept.get_preflabel(lang=lang) 
            for relatedconcept in concept_graph.relatedconcepts:
                relatedconcept.prefLabel = relatedconcept.get_preflabel(lang=lang) 
            for value in concept_graph.values:
                if value.category == 'label':
                    labels.append(value)

            if mode == '' and (this_concept.nodetype == 'Concept' or this_concept.nodetype == 'ConceptScheme' or this_concept.nodetype == 'EntityType'):
                if concept_graph.nodetype == 'ConceptScheme':
                    parent_relations = relationtypes.filter(category='Properties')
                else:
                    parent_relations = relationtypes.filter(category='Semantic Relations').exclude(relationtype = 'related').exclude(relationtype='broader').exclude(relationtype='broaderTransitive')
                return render_to_response('views/rdm/concept-report.htm', {
                    'lang': lang,
                    'prefLabel': prefLabel,
                    'labels': labels,
                    'concept': concept_graph,
                    'languages': languages,
                    'sparql_providers': sparql_providers,
                    'valuetype_labels': valuetypes.filter(category='label'),
                    'valuetype_notes': valuetypes.filter(category='note'),
                    'valuetype_related_values': valuetypes.filter(category='undefined'),
                    'parent_relations': parent_relations,
                    'related_relations': relationtypes.filter(Q(category='Mapping Properties') | Q(relationtype = 'related')),
                    'concept_paths': concept_graph.get_paths(lang=lang),
                    'graph_json': JSONSerializer().serialize(concept_graph.get_node_and_links(lang=lang)),
                    'direct_parents': [parent.get_preflabel(lang=lang) for parent in concept_graph.parentconcepts]
                }, context_instance=RequestContext(request))
            else:
                return render_to_response('views/rdm/entitytype-report.htm', {
                    'lang': lang,
                    'prefLabel': prefLabel,
                    'labels': labels,
                    'concept': concept_graph,
                    'languages': languages,
                    'valuetype_labels': valuetypes.filter(category='label'),
                    'valuetype_notes': valuetypes.filter(category='note'),
                    'valuetype_related_values': valuetypes.filter(category='undefined'),
                    'related_relations': relationtypes.filter(relationtype = 'member'),
                    'concept_paths': concept_graph.get_paths(lang=lang)
                }, context_instance=RequestContext(request))


        concept_graph = Concept().get(id=conceptid, include_subconcepts=include_subconcepts, 
                include_parentconcepts=include_parentconcepts, include_relatedconcepts=include_relatedconcepts,
                depth_limit=depth_limit, up_depth_limit=None, lang=lang)

        if f == 'skos':
            include_parentconcepts = False
            include_subconcepts = True
            depth_limit = None
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
                value = models.FileValues(valueid = str(uuid.uuid4()), value = request.FILES.get('file', None), conceptid_id = conceptid, valuetype_id = 'image',languageid_id = request.LANGUAGE_CODE)
                value.save()
                return JSONResponse(value)

            elif skosfile:
                skos = SKOSReader()
                rdf = skos.read_file(skosfile)
                ret = skos.save_concepts_from_skos(rdf)
                return JSONResponse(ret)
            
        else:
            data = JSONDeserializer().deserialize(request.body) 
            if data:
                with transaction.atomic():
                    concept = Concept(data)
                    concept.save()
                    concept.index()

                    return JSONResponse(concept)


    if request.method == 'DELETE':
        data = JSONDeserializer().deserialize(request.body) 

        if data:
            with transaction.atomic():

                concept = Concept(data)

                delete_self = data['delete_self'] if 'delete_self' in data else False  
                if not (delete_self and concept.id in CORE_CONCEPTS):
                    in_use = False
                    if delete_self:
                        check_concept = Concept().get(data['id'], include_subconcepts=True)
                        in_use = check_concept.check_if_concept_in_use()
                    if 'subconcepts' in data:
                        for subconcept in data['subconcepts']:
                            if in_use == False:
                                check_concept = Concept().get(subconcept['id'], include_subconcepts=True)
                                in_use = check_concept.check_if_concept_in_use()

                    if in_use == False:
                        concept.delete_index(delete_self=delete_self)
                        concept.delete(delete_self=delete_self)
                    else:
                        return JSONResponse({"in_use": in_use})
                        
                return JSONResponse(concept)

    return HttpResponseNotFound

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
        return HttpResponseNotAllowed(['POST'])

    return HttpResponseNotFound()

@csrf_exempt
def confirm_delete(request, conceptid):
    lang = request.GET.get('lang', request.LANGUAGE_CODE) 
    concept = Concept().get(id=conceptid)
    concepts_to_delete = [concept.get_preflabel(lang=lang).value for key, concept in Concept.gather_concepts_to_delete(concept, lang=lang).iteritems()]
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
    #     bool.must(Match(field='conceptidto', query=conceptid, type='phrase'))
    #     bool.must(Match(field='relationtype', query='narrower', type='phrase'))
    #     query.add_query(bool)
    #     relations = query.search(index='concept_relations')
    #     for relation in relations['hits']['hits']:
    #         path.insert(0, relation)
    #         crawl(relation['_source']['conceptidfrom'], path=path)
    #     return path

    # for result in results['hits']['hits']:
    #     if result['_source']['conceptid'] not in ids:
    #         concept_relations = crawl(result['_source']['conceptid'], path=[])
    #         if len(concept_relations) > 0:
    #             conceptid = concept_relations[0]['_source']['conceptidfrom']
    #             if conceptid in cached_scheme_names:
    #                 result['in_scheme_name'] = cached_scheme_names[conceptid]
    #             else:
    #                 result['in_scheme_name'] = get_preflabel_from_conceptid(conceptid, lang=request.LANGUAGE_CODE)['value']             
    #                 cached_scheme_names[conceptid] = result['in_scheme_name'] 

    #         newresults.append(result)

    results['hits']['hits'] = newresults
    return JSONResponse(results)

@csrf_exempt
def add_concepts_from_sparql_endpoint(request, conceptid):
    if request.method == 'POST':
        json = request.body
        if json != None:
            data = JSONDeserializer().deserialize(json)

            parentconcept = Concept({
                'id': conceptid,
                'nodetype': data['model']['nodetype']
            }) 

            if parentconcept.nodetype == 'Concept':
                relationshiptype = 'narrower'
            elif parentconcept.nodetype == 'ConceptScheme':
                relationshiptype = 'hasTopConcept' 

            provider = sparql_providers[data['endpoint']]
            try:
                parentconcept.subconcepts = provider.get_concepts(data['ids'])
            except Exception as e:
                return HttpResponseServerError(e.message)

            for subconcept in parentconcept.subconcepts:
                subconcept.relationshiptype = relationshiptype
        
            parentconcept.save()
            parentconcept.index()

            return JSONResponse(parentconcept, indent=4)

    else:
        return HttpResponseNotAllowed(['POST'])

    return HttpResponseNotFound()

def search_sparql_endpoint_for_concepts(request):
    provider = sparql_providers[request.GET.get('endpoint')]
    results = provider.search_for_concepts(request.GET.get('terms'))
    return JSONResponse(results)

def concept_tree(request):
    lang = request.GET.get('lang', request.LANGUAGE_CODE) 
    conceptid = request.GET.get('node', None)
    concepts = Concept({'id': conceptid}).concept_tree(lang=lang)
    return JSONResponse(concepts, indent=4)

def get_preflabel_from_valueid(valueid, lang):

    se = SearchEngineFactory().create()
    concept_label = se.search(index='concept_labels', id=valueid)
    if concept_label['found']:
#         print "ConceptID from ValueID: %s" % get_concept_label_from_valueid(valueid)
        return get_preflabel_from_conceptid(get_concept_label_from_valueid(valueid)['conceptid'], lang)

        
def get_concept_label_from_valueid(valueid):
    se = SearchEngineFactory().create()
    concept_label = se.search(index='concept_labels', id=valueid)
    if concept_label['found']:
        return concept_label['_source']

def get_preflabel_from_conceptid(conceptid, lang):
    ret = None
    default = {
        "category": "",
        "conceptid": "",
        "language": "",
        "value": "",
        "type": "",
        "id": ""
    }
    se = SearchEngineFactory().create()
    query = Query(se)
    terms = Terms(field='conceptid', terms=[conceptid])
    # Uncomment the following line only after having reindexed ElasticSearch cause currently the Arabic labels are indexed as altLabels
#     match = Match(field='type', query='prefLabel', type='phrase')
    query.add_filter(terms)
    # Uncomment the following line only after having reindexed ElasticSearch cause currently the Arabic labels are indexed as altLabels
#     query.add_query(match)

    preflabels = query.search(index='concept_labels')['hits']['hits'] 
    for preflabel in preflabels:
#         print 'Language at this point %s and label language %s and ret is %s' % (lang, preflabel['_source']['language'], ret)
        default = preflabel['_source']
        # get the label in the preferred language, otherwise get the label in the default language
        if preflabel['_source']['language'] == lang:
#             print 'prefLabel from Conceptid: %s' % preflabel['_source']
            return preflabel['_source']
        if preflabel['_source']['language'].split('-')[0] == lang.split('-')[0]:
            ret = preflabel['_source']
        if preflabel['_source']['language'] == lang and ret == None:
            ret = preflabel['_source']
    return default if ret == None else ret

