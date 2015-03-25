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
{% if source_app == 'arches' %}
# import re
# from django.template import RequestContext
# from django.shortcuts import render_to_response
# from django.conf import settings
# from arches.app.models import models
# from arches.app.models.concept import Concept
# from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
# from arches.app.utils.JSONResponse import JSONResponse
# from arches.app.views.concept import get_preflabel_from_valueid
# from arches.app.views.concept import get_preflabel_from_conceptid
# from arches.app.views.resources import get_related_resources
# from arches.app.search.search_engine_factory import SearchEngineFactory
# from arches.app.search.elasticsearch_dsl_builder import Query, Terms, Bool, Match
{% else %}
import re
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings
from arches.app.models import models
from arches.app.models.concept import Concept
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.utils.JSONResponse import JSONResponse
from arches.app.views.concept import get_preflabel_from_valueid
from arches.app.views.concept import get_preflabel_from_conceptid
from arches.app.views.resources import get_related_resources
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.search.elasticsearch_dsl_builder import Query, Terms, Bool, Match
{% endif %}

{% if source_app == 'arches' %}
def report(request, resourceid):
    pass
    # lang = request.GET.get('lang', settings.LANGUAGE_CODE)
    # se = SearchEngineFactory().create()
    # report_info = se.search(index='resource', id=resourceid)
    # report_info['source'] = report_info['_source']
    # report_info['type'] = report_info['_type']
    # report_info['source']['graph'] = report_info['source']['graph']
    # del report_info['_source']
    # del report_info['_type']

    # def get_evaluation_path(valueid):
    #     value = models.Values.objects.get(pk=valueid)
    #     concept_graph = Concept().get(id=value.conceptid_id, include_subconcepts=False, 
    #         include_parentconcepts=True, include_relatedconcepts=False, up_depth_limit=None, lang=lang)
        
    #     paths = []
    #     for path in concept_graph.get_paths(lang=lang)[0]:
    #         if path['label'] != 'Arches' and path['label'] != 'Evaluation Criteria Type':
    #             paths.append(path['label'])
    #     return '; '.join(paths)


    # concept_label_ids = set()
    # uuid_regex = re.compile('[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}')
    # # gather together all uuid's referenced in the resource graph
    # def crawl(items):
    #     for item in items:
    #         for key in item:
    #             if isinstance(item[key], list):
    #                 crawl(item[key])
    #             else:
    #                 if uuid_regex.match(item[key]):
    #                     if key == 'EVALUATION_CRITERIA_TYPE_E55__value':
    #                         item[key] = get_evaluation_path(item[key])
    #                     concept_label_ids.add(item[key])

    # crawl([report_info['source']['graph']])

    # # get all the concept labels from the uuid's
    # concept_labels = se.search(index='concept_labels', id=list(concept_label_ids))

    # # convert all labels to their localized prefLabel
    # temp = {}
    # if concept_labels != None:
    #     for concept_label in concept_labels['docs']:
    #         #temp[concept_label['_id']] = concept_label
    #         if concept_label['found']:
    #             # the resource graph already referenced the preferred label in the desired language
    #             if concept_label['_source']['type'] == 'prefLabel' and concept_label['_source']['language'] == lang:
    #                 temp[concept_label['_id']] = concept_label['_source']
    #             else: 
    #                 # the resource graph referenced a non-preferred label or a label not in our target language, so we need to get the right label
    #                 temp[concept_label['_id']] = get_preflabel_from_conceptid(concept_label['_source']['conceptid'], lang)

    # # replace the uuid's in the resource graph with their preferred and localized label                    
    # def crawl_again(items):
    #     for item in items:
    #         for key in item:
    #             if isinstance(item[key], list):
    #                 crawl_again(item[key])
    #             else:
    #                 if uuid_regex.match(item[key]):
    #                     try:
    #                         item[key] = temp[item[key]]['value']
    #                     except:
    #                         pass

    # crawl_again([report_info['source']['graph']])

    # #return JSONResponse(report_info, indent=4)

    # related_resource_dict = {
    #     'HERITAGE_RESOURCE': [],
    #     'HERITAGE_RESOURCE_GROUP': [],
    #     'ACTIVITY': [],
    #     'ACTOR': [],
    #     'HISTORICAL_EVENT': [],
    #     'INFORMATION_RESOURCE_IMAGE': [],
    #     'INFORMATION_RESOURCE_DOCUMENT': []
    # }

    # related_resource_info = get_related_resources(resourceid, lang)

    # # parse the related entities into a dictionary by resource type
    # for related_resource in related_resource_info['related_resources']:
    #     information_resource_type = None
    #     related_resource['relationship'] = []
    #     if related_resource['entitytypeid'] == 'HERITAGE_RESOURCE.E18':
    #         for entity in related_resource['domains']:
    #             if entity['entitytypeid'] == 'RESOURCE_TYPE_CLASSIFICATION.E55':
    #                 related_resource['relationship'].append(get_preflabel_from_valueid(entity['value'], lang)['value'])
    #     elif related_resource['entitytypeid'] == 'HERITAGE_RESOURCE_GROUP.E27':
    #         for entity in related_resource['domains']:
    #             if entity['entitytypeid'] == 'RESOURCE_TYPE_CLASSIFICATION.E55':
    #                 related_resource['relationship'].append(get_preflabel_from_valueid(entity['value'], lang)['value'])
    #     elif related_resource['entitytypeid'] == 'ACTIVITY.E7':
    #         for entity in related_resource['domains']:
    #             if entity['entitytypeid'] == 'ACTIVITY_TYPE.E55':
    #                 related_resource['relationship'].append(get_preflabel_from_valueid(entity['value'], lang)['value'])
    #     elif related_resource['entitytypeid'] == 'ACTOR.E39':
    #         for entity in related_resource['domains']:
    #             if entity['entitytypeid'] == 'ACTOR_TYPE.E55':
    #                 related_resource['relationship'].append(get_preflabel_from_conceptid(entity['conceptid'], lang)['value'])
    #                 related_resource['actor_relationshiptype'] = ''
    #     elif related_resource['entitytypeid'] == 'HISTORICAL_EVENT.E5':
    #         for entity in related_resource['domains']:
    #             if entity['entitytypeid'] == 'HISTORICAL_EVENT_TYPE.E55':
    #                 related_resource['relationship'].append(get_preflabel_from_conceptid(entity['conceptid'], lang)['value'])
    #     elif related_resource['entitytypeid'] == 'INFORMATION_RESOURCE.E73':
    #         for entity in related_resource['domains']:
    #             if entity['entitytypeid'] == 'INFORMATION_RESOURCE_TYPE.E55':
    #                 related_resource['relationship'].append(get_preflabel_from_valueid(entity['value'], lang)['value'])
    #             if entity['entitytypeid'] == 'INFORMATION_CARRIER_FORMAT_TYPE.E55':
    #                 if display_as_image(entity['conceptid']):
    #                     information_resource_type = 'IMAGE'
    #                 else:
    #                     information_resource_type = 'DOCUMENT'
    #         for entity in related_resource['child_entities']:
    #             if entity['entitytypeid'] == 'FILE_PATH.E62':
    #                 related_resource['file_path'] = settings.MEDIA_URL + entity['label']
    #             if entity['entitytypeid'] == 'THUMBNAIL.E62':
    #                 related_resource['thumbnail'] = settings.MEDIA_URL + entity['label']
            
    #     # get the relationship between the two entities
    #     for relationship in related_resource_info['resource_relationships']:
    #         if relationship['entityid1'] == related_resource['entityid'] or relationship['entityid2'] == related_resource['entityid']: 
    #             related_resource['relationship'].append(get_preflabel_from_valueid(relationship['relationshiptype'], lang)['value'])

    #     if len(related_resource['relationship']) > 0:
    #         related_resource['relationship'] = '(%s)' % (', '.join(related_resource['relationship']))
    #     else:
    #         related_resource['relationship'] = ''

    #     entitytypeidkey = related_resource['entitytypeid'].split('.')[0]
    #     if information_resource_type:
    #         entitytypeidkey = '%s_%s' % (entitytypeidkey, information_resource_type)
    #     if entitytypeidkey != 'INFORMATION_RESOURCE':
    #         related_resource_dict[entitytypeidkey].append(related_resource)


    # return render_to_response('resource-report.htm', {
    #         'geometry': JSONSerializer().serialize(report_info['source']['geometry']),
    #         'resourceid': resourceid,
    #         'report_template': 'views/reports/' + report_info['type'] + '.htm',
    #         'report_info': report_info,
    #         'related_resource_dict': related_resource_dict,
    #         'main_script': 'resource-report',
    #         'active_page': 'ResourceReport'
    #     },
    #     context_instance=RequestContext(request))        

