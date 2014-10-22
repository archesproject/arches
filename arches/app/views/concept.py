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
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.shortcuts import render_to_response
import arches.app.models.models as archesmodels
from arches.app.models.concept import Concept, ConceptValue
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Bool, Match, Query, Nested, Terms, GeoShape, Range, SimpleQueryString
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.utils.skos import SKOSWriter


def rdm(request, conceptid):
    languages = archesmodels.DLanguages.objects.all()

    return render_to_response('rdm.htm', {
            'main_script': 'rdm',
            'active_page': 'RDM',
            'conceptid': conceptid
        }, context_instance=RequestContext(request))

@csrf_exempt
def concept(request, conceptid):
    ret = {'success': False}
    f = request.GET.get('f', 'json')
    lang = request.GET.get('lang', 'en-us')
    pretty = request.GET.get('pretty', False)

    if request.method == 'GET':
        include_subconcepts = request.GET.get('include_subconcepts', 'true') == 'true'
        include_parentconcepts = request.GET.get('include_parentconcepts', 'true') == 'true'
        include_relatedconcepts = request.GET.get('include_relatedconcepts', 'true') == 'true'
        emulate_elastic_search = request.GET.get('emulate_elastic_search', 'false') == 'true'
        fromdb = request.GET.get('fromdb', 'false') == 'true'
        depth_limit = request.GET.get('depth_limit', None)

        if f == 'html':
            fromdb = True
            depth_limit = 1

        if f == 'skos':
            fromdb = True

        ret = []

        if fromdb:
            concept_graph = Concept().get(id=conceptid, include_subconcepts=include_subconcepts, 
                include_parentconcepts=include_parentconcepts, include_relatedconcepts=include_relatedconcepts,
                depth_limit=depth_limit, up_depth_limit=None)
            
            nodes = [{'concept_id': concept_graph.id, 'name': concept_graph.get_preflabel(lang=lang).value,'type': 'Current'}]
            links = []
            # path = []
            # path_list = [path]

            def graph_to_paths(current_concept, path=[], path_list=[[]]):
                parents = current_concept.parentconcepts
                for i, parent in enumerate(parents):
                    current_path = path[:]
                    if len(parent.parentconcepts) == 0:
                        type = 'Root'
                        path_list.append(current_path)
                    else:
                        type = 'Ancestor'
                    nodes.append({'concept_id': parent.id, 'name': parent.get_preflabel(lang=lang).value,'type': type })
                    links.append({'target': current_concept.id, 'source': parent.id, 'relationship': 'broader' })
                    current_path.insert(0, {'label': parent.get_preflabel(lang=lang).value, 'relationshiptype': parent.relationshiptype, 'id': parent.id})
                    graph_to_paths(parent, current_path, path_list)
                return path_list

            path_list = graph_to_paths(concept_graph)
            for child in concept_graph.subconcepts:
                nodes.append({'concept_id': child.id, 'name': child.get_preflabel(lang=lang).value,'type': 'Descendant' })
                links.append({'source': concept_graph.id, 'target': child.id, 'relationship': 'narrower' })
            nodes = {node['concept_id']:node for node in nodes}.values()
            for i in range(len(nodes)):
                nodes[i]['id'] = i
                for link in links:
                    link['source'] = i if link['source'] == nodes[i]['concept_id'] else link['source']
                    link['target'] = i if link['target'] == nodes[i]['concept_id'] else link['target']
            
            graph_json = JSONSerializer().serialize({'nodes': nodes, 'links': links})

            if f == 'html':
                languages = archesmodels.DLanguages.objects.all()
                valuetypes = archesmodels.ValueTypes.objects.all()
                prefLabel = concept_graph.get_preflabel(lang=lang).value
                return render_to_response('views/rdm/concept-report.htm', {
                    'lang': lang,
                    'prefLabel': prefLabel,
                    'concept': concept_graph,
                    'languages': languages,
                    'valuetype_labels': valuetypes.filter(category='label'),
                    'valuetype_notes': valuetypes.filter(category='note'),
                    'valuetype_related_values': valuetypes.filter(category=''),
                    'concept_paths': path_list,
                    'graph_json': graph_json
                }, context_instance=RequestContext(request))
            
            if f == 'skos':
                skos = SKOSWriter()
                response = HttpResponse(skos.write(concept_graph, format="pretty-xml"), content_type="application/xml")
                return response

            if emulate_elastic_search:
                ret.append({'_type': id, '_source': concept_graph})
            else:
                ret.append(concept_graph)       

            if emulate_elastic_search:
                ret = {'hits':{'hits':ret}}    

        else:
            se = SearchEngineFactory().create()
            ret = se.search('', index='concept', type=ids, search_field='value', use_wildcard=True)

    if request.method == 'POST':
        json = request.body

        if json != None:
            data = JSONDeserializer().deserialize(json)

            if conceptid == '':
                with transaction.atomic():
                    concept = Concept()

                    if 'label' in data and data['label'].strip() != '':
                        value = ConceptValue()
                        value.type = 'prefLabel'
                        value.value = data['label']
                        value.language = data['language']
                        value.category = 'label'
                        value.datatype = 'text'
                        concept.addvalue(value)
                    else:
                         return JSONResponse(SaveFailed(message='A label is required'))

                    if 'note' in data:
                        value = ConceptValue()
                        value.type = 'scopeNote'
                        value.value = data['note']
                        value.language = data['language']
                        value.category = 'note'
                        value.datatype = 'text'
                        concept.addvalue(value)

                    concept.addparent({'id': data['parentconceptid'], 'relationshiptype': 'has narrower concept'})    
                    concept.save()
                    concept.index()
                    ret = concept

                return JSONResponse(ret, indent=(4 if request.GET.get('pretty', False) else None))

            elif data['action'] == 'manage-related-concept':
                relation = None
                if 'related_concept' in data:
                    relation = archesmodels.ConceptRelations()
                    relation.pk = str(uuid.uuid4())
                    relation.conceptidfrom_id = conceptid
                    relation.conceptidto_id = data['related_concept']
                    relation.relationtype_id = 'has related concept'
                    relation.save()
                else:
                    conceptid = data['conceptid']
                    target_parent_conceptid = data['target_parent_conceptid']
                    current_parent_conceptid = data['current_parent_conceptid']

                    relation = archesmodels.ConceptRelations.objects.get(conceptidfrom_id= current_parent_conceptid, conceptidto_id=conceptid)
                    relation.conceptidfrom_id = target_parent_conceptid
                    relation.save()

                return JSONResponse(relation)


    if request.method == 'DELETE':
        json = request.body
        if json != None:
            data = JSONDeserializer().deserialize(json)
            if 'action' in data:
                action = data['action']

                if data['action'] == 'delete-relationship':
                    relatedconceptid = data['relatedconceptid']
                    concept = Concept({'id':conceptid})
                    concept.addrelatedconcept({'id': relatedconceptid})
                    concept.delete_related_concept()
                
                elif data['action'] == 'delete-concept':
                    concept = Concept()
                    concept.get(id=conceptid)
                    concept.delete_index()
                    concept.delete()
                    ret['success'] = True

    return JSONResponse(ret, indent=(4 if pretty else None))

