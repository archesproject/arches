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

import re
import urllib,json
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
from arches.app.search.elasticsearch_dsl_builder import Query, Terms, Bool, Match, Nested
from django.contrib.gis.geos import GEOSGeometry
import binascii
from arches.app.utils.encrypt import Crypter
from arches.app.utils.spatialutils import getdates
from arches.app.utils.eamena_utils import validatedates
from django.shortcuts import redirect

import logging

def report(request, resourceid):
    logging.warning("Viewing Report. User=%s", request.user)

    # Redirect non-logged-in users to the login screen
    if request.user.is_anonymous:
	redirect('/auth')

    lang = request.GET.get('lang', request.LANGUAGE_CODE)
    page = request.GET.get('page', 1)
    se = SearchEngineFactory().create()
    report_info = se.search(index='resource', id=resourceid)
    primaryname = se.search(index='entity', id = resourceid)
    report_info['source'] = report_info['_source']
    report_info['type'] = report_info['_type']
    report_info['source']['graph'] = report_info['source']['graph']
    if primaryname['_source']['primaryname']:
        report_info['source']['primaryname'] = primaryname['_source']['primaryname'] 
    del report_info['_source']
    del report_info['_type']            
    geometry = JSONSerializer().serialize(report_info['source']['geometry'])
    GeoCrypt = Crypter(settings.ENCODING_KEY)
    iv, encrypted = GeoCrypt.encrypt(geometry, GeoCrypt.KEY)
    ciphertext = binascii.b2a_base64(encrypted).rstrip()
    if geometry !='null':
        result = {
          'editor': 'true' if 'edit' in request.user.user_groups else 'false',
          'key': GeoCrypt.KEY,
          'iv': iv,
          'ciphertext': ciphertext
          
        }
    else:
        result = None
    
    if report_info['type'] == "INFORMATION_RESOURCE.E73": # These clauses produce subtypes for Imagery, Shared Dataset and Cartography Info Resources, with the aim of producing different Report pages for each of these Resource Types
        report_info['subtype'] = ''
        report_info['filepath'] =''
        report_info['has_image'] =''
        if 'ACQUISITION_ASSIGNMENT_E17' in report_info['source']['graph'] or 'CATALOGUE_ID_E42' in report_info['source']['graph']:
            report_info['subtype'] = 'Imagery'
        if 'RESOURCE_CREATION_EVENT_E65' in report_info['source']['graph']:
            for value in report_info['source']['graph']['RESOURCE_CREATION_EVENT_E65']:
                if 'CREATOR_E39' in value:
                    for subvalue in value['CREATOR_E39']:
                        if 'IMAGERY_CREATOR_APPELLATION_E82' in subvalue:
                            report_info['subtype'] = 'Imagery'
                        elif 'SHARED_DATA_SOURCE_CREATOR_APPELLATION_E82' in subvalue:
                            report_info['subtype'] = 'Shared'
                if 'SHARED_DATA_SOURCE_SHARER_E39' in value:
                    report_info['subtype'] = 'Shared'
        if 'PUBLICATION_EVENT_E12' in report_info['source']['graph']:
            for value in report_info['source']['graph']['PUBLICATION_EVENT_E12']:
                if 'PUBLICATION_ASSIGNMENT_E17' in value:
                    for subvalue in value['PUBLICATION_ASSIGNMENT_E17']:
                        if 'TILE_SQUARE_APPELLATION_E44' in subvalue or 'TILE_SQUARE_DETAILS_E44' in subvalue:
                            report_info['subtype'] = 'Cartography'
                        elif 'IMAGERY_SOURCE_TYPE_E55' in subvalue:
                            report_info['subtype'] = 'Imagery'
        if 'FILE_PATH_E62' in report_info['source']['graph']:
            report_info['filepath'] = report_info['source']['graph']['FILE_PATH_E62'][0]
        if 'THUMBNAIL_E62' in report_info['source']['graph']:
            report_info['has_image'] = report_info['source']['graph']['THUMBNAIL_E62'][0]
        if 'URL_E51' in report_info['source']['graph']: #If the resource has a URL, it verifies that it is an APAAME json string, in which case it retrieves the url of the photo from the json string and passes it to the report
            flickr_feed = report_info['source']['graph']['URL_E51'][0]['URL_E51__value'][:-1] if report_info['source']['graph']['URL_E51'][0]['URL_E51__value'].endswith('/') else report_info['source']['graph']['URL_E51'][0]['URL_E51__value']
            try:
                response = urllib.urlopen('https://www.flickr.com/services/oembed?url='+flickr_feed+'&format=json')          
                data = response.read().decode("utf-8")
                flickr_feed = json.loads(data)
                report_info['filepath'], report_info['has_image'] = flickr_feed['url'], True
            except:
                pass
                
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
                    if isinstance(item[key], basestring) and uuid_regex.match(item[key]):
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
                    if isinstance(item[key], basestring) and uuid_regex.match(item[key]):
                        try:
                            item[key] = temp[item[key]]['value']
                        except:
                            pass

    crawl_again([report_info['source']['graph']])

    #return JSONResponse(report_info, indent=4)

    related_resource_dict = {
        'HERITAGE_RESOURCE': [],
        'HERITAGE_RESOURCE_GROUP': [],
        'HERITAGE_FEATURE': [],
        'HERITAGE_COMPONENT': [],
        'ACTIVITY': [],
        'ACTOR': [],
        'HISTORICAL_EVENT': [],
        'INFORMATION_RESOURCE_IMAGE': [],
        'INFORMATION_RESOURCE_DOCUMENT': [],
        'INFORMATION_RESOURCE_MAP': [],
        'INFORMATION_RESOURCE_SATELLITE': [],
        'INFORMATION_RESOURCE_SHARED': []
    }

    related_resource_info = get_related_resources(resourceid, lang) 
    # parse the related entities into a dictionary by resource type
    for related_resource in related_resource_info['related_resources']:
        VirtualGlobeName = []
        OtherImageryName = []
        SharedDataset = []
        VirtualGlobe = False
        OtherImagery = True
        information_resource_type = 'DOCUMENT'
        related_resource['relationship'] = []
        related_resource['datefrom'] = []
        related_resource['dateto'] = []
        related_resource['notes'] = []
        related_resource['date'] = []
        if related_resource['entitytypeid'] == 'HERITAGE_RESOURCE.E18':
            for entity in related_resource['domains']:
                if entity['entitytypeid'] == 'RESOURCE_TYPE_CLASSIFICATION.E55':
                    related_resource['relationship'].append(get_preflabel_from_valueid(entity['value'], lang)['value'])
        elif related_resource['entitytypeid'] == 'HERITAGE_RESOURCE_GROUP.E27':
            for entity in related_resource['domains']:
                if entity['entitytypeid'] == 'NAME.E41':
                    related_resource['relationship'].append(get_preflabel_from_valueid(entity['value'], lang)['value'])
        elif related_resource['entitytypeid'] == 'HERITAGE_FEATURE.E24':
            for entity in related_resource['domains']:
                if entity['entitytypeid'] == 'INTERPRETATION_TYPE.I4':
                    related_resource['relationship'].append(get_preflabel_from_valueid(entity['value'], lang)['value'])
        elif related_resource['entitytypeid'] == 'HERITAGE_COMPONENT.B2':
            for entity in related_resource['domains']:
                if entity['entitytypeid'] == 'COMPONENT_TYPE.E55':
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
            for entity in related_resource['child_entities']:
                if entity['entitytypeid'] == 'ACTOR_APPELLATION.E82':
                    related_resource['primaryname'] = entity['value']
        elif related_resource['entitytypeid'] == 'HISTORICAL_EVENT.E5':
            for entity in related_resource['domains']:
                if entity['entitytypeid'] == 'HISTORICAL_EVENT_TYPE.E55':
                    related_resource['relationship'].append(get_preflabel_from_conceptid(entity['conceptid'], lang)['value'])
        elif related_resource['entitytypeid'] == 'INFORMATION_RESOURCE.E73':
            for entity in related_resource['domains']:
                if entity['entitytypeid'] == 'INFORMATION_RESOURCE_TYPE.E55':                            
                    related_resource['relationship'].append(get_preflabel_from_valueid(entity['value'], lang)['value'])
  
            for entity in related_resource['child_entities']:
                if entity['entitytypeid'] == 'FILE_PATH.E62':
                    related_resource['file_path'] = settings.MEDIA_URL + entity['label']
                if entity['entitytypeid'] == 'THUMBNAIL.E62':
                    related_resource['thumbnail'] = settings.MEDIA_URL + entity['label']
                    information_resource_type = 'IMAGE'
                if entity['entitytypeid'] == 'TILE_SQUARE_DETAILS.E44' or entity['entitytypeid'] == 'TILE_SQUARE_APPELLATION.E44': #If this node is populated, the Info resource is assumed to be a Map and its default name is set to Sheet Name
                    related_resource['primaryname'] = entity['label']
                    information_resource_type = 'MAP'                      
                elif entity['entitytypeid'] == 'SHARED_DATA_SOURCE_APPELLATION.E82' or entity['entitytypeid'] == 'SHARED_DATA_SOURCE_AFFILIATION.E82' or entity['entitytypeid'] == 'SHARED_DATA_SOURCE_CREATOR_APPELLATION.E82': #If this node is populated, the Info resource is assumed to be a Shared Dataset and its default name is set to Shared Dated Source
                    SharedDataset.append(entity['label'])
                    information_resource_type = 'SHARED'        
                elif entity['entitytypeid'] == 'CATALOGUE_ID.E42': #If this node is populated, the Info resource is assumed to be Imagery other than VirtualGlobe type
                    OtherImageryName.append(entity['label'])
                    OtherImagery = False
                    information_resource_type = 'SATELLITE'
                elif entity['entitytypeid'] == 'IMAGERY_CREATOR_APPELLATION.E82': #If this node is populated, and Catalogue_ID.E42 is not (checked by bool OtherImagery), the Info resource is assumed to be a VirtualGlobe
                    VirtualGlobe = True
                    VirtualGlobeName.append(entity['label'])
                    information_resource_type = 'SATELLITE'
                elif entity['entitytypeid'] == 'TITLE.E41':
                    related_resource['primaryname'] = entity['value']

            for entity in related_resource['dates']:
                if entity['entitytypeid'] == 'DATE_OF_ACQUISITION.E50':                 
                    related_resource['date'] = validatedates(entity['label'])                                
            if VirtualGlobe == True and OtherImagery == True: #This routine creates the concatenated primary name for a Virtual Globe related resource
                for entity in related_resource['domains']:
                    if entity['entitytypeid'] == 'IMAGERY_SOURCE_TYPE.E55':
                        VirtualGlobeName.append(entity['label'])
                for entity in related_resource['dates']:
                    if entity['entitytypeid'] == 'DATE_OF_ACQUISITION.E50':
                        VirtualGlobeName.append(entity['label'])
                related_resource['primaryname'] = " - ".join(VirtualGlobeName)
            elif OtherImagery == False: #This routine creates the concatenated primary name for Imagery related resource
                for entity in related_resource['dates']:
                    if entity['entitytypeid'] == 'DATE_OF_ACQUISITION.E50':
                        OtherImageryName.append(entity['label'])
                related_resource['primaryname'] = " - ".join(OtherImageryName)
            if  information_resource_type == 'SHARED':  #This routine creates the concatenated primary name for a Shared dataset
                related_resource['primaryname'] = " - ".join(SharedDataset)
        # get the relationship between the two entities as well as the notes and dates, if the exist
        
        for relationship in related_resource_info['resource_relationships']:
            if relationship['entityid1'] == related_resource['entityid'] or relationship['entityid2'] == related_resource['entityid']: 
                related_resource['relationship'].append(get_preflabel_from_valueid(relationship['relationshiptype'], lang)['value'])
                if relationship['datestarted']: related_resource['datefrom'] = relationship['datestarted']
                if relationship['dateended']: related_resource['dateto'] = relationship['dateended']
                if relationship['notes']: related_resource['notes'] = relationship['notes']
        entitytypeidkey = related_resource['entitytypeid'].split('.')[0]
        if entitytypeidkey == 'INFORMATION_RESOURCE':
            entitytypeidkey = '%s_%s' % (entitytypeidkey, information_resource_type)
        related_resource_dict[entitytypeidkey].append(related_resource)

    return render_to_response('resource-report.htm', {
            'geometry': JSONSerializer().serialize(result),
#             'geometry': JSONSerializer().serialize(report_info['source']['geometry']),
            'resourceid': resourceid,
            'report_template': 'views/reports/' + report_info['type'] + '.htm',
            'report_info': report_info,
            'related_resource_dict': related_resource_dict,
            'main_script': 'resource-report',
            'active_page': 'ResourceReport',
            'BingDates': getdates(report_info['source']['geometry']) # Retrieving the dates of Bing Imagery
        },
        context_instance=RequestContext(request))        
