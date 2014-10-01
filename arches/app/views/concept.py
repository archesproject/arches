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
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.shortcuts import render_to_response
import arches.app.models.models as archesmodels
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.utils.skos import SKOSWriter


def rdm(request, conceptid):
    languages = archesmodels.DLanguages.objects.all()
    valuetypes = archesmodels.ValueTypes.objects.all()
    othertypes = []
    for type in valuetypes:
        if type.category == 'label' or type.pk == 'scopeNote':
            pass
        else:
            othertypes.append(type)

    return render_to_response('rdm.htm', {'conceptid': conceptid, 'languages': languages, 'valuetype_labels': valuetypes.filter(category='label'), 'valuetype_notes': valuetypes.filter(pk='scopeNote'),'valuetype_related_values': othertypes}, context_instance=RequestContext(request))

@csrf_exempt
def concept(request, ids):
    include_subconcepts = request.GET.get('include_subconcepts', 'true') == 'true'
    include_parentconcepts = request.GET.get('include_parentconcepts', 'true') == 'true'
    emulate_elastic_search = request.GET.get('emulate_elastic_search', 'false') == 'true'
    fromdb = request.GET.get('fromdb', 'false') == 'true'
    f = request.GET.get('f', 'json')
    lang = request.GET.get('lang', 'en-us')
    depth_limit = request.GET.get('depth_limit', None)
    pretty = request.GET.get('pretty', False)

    if f == 'html':
        fromdb = True
        depth_limit = 1

    if f == 'skos':
        fromdb = True

    ret = []
    if request.method == 'GET':
        if fromdb:
            for id in ids.split(','):
                if ".E" in id:
                    entitytype = archesmodels.EntityTypes.objects.get(pk = id)
                    concept = entitytype.conceptid
                else:
                    concept = archesmodels.Concepts.objects.get(conceptid = id)

                concept_graph = concept.graph(include_subconcepts=include_subconcepts, 
                    include_parentconcepts=include_parentconcepts, depth_limit=depth_limit, up_depth_limit=1)
                
                if f == 'html':
                    languages = archesmodels.DLanguages.objects.all()
                    valuetypes = archesmodels.ValueTypes.objects.all()
                    prefLabel = concept_graph.get_preflabel(lang=lang)
                    return render_to_response('rdm_item.htm', {'lang': lang, 'prefLabel': prefLabel, 'concept': concept_graph , 'languages': languages}, context_instance=RequestContext(request))
                
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

            with transaction.atomic():
                concept = archesmodels.Concepts()
                concept.pk = str(uuid.uuid4())
                concept.conceptschemeid = archesmodels.Conceptschemes.objects.get(pk='00000000-0000-0000-0000-000000000000')
                concept.save()

                conceptrelation = archesmodels.ConceptRelations()
                conceptrelation.pk = str(uuid.uuid4())
                conceptrelation.conceptidfrom = archesmodels.Concepts.objects.get(pk=data['parentconceptid'])
                conceptrelation.conceptidto = concept
                conceptrelation.relationtype = archesmodels.DRelationtypes.objects.get(pk='has narrower concept')
                conceptrelation.save()

                if 'label' in data:
                    value = archesmodels.Values()
                    value.pk = str(uuid.uuid4())
                    value.conceptid = concept
                    value.valuetype = archesmodels.ValueTypes.objects.get(pk='prefLabel')
                    value.value = data['label']
                    value.languageid = archesmodels.DLanguages.objects.get(pk=data['language'])
                    value.save()

                if 'note' in data:
                    value = archesmodels.Values()
                    value.pk = str(uuid.uuid4())
                    value.conceptid = concept
                    value.valuetype = archesmodels.ValueTypes.objects.get(pk='scopeNote')
                    value.value = data['note']
                    value.languageid = archesmodels.DLanguages.objects.get(pk=data['language'])
                    value.save()

            ret = concept.graph(include_subconcepts=False, include_parentconcepts=False, include=['label'])


    if request.method == 'DELETE':
        for id in ids.split(','):
            ret = []

            if ".E" in id:
                entitytype = archesmodels.EntityTypes.objects.get(pk = id)
                concept = entitytype.conceptid
            else:
                concept = archesmodels.Concepts.objects.get(conceptid = id)

            concepts = concept.graph(exclude=['note','label',None], include_parentconcepts=False).flatten()

            with transaction.atomic():
                for concept in concepts:
                    ret.append(concept.get_preflabel())
                    concept.delete()

            ret.success = True

    return JSONResponse(ret, indent=(4 if pretty else None))