@csrf_exempt
def concept_value(request, valueid):
    #  need to check user credentials here

    if request.method == 'POST':
        json = request.body

        if json != None:
            value = ConceptValue(json)
            value.save()

            return JSONResponse(value)

    if request.method == 'DELETE':
        value = ConceptValue({'id': valueid})
        value.delete()
        
        return JSONResponse(value)

    return JSONResponse({'success': False})

@csrf_exempt
def search(request):
    se = SearchEngineFactory().create()
    searchString = request.GET['q']
    query = Query(se, start=0, limit=100)
    phrase = Match(field='value', query=searchString.lower(), type='phrase_prefix')
    query.add_query(phrase)
    results = query.search(index='concept_labels')

    cached_scheme_names = {}
    for result in results['hits']['hits']:
        # first look to see if we've already retrieved the scheme name
        # else look up the scheme name with ES and cache the result
        if result['_type'] in cached_scheme_names:
            result['_type'] = cached_scheme_names[result['_type']]
        else:
            query = Query(se, start=0, limit=100)
            phrase = Match(field='conceptid', query=result['_type'], type='phrase')
            query.add_query(phrase)
            scheme = query.search(index='concept_labels')
            for label in scheme['hits']['hits']:
                if label['_source']['type'] == 'prefLabel':
                    cached_scheme_names[result['_type']] = label['_source']['value']
                    result['_type'] = label['_source']['value']
    return JSONResponse(results)

def concept_tree(request):
    conceptid = request.GET.get('node', None)
    concepts = Concept({'id': conceptid}).concept_tree(top_concept = '00000000-0000-0000-0000-000000000003')
    return JSONResponse(concepts, indent=4)

class SaveFailed(object):
    def __init__(self, message='', additionaldata=None):
        self.success = False
        self.message = message
        self.additionaldata = additionaldata
