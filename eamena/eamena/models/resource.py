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
from django.conf import settings
import arches.app.models.models as archesmodels
from arches.app.models.resource import Resource as ArchesResource
from arches.app.search.search_engine_factory import SearchEngineFactory
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from eamena.models import forms
from django.utils.translation import ugettext as _
from arches.app.models.entity import Entity

class Resource(ArchesResource):
    def __init__(self, *args, **kwargs):
        super(Resource, self).__init__(*args, **kwargs)
        description_group = {
            'id': 'resource-description',
            'icon':'fa-folder',
            'name': _('Resource Description'),
            'forms': [
                
            ]   
        }

        self.form_groups.append(description_group)

        if self.entitytypeid == 'HERITAGE_RESOURCE.E18':
            description_group['forms'][:0] = [
                forms.SummaryForm.get_info(), 
                forms.LocationForm.get_info(),
                forms.MeasurementvaluesForm.get_info(),
                forms.Classification1Form.get_info(),                                             
                forms.MeasurementForm.get_info(),
                forms.RelatedFilesForm.get_info(),
                forms.RelatedResourcesForm.get_info(),
                forms.DescriptionForm.get_info(),
                                              
            ]

        elif self.entitytypeid == 'HERITAGE_RESOURCE_GROUP.E27':
            description_group['forms'][:0] = [
                forms.AssessmentSummaryForm.get_info(),
                forms.SummaryForm.get_info(),
                forms.LocationResForm.get_info(),
                forms.MeasurementvaluesForm.get_info(),
                forms.ArchaeologicalAssessmentForm.get_info(),
                forms.ConditionAssessmentForm.get_info(),
                # forms.Classification1Form.get_info(),
                # forms.MeasurementForm.get_info( ),
                forms.RelatedFilesForm.get_info(),
                # forms.DesignationForm.get_info(),
                forms.ManMadeForm.get_info(),
                forms.RelatedResourcesForm.get_info(),
                # forms.DescriptionForm.get_info(),
                # forms.TestWizForm.get_info(),
        
            ]


        elif self.entitytypeid == 'ACTIVITY.E7':
            description_group['forms'][:0] = [
                forms.ActivitySummaryForm.get_info(),
                forms.DescriptionForm.get_info(),
                forms.LocationForm.get_info(),
                forms.ActivityActionsForm.get_info(),
                forms.ExternalReferenceForm.get_info(),
                forms.RelatedResourcesForm.get_info(),
            ]
     

        elif self.entitytypeid == 'ACTOR.E39':
            description_group['forms'][:0] = [
                forms.ActorSummaryForm.get_info(), 
                forms.DescriptionForm.get_info(),
                forms.RoleForm.get_info(),
                forms.ExternalReferenceForm.get_info(),
                forms.RelatedResourcesForm.get_info(),                
            ]


        elif self.entitytypeid == 'HISTORICAL_EVENT.E5':
            description_group['forms'][:0] = [
                forms.HistoricalEventSummaryForm.get_info(),
                forms.DescriptionForm.get_info(),
                forms.LocationForm.get_info(), 
                forms.PhaseForm.get_info(),
                forms.RelatedResourcesForm.get_info(),
            ]


        elif self.entitytypeid == 'INFORMATION_RESOURCE.E73':
            description_group['forms'][:0] = [
                forms.InformationResourceSummaryForm.get_info(), 
                forms.PublicationForm.get_info(),
                forms.ImageryForm.get_info(),
                forms.CartographyForm.get_info(),
                forms.SharedDataForm.get_info(),
                forms.ExternalReferenceForm.get_info(),
                forms.CoverageForm.get_info(),
                forms.FileUploadForm.get_info(),
                forms.DescriptionForm.get_info(),
                forms.RelatedResourcesForm.get_info(),
            ]

        if self.entityid != '':
            self.form_groups.append({
                'id': 'manage-resource',
                'icon': 'fa-wrench',
                'name': _('Manage Resource'),
                'forms': [
                    forms.EditHistory.get_info(),
                    forms.DeleteResourceForm.get_info()
                ]
            })
            
            

    def get_primary_name(self):
        displayname = super(Resource, self).get_primary_name()
        names = self.get_names()
        if len(names) > 0:
            displayname = names[0].value
        return displayname


    def get_names(self):
        """
        Gets the human readable name to display for entity instances

        """

        names = []
        name_nodes = self.find_entities_by_type_id(settings.RESOURCE_TYPE_CONFIGS()[self.entitytypeid]['primary_name_lookup']['entity_type'])
        if len(name_nodes) > 0:
            for name in name_nodes:
                names.append(name)

        return names


    def prepare_documents_for_map_index(self, geom_entities=[]):
        """
        Generates a list of geojson documents to support the display of resources on a map

        """

        documents = super(Resource, self).prepare_documents_for_map_index(geom_entities=geom_entities)
        
        def get_entity_data(entitytypeid, get_label=False):

            entity_data = _('None specified')
            entity_nodes = self.find_entities_by_type_id(entitytypeid)
            if len(entity_nodes) > 0:
                entity_data = []
                for node in entity_nodes:
                    if get_label:

                        entity_data.append(node.label)
                    else:
                        entity_data.append(node.value)
                entity_data = ', '.join(entity_data)
            return entity_data

        document_data = {}
        