def concept_tree(request):
    conceptid = request.GET.get('node', None)
    class concept(object):
        def __init__(self, *args, **kwargs):
            self.label = ''
            self.labelid = ''
            self.id = ''
            self.load_on_demand = False
            self.children = []    

    def _findNarrowerConcept(conceptid, depth_limit=None, level=0):
        labels = archesmodels.Values.objects.filter(conceptid = conceptid)
        ret = concept()          
        for label in labels:
            if label.valuetype_id == 'prefLabel':
                ret.label = label.value
                ret.id = label.conceptid_id
                ret.labelid = label.valueid

        conceptrealations = archesmodels.ConceptRelations.objects.filter(conceptidfrom = conceptid)
        if depth_limit != None and len(conceptrealations) > 0 and level >= depth_limit:
            ret.load_on_demand = True
        else:
            if depth_limit != None:
                level = level + 1                
            for relation in conceptrealations:
                ret.children.append(_findNarrowerConcept(relation.conceptidto_id, depth_limit=depth_limit, level=level))   

        return ret 

    def _findBroaderConcept(conceptid, child_concept, depth_limit=None, level=0):
        conceptrealations = archesmodels.ConceptRelations.objects.filter(conceptidto = conceptid)
        if len(conceptrealations) > 0:
            labels = archesmodels.Values.objects.filter(conceptid = conceptrealations[0].conceptidfrom_id)
            ret = concept()          
            for label in labels:
                if label.valuetype_id == 'prefLabel':
                    ret.label = label.value
                    ret.id = label.conceptid_id
                    ret.labelid = label.valueid

            ret.children.append(child_concept)
            return _findBroaderConcept(conceptrealations[0].conceptidfrom_id, ret, depth_limit=depth_limit, level=level)
        else:
            return child_concept
    
    if conceptid == None or conceptid == '':
        concepts = [_findNarrowerConcept('00000000-0000-0000-0000-000000000001', depth_limit=2)]
    else:
        concepts = _findNarrowerConcept(conceptid, depth_limit=2)
        concepts = [_findBroaderConcept(conceptid, concepts, depth_limit=1)]

    return JSONResponse(concepts, indent=4)

@csrf_exempt
def concept_value(request, id=None):
    #  need to check user credentials here

    if request.method == 'POST':
        json = request.POST.get('json', None)

        if json != None:
            value = JSONDeserializer().deserialize(json)
            
            newvalue = archesmodels.Values()
            newvalue.pk = str(uuid.uuid4())
            if value['id'] != '':
                newvalue = archesmodels.Values.objects.get(pk=value['id'])

            newvalue.value = value['value']
            newvalue.conceptid = archesmodels.Concepts.objects.get(pk=value['conceptid'])
            newvalue.valuetype = archesmodels.ValueTypes.objects.get(pk=value['valuetype'])
            newvalue.datatype = value['datatype']
            newvalue.languageid = archesmodels.DLanguages.objects.get(pk=value['language'])
            newvalue.save()

            return JSONResponse(newvalue)

    if request.method == 'DELETE':
        if id != None:
            newvalue = archesmodels.Values.objects.get(pk=id)
            newvalue.delete();

            return JSONResponse(newvalue)

    return JSONResponse({'success': False})

@csrf_exempt
def update_relation(request):
    if request.method == 'POST':
        json = request.body
        print json

        if json != None:
            data = JSONDeserializer().deserialize(json)
            
            conceptid = data['conceptid']
            target_parent_conceptid = data['target_parent_conceptid']
            current_parent_conceptid = data['current_parent_conceptid']

            relation = archesmodels.ConceptRelations.objects.get(conceptidfrom_id= current_parent_conceptid, conceptidto_id=conceptid)
            relation.conceptidfrom_id = target_parent_conceptid
            relation.save()

            return JSONResponse(relation)

    return JSONResponse({'success': False})


# class ConceptValueViewModel(object):
    
#     def __init__(self, data=None):
#         self.
#         if data:
#         self. 