# def display_as_image(conceptid):
#     concept = Concept().get(id=conceptid, include=['undefined'])
#     for value in concept.values:
#         if value.value == 'Y' and value.type == 'ViewableInBrowser':
#             return True
#     return False
{% else %}
def report(request, resourceid):
    lang = request.GET.get('lang', settings.LANGUAGE_CODE)
    se = SearchEngineFactory().create()
    report_info = se.search(index='resource', id=resourceid)
    report_info['source'] = report_info['_source']
    report_info['type'] = report_info['_type']
    report_info['source']['graph'] = report_info['source']['graph']
    del report_info['_source']
    del report_info['_type']

    def get_evaluation_path(valueid):
        value = models.Values.objects.get(pk=valueid)
        concept_graph = Concept().get(id=value.conceptid_id, include_subconcepts=False, 
            include_parentconcepts=True, include_relatedconcepts=False, up_depth_limit=None, lang=lang)
        
        paths = []
        for path in concept_graph.get_paths(lang=lang)[0]:
            if path['label'] != 'Arches' and path['label'] != 'Evaluation Criteria Type':
                paths.append(path['label'])
        return '; '.join(paths)


    concept_label_ids = set()
    uuid_regex = re.compile('[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}')
    # gather together all uuid's referenced in the resource graph
    def crawl(items):
        for item in items:
            for key in item:
                if isinstance(item[key], list):
                    crawl(item[key])
                else:
                    if uuid_regex.match(item[key]):
                        if key == 'EVALUATION_CRITERIA_TYPE_E55__value':
                            item[key] = get_evaluation_path(item[key])
                        concept_label_ids.add(item[key])

    crawl([report_info['source']['graph']])

    # get all the concept labels from the uuid's
    concept_labels = se.search(index='concept_labels', id=list(concept_label_ids))

    # convert all labels to their localized prefLabel
    temp = {}
    if concept_labels != None:
        for concept_label in concept_labels['docs']:
            #temp[concept_label['_id']] = concept_label
            if concept_label['found']:
                # the resource graph already referenced the preferred label in the desired language
                if concept_label['_source']['type'] == 'prefLabel' and concept_label['_source']['language'] == lang:
                    temp[concept_label['_id']] = concept_label['_source']
                else: 
                    # the resource graph referenced a non-preferred label or a label not in our target language, so we need to get the right label
                    temp[concept_label['_id']] = get_preflabel_from_conceptid(concept_label['_source']['conceptid'], lang)

    # replace the uuid's in the resource graph with their preferred and localized label                    
    def crawl_again(items):
        for item in items:
            for key in item:
                if isinstance(item[key], list):
                    crawl_again(item[key])
                else:
                    if uuid_regex.match(item[key]):
                        try:
                            item[key] = temp[item[key]]['value']
                        except:
                            pass

    crawl_again([report_info['source']['graph']])

    #return JSONResponse(report_info, indent=4)

    related_resource_dict = {
        'HERITAGE_RESOURCE': [],
        'HERITAGE_RESOURCE_GROUP': [],
        'ACTIVITY': [],
        'ACTOR': [],
        'HISTORICAL_EVENT': [],
        'INFORMATION_RESOURCE_IMAGE': [],
        'INFORMATION_RESOURCE_DOCUMENT': []
    }

    related_resource_info = get_related_resources(resourceid, lang)

    # parse the related entities into a dictionary by resource type
    for related_resource in related_resource_info['related_resources']:
        information_resource_type = None
        related_resource['relationship'] = []
        if related_resource['entitytypeid'] == 'HERITAGE_RESOURCE.E18':
            for entity in related_resource['domains']:
                if entity['entitytypeid'] == 'RESOURCE_TYPE_CLASSIFICATION.E55':
                    related_resource['relationship'].append(get_preflabel_from_valueid(entity['value'], lang)['value'])
        elif related_resource['entitytypeid'] == 'HERITAGE_RESOURCE_GROUP.E27':
            for entity in related_resource['domains']:
                if entity['entitytypeid'] == 'RESOURCE_TYPE_CLASSIFICATION.E55':
                    related_resource['relationship'].append(get_preflabel_from_valueid(entity['value'], lang)['value'])
        elif related_resource['entitytypeid'] == 'ACTIVITY.E7':
            for entity in related_resource['domains']:
                if entity['entitytypeid'] == 'ACTIVITY_TYPE.E55':
                    related_resource['relationship'].append(get_preflabel_from_valueid(entity['value'], lang)['value'])
        elif related_resource['entitytypeid'] == 'ACTOR.E39':
            for entity in related_resource['domains']:
                if entity['entitytypeid'] == 'ACTOR_TYPE.E55':
                    related_resource['relationship'].append(get_preflabel_from_conceptid(entity['conceptid'], lang)['value'])
                    related_resource['actor_relationshiptype'] = ''
        elif related_resource['entitytypeid'] == 'HISTORICAL_EVENT.E5':
            for entity in related_resource['domains']:
                if entity['entitytypeid'] == 'HISTORICAL_EVENT_TYPE.E55':
                    related_resource['relationship'].append(get_preflabel_from_conceptid(entity['conceptid'], lang)['value'])
        elif related_resource['entitytypeid'] == 'INFORMATION_RESOURCE.E73':
            for entity in related_resource['domains']:
                if entity['entitytypeid'] == 'INFORMATION_RESOURCE_TYPE.E55':
                    related_resource['relationship'].append(get_preflabel_from_valueid(entity['value'], lang)['value'])
                if entity['entitytypeid'] == 'INFORMATION_CARRIER_FORMAT_TYPE.E55':
                    if display_as_image(entity['conceptid']):
                        information_resource_type = 'IMAGE'
                    else:
                        information_resource_type = 'DOCUMENT'
            for entity in related_resource['child_entities']:
                if entity['entitytypeid'] == 'FILE_PATH.E62':
                    related_resource['file_path'] = settings.MEDIA_URL + entity['label']
                if entity['entitytypeid'] == 'THUMBNAIL.E62':
                    related_resource['thumbnail'] = settings.MEDIA_URL + entity['label']
            
        # get the relationship between the two entities
        for relationship in related_resource_info['resource_relationships']:
            if relationship['entityid1'] == related_resource['entityid'] or relationship['entityid2'] == related_resource['entityid']: 
                related_resource['relationship'].append(get_preflabel_from_valueid(relationship['relationshiptype'], lang)['value'])

        if len(related_resource['relationship']) > 0:
            related_resource['relationship'] = '(%s)' % (', '.join(related_resource['relationship']))
        else:
            related_resource['relationship'] = ''

        entitytypeidkey = related_resource['entitytypeid'].split('.')[0]
        if information_resource_type:
            entitytypeidkey = '%s_%s' % (entitytypeidkey, information_resource_type)
        if entitytypeidkey != 'INFORMATION_RESOURCE':
            related_resource_dict[entitytypeidkey].append(related_resource)


    return render_to_response('resource-report.htm', {
            'geometry': JSONSerializer().serialize(report_info['source']['geometry']),
            'resourceid': resourceid,
            'report_template': 'views/reports/' + report_info['type'] + '.htm',
            'report_info': report_info,
            'related_resource_dict': related_resource_dict,
            'main_script': 'resource-report',
            'active_page': 'ResourceReport'
        },
        context_instance=RequestContext(request))        

def display_as_image(conceptid):
    concept = Concept().get(id=conceptid, include=['undefined'])
    for value in concept.values:
        if value.value == 'Y' and value.type == 'ViewableInBrowser':
            return True
    return False
{% endif %}