#         if self.entitytypeid == 'HERITAGE_RESOURCE.E18':
#             document_data['certainty_type'] = get_entity_data('ARCHAEOLOGY_CERTAINTY_VALUE.I6', get_label=True)

#             document_data['address'] = _('None specified')
#             address_nodes = self.find_entities_by_type_id('PLACE_ADDRESS.E45')
#             for node in address_nodes:
#                 if node.find_entities_by_type_id('ADDRESS_TYPE.E55')[0].label == 'Primary':
#                     document_data['address'] = node.value

#         if self.entitytypeid == 'HERITAGE_RESOURCE_GROUP.E27':
#             document_data['certainty_type'] = get_entity_data('ARCHAEOLOGY_CERTAINTY_VALUE.I6', get_label=True)
                    
        if self.entitytypeid == 'ACTIVITY.E7':
            document_data['resource_type'] = get_entity_data('ACTIVITY_TYPE.E55', get_label=True)

        if self.entitytypeid == 'HISTORICAL_EVENT.E5':
            document_data['resource_type'] = get_entity_data('HISTORICAL_EVENT_TYPE.E55', get_label=True)

        if self.entitytypeid == 'ACTOR.E39':
            document_data['resource_type'] = get_entity_data('ACTOR_TYPE.E55', get_label=True)

        if self.entitytypeid == 'INFORMATION_RESOURCE.E73':
            document_data['resource_type'] = get_entity_data('INFORMATION_RESOURCE_TYPE.E55', get_label=True)
            document_data['format'] = get_entity_data('INFORMATION_CARRIER_FORMAT_TYPE.E55',  get_label=True)
#           Fields for Information_Resource.E73 map pop-up yet to be decided. AZ(10/08/16)
#             document_data['creation_date'] = get_entity_data('DATE_OF_CREATION.E50')
#             document_data['publication_date'] = get_entity_data('DATE_OF_PUBLICATION.E50')

        if self.entitytypeid == 'HISTORICAL_EVENT.E5' or self.entitytypeid == 'ACTIVITY.E7' or self.entitytypeid == 'ACTOR.E39':
            document_data['start_date'] = get_entity_data('BEGINNING_OF_EXISTENCE.E63')
            document_data['end_date'] = get_entity_data('END_OF_EXISTENCE.E64')

        if self.entitytypeid == 'HERITAGE_RESOURCE.E18' or self.entitytypeid == 'HERITAGE_RESOURCE_GROUP.E27':
            document_data['certainty_type'] = get_entity_data('ARCHAEOLOGY_CERTAINTY_VALUE.I6', get_label=True)
            document_data['site_function'] = get_entity_data('SITE_FUNCTION_TYPE.E55', get_label=True)
            document_data['disturbance_type'] = get_entity_data('DISTURBANCE_TYPE.E55', get_label=True)

        for document in documents:
            for key in document_data:
                document['properties'][key] = document_data[key]

        return documents


        
    @staticmethod
    def get_report(resourceid):
        # get resource data for resource_id from ES, return data
        # with correct id for the given resource type
        return {
            'id': 'heritage-resource',
            'data': {
                'hello_world': 'Hello World!'
            }
        }
