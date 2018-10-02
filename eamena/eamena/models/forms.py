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
import uuid
from arches.app.models.models import RelatedResource
from arches.app.models.entity import Entity
from arches.app.models.resource import Resource
from arches.app.models.concept import Concept
from arches.app.models.forms import ResourceForm
from arches.app.utils.imageutils import generate_thumbnail
from arches.app.views.concept import get_preflabel_from_valueid
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.search.search_engine_factory import SearchEngineFactory
from django.forms.models import model_to_dict
from django.utils.translation import ugettext as _
# from django.forms.models import model_to_dict
from datetime import datetime
from arches.app.utils.spatialutils import getdates
from django.conf import settings

import logging
from arches.app.utils.JSONResponse import JSONResponse


def add_actor( observed_field, actor_field, data, user):
    observed = data[observed_field]
    for nodes_obj in observed:
        actor_found = False
        nodes = nodes_obj['nodes']
        for node in nodes:
            if node['entitytypeid'] == actor_field and not node['value'].strip() == '':
                actor_found = True
                
        if not actor_found :
            try:
                #If the node already has a UUID but doesn't have an actor, do not populate it from the current user
                uuid.UUID(node['entityid'])
            except(ValueError):
                nodes.append({
                    "entityid": "",
                    "entitytypeid": actor_field,
                    "value": user.first_name + ' ' + user.last_name
                })
        
    return data

def datetime_nodes_to_dates(branch_list):
    for branch in branch_list:
        for node in branch['nodes']:
            if hasattr(node, 'value') and isinstance(node.value, datetime):
                node.value = node.value.date()
                node.label = node.value
        
    return branch_list

def exclude_empty_branches(branch_list, required_node):
    branch_list_filled =[]
    for branch in branch_list:
        for node in branch['nodes']:
            if node.entitytypeid == required_node:
                branch_list_filled.append(branch)
    return branch_list_filled
    


# --- Resource Summary -> SummaryForm ------------------------------------------
class SummaryForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'summary',
            'icon': 'fa-align-center',
            'name': _('Resource Summary'),
            'class': SummaryForm
        }

    def update(self, data, files):
        self.update_nodes('NAME.E41', data)
        self.update_nodes('HERITAGE_PLACE_TYPE.E55', data)
        self.update_nodes('RIGHT.E30', data)
        self.update_nodes('DESCRIPTION_ASSIGNMENT.E13', data)
        return

    def load(self, lang):
        if self.resource:
            self.data['NAME.E41'] = {
                'branch_lists': self.get_nodes('NAME.E41'),
                'domains': {'NAME_TYPE.E55' : Concept().get_e55_domain('NAME_TYPE.E55')}
            }
            self.data['HERITAGE_PLACE_TYPE.E55'] = {
                'branch_lists': self.get_nodes('HERITAGE_PLACE_TYPE.E55'),
                'domains': {'HERITAGE_PLACE_TYPE.E55' : Concept().get_e55_domain('HERITAGE_PLACE_TYPE.E55')}
            }            
            
            self.data['RIGHT.E30'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes('RIGHT.E30')),
                'domains': {'DESIGNATION_TYPE.E55' : Concept().get_e55_domain('DESIGNATION_TYPE.E55')}
            }
            self.data['DESCRIPTION_ASSIGNMENT.E13'] = {
                'branch_lists': self.get_nodes('DESCRIPTION_ASSIGNMENT.E13'),
                'domains': {
                    'GENERAL_DESCRIPTION_TYPE.E55' : Concept().get_e55_domain('GENERAL_DESCRIPTION_TYPE.E55')
                }
            }
            
class FeatureSummaryForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'summary-feature',
            'icon': 'fa-align-center',
            'name': _('Feature Summary'),
            'class': FeatureSummaryForm
        }

    def update(self, data, files):
        self.update_nodes('NAME.E41', data)
        self.update_nodes('HERITAGE_CLASSIFICATION_TYPE.E55', data)
        self.update_nodes('HERITAGE_FEATURE_USE_TYPE.E55', data)
        self.update_nodes('RIGHT.E30', data)
        self.update_nodes('DESCRIPTION_ASSIGNMENT.E13', data)
        return

    def load(self, lang):
        if self.resource:
            self.data['NAME.E41'] = {
                'branch_lists': self.get_nodes('NAME.E41'),
                'domains': {'NAME_TYPE.E55' : Concept().get_e55_domain('NAME_TYPE.E55')}
            }
            self.data['HERITAGE_CLASSIFICATION_TYPE.E55'] = {
                'branch_lists': self.get_nodes('HERITAGE_CLASSIFICATION_TYPE.E55'),
                'domains': {'HERITAGE_CLASSIFICATION_TYPE.E55' : Concept().get_e55_domain('HERITAGE_CLASSIFICATION_TYPE.E55')}
            }        
            self.data['HERITAGE_FEATURE_USE_TYPE.E55'] = {
                'branch_lists': self.get_nodes('HERITAGE_FEATURE_USE_TYPE.E55'),
                'domains': {'HERITAGE_FEATURE_USE_TYPE.E55' : Concept().get_e55_domain('HERITAGE_FEATURE_USE_TYPE.E55')}
            }               
            
            self.data['RIGHT.E30'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes('RIGHT.E30')),
                'domains': {'DESIGNATION_TYPE.E55' : Concept().get_e55_domain('DESIGNATION_TYPE.E55')}
            }
            self.data['DESCRIPTION_ASSIGNMENT.E13'] = {
                'branch_lists': self.get_nodes('DESCRIPTION_ASSIGNMENT.E13'),
                'domains': {
                    'GENERAL_DESCRIPTION_TYPE.E55' : Concept().get_e55_domain('GENERAL_DESCRIPTION_TYPE.E55')
                }
            }
            
class ComponentClassification(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'component-classification',
            'icon': 'fa-tag',
            'name': _('Component Classification'),
            'class': ComponentClassification
        }

    def update(self, data, files):
        self.update_nodes('COMPONENT_CLASSIFICATION.E17', data)
        return

    def load(self, lang):
        if self.resource:
            self.data['COMPONENT_CLASSIFICATION.E17'] = {
                'branch_lists': self.get_nodes('COMPONENT_CLASSIFICATION.E17'),
                'domains': {
                    'COMPONENT_TYPE.E55' : Concept().get_e55_domain('COMPONENT_TYPE.E55'),
                    'COMPONENT_ORIENTATION.E55' : Concept().get_e55_domain('COMPONENT_ORIENTATION.E55')
                }
            }
            
class ModificationForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'modification',
            'icon': 'fa-plus',
            'name': _('Modification and Construction'),
            'class': ModificationForm
        }

    def update(self, data, files):
        self.update_nodes('MODIFICATION_TYPE.E55', data)
        self.update_nodes('MODIFICATION_DESCRIPTION.E62', data)
        self.update_nodes('CONSTRUCTION_TECHNIQUE_TYPE.E55', data)
        return

    def load(self, lang):
        if self.resource:
            self.data['MODIFICATION_TYPE.E55'] = {
                'branch_lists': datetime_nodes_to_dates(exclude_empty_branches(self.get_nodes('MODIFICATION.E11'),'MODIFICATION_TYPE.E55')),
                'domains': {
                    'MODIFICATION_TYPE.E55' : Concept().get_e55_domain('MODIFICATION_TYPE.E55'),
                }
            }
            
            self.data['MODIFICATION_DESCRIPTION.E62'] = {
                'branch_lists': exclude_empty_branches(self.get_nodes('MODIFICATION.E11'),'MODIFICATION_DESCRIPTION.E62'),
                'domains': {}
            }
            
            self.data['CONSTRUCTION_TECHNIQUE_TYPE.E55'] = {
                'branch_lists': exclude_empty_branches(self.get_nodes('MODIFICATION.E11'),'CONSTRUCTION_TECHNIQUE_TYPE.E55'),
                'domains': {
                    'CONSTRUCTION_TECHNIQUE_TYPE.E55' : Concept().get_e55_domain('CONSTRUCTION_TECHNIQUE_TYPE.E55'),
                    'CONSTRUCTION_MATERIAL.E57' : Concept().get_e55_domain('CONSTRUCTION_MATERIAL.E57')
                }
            }

# --- Assessment  Summary -> AssessmentSummaryForm ------------------------------------------
class AssessmentSummaryForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'assessment-summary',
            'icon': 'fa-users',
            'name': _('Assessment Summary'),
            'class': AssessmentSummaryForm
        }

    def update(self, data, files):
        self.update_nodes('INVESTIGATION_ASSESSMENT_ACTIVITY.E7', data)
        return

    def load(self, lang):
        if self.resource:
            self.data['INVESTIGATION_ASSESSMENT_ACTIVITY.E7'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes('INVESTIGATION_ASSESSMENT_ACTIVITY.E7')),
                'domains': {
                    'INVESTIGATOR_ROLE_TYPE.E55' : Concept().get_e55_domain('INVESTIGATOR_ROLE_TYPE.E55'),
                    'ASSESSMENT_ACTIVITY_TYPE.E55' : Concept().get_e55_domain('ASSESSMENT_ACTIVITY_TYPE.E55'),
                }
            }
            

class ComponentAssessmentForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'component-assessment',
            'icon': 'fa-tag',
            'name': _('Assessment Summary'),
            'class': ComponentAssessmentForm
        }

    def update(self, data, files):
        self.update_nodes('INVESTIGATION_ACTIVITY.E7', data)
        return

    def load(self, lang):
        if self.resource:
            self.data['INVESTIGATION_ACTIVITY.E7'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes('INVESTIGATION_ACTIVITY.E7')),
                'domains': {
                    'INVESTIGATION_ACTIVITY_TYPE.E55' : Concept().get_e55_domain('INVESTIGATION_ACTIVITY_TYPE.E55'),
                    'INVESTIGATOR_ROLE_TYPE.E55' : Concept().get_e55_domain('INVESTIGATOR_ROLE_TYPE.E55')
                }
            }


# --- Measurements -> MeasurementvaluesForm ------------------------------------------
class MeasurementvaluesForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'measurementvalues',
            'icon': 'fa-wrench',
            'name': _('Measurements'),
            'class': MeasurementvaluesForm
    }

    def update(self, data, files):
        self.update_nodes('MEASUREMENTS.E16', data)
    
    def load(self, lang):
        if self.resource:
            self.data['MEASUREMENTS.E16'] = {
                'branch_lists': self.get_nodes('MEASUREMENTS.E16'),
                'domains': {
                    'MEASUREMENT_SOURCE_TYPE.E55' : Concept().get_e55_domain('MEASUREMENT_SOURCE_TYPE.E55'),
                    'MEASUREMENT_UNIT.E58': Concept().get_e55_domain('MEASUREMENT_UNIT.E58'),
                    'DIMENSION_TYPE.E55' : Concept().get_e55_domain('DIMENSION_TYPE.E55')
                 }
            }



# --- Archaeological Assessment (formerly Forms and Interpretations) -> ArchaeologicalAssessmentForm ------------------------------------------
class ArchaeologicalAssessmentForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'archaeological-assessment',
            'icon': 'fa-flag',
            'name': _('Archaeological Assessment'),
            'class': ArchaeologicalAssessmentForm
        }

    def update(self, data, files):
        data = add_actor( 'DATE_INFERENCE_MAKING.I5', 'DATE_INFERENCE_MAKING_ACTOR_NAME.E41', data, self.user)
        data = add_actor( 'FEATURE_ASSIGNMENT.E13', 'FEATURE_ASSIGNMENT_INVESTIGATOR_NAME.E41', data, self.user)
        data = add_actor( 'FUNCTION_INTERPRETATION_INFERENCE_MAKING.I5', 'FUNCTION_INTERPRETATION_INFERENCE_MAKING_ACTOR_NAME.E41', data, self.user)
        
        self.update_nodes('ARCHAEOLOGICAL_CERTAINTY_OBSERVATION.S4', data)
        self.update_nodes('DATE_INFERENCE_MAKING.I5', data)
        self.update_nodes('ARCHAEOLOGICAL_TIMESPAN.E52', data)
        self.update_nodes('FEATURE_ASSIGNMENT.E13', data)
        self.update_nodes('FEATURE_MORPHOLOGY_TYPE.E55', data)
        self.update_nodes('FUNCTION_INTERPRETATION_INFERENCE_MAKING.I5', data)
        return
    
    
    def load(self, lang):
        if self.resource:
            self.data['ARCHAEOLOGICAL_CERTAINTY_OBSERVATION.S4'] = {
                'branch_lists': self.get_nodes('ARCHAEOLOGICAL_CERTAINTY_OBSERVATION.S4'),
                'domains': {
                    'OVERALL_ARCHAEOLOGICAL_CERTAINTY_VALUE.I6' : Concept().get_e55_domain('OVERALL_ARCHAEOLOGICAL_CERTAINTY_VALUE.I6')
                }
            }
            self.data['DATE_INFERENCE_MAKING.I5'] = {
                'branch_lists': self.get_nodes('DATE_INFERENCE_MAKING.I5'),
                'domains': {
                    'CULTURAL_PERIOD_TYPE.I4' : Concept().get_e55_domain('CULTURAL_PERIOD_TYPE.I4'),
                    'CULTURAL_PERIOD_CERTAINTY.I6' : Concept().get_e55_domain('CULTURAL_PERIOD_CERTAINTY.I6'),
                    'CULTURAL_PERIOD_DETAIL_TYPE.E55' : Concept().get_e55_domain('CULTURAL_PERIOD_DETAIL_TYPE.E55'),
                }
            }
            self.data['ARCHAEOLOGICAL_TIMESPAN.E52'] = {
                'branch_lists': self.get_nodes('ARCHAEOLOGICAL_TIMESPAN.E52'),
                'domains': {}
            }
            
            self.data['FEATURE_MORPHOLOGY_TYPE.E55'] = {
                'branch_lists': self.get_nodes('FEATURE_MORPHOLOGY_TYPE.E55'),
                'domains': {
                    'FEATURE_MORPHOLOGY_TYPE.E55' : Concept().get_e55_domain('FEATURE_MORPHOLOGY_TYPE.E55')
                }
            }
            
            self.data['FEATURE_ASSIGNMENT.E13'] = {
                'branch_lists': exclude_empty_branches(self.get_nodes('FEATURE_ASSIGNMENT.E13'),'FEATURE_FORM_TYPE.I4'),
                'domains': {
                    'FEATURE_FORM_TYPE.I4' : Concept().get_e55_domain('FEATURE_FORM_TYPE.I4'),
                    'FEATURE_FORM_TYPE_CERTAINTY.I6' : Concept().get_e55_domain('FEATURE_FORM_TYPE_CERTAINTY.I6'),
                    'FEATURE_SHAPE_TYPE.E55' : Concept().get_e55_domain('FEATURE_SHAPE_TYPE.E55'),
                    'FEATURE_ARRANGEMENT_TYPE.E55' : Concept().get_e55_domain('FEATURE_ARRANGEMENT_TYPE.E55'),
                    'FEATURE_NUMBER_TYPE.E55' : Concept().get_e55_domain('FEATURE_NUMBER_TYPE.E55')
                }
            }
            self.data['FUNCTION_INTERPRETATION_INFERENCE_MAKING.I5'] = {
                'branch_lists': self.get_nodes('FUNCTION_INTERPRETATION_INFERENCE_MAKING.I5'),
                'domains': {
                    'INTERPRETATION_TYPE.I4' : Concept().get_e55_domain('INTERPRETATION_TYPE.I4'),
                    'INTERPRETATION_CERTAINTY.I6' : Concept().get_e55_domain('INTERPRETATION_CERTAINTY.I6'),
                    'INTERPRETATION_NUMBER_TYPE.E55' : Concept().get_e55_domain('INTERPRETATION_NUMBER_TYPE.E55'),
                    'FUNCTION_TYPE.I4' : Concept().get_e55_domain('FUNCTION_TYPE.I4'),
                    'FUNCTION_CERTAINTY.I6' : Concept().get_e55_domain('FUNCTION_CERTAINTY.I6')
                }
            }
            
class FeatureArchaeologicalAssessmentForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'archaeological-assessment-feature',
            'icon': 'fa-flag',
            'name': _('Archaeological Assessment'),
            'class': FeatureArchaeologicalAssessmentForm
        }

    def update(self, data, files):
        data = add_actor('DATE_INTERPRETATION_INFERENCE_MAKING.I5', 'DATE_INTERPRETATION_INFERENCE_MAKING_ACTOR_NAME.E41', data, self.user)
        self.update_nodes('DATE_INTERPRETATION_INFERENCE_MAKING.I5', data)
        
        data = add_actor('FORM_ASSIGNMENT.E13', 'FORM_ASSIGNMENT_INVESTIGATOR_NAME.E41', data, self.user)
        self.update_nodes('FORM_ASSIGNMENT.E13', data)

        return
    
    def load(self, lang):
        if self.resource:

            self.data['DATE_INTERPRETATION_INFERENCE_MAKING.I5'] = {
                'branch_lists': self.get_nodes('DATE_INTERPRETATION_INFERENCE_MAKING.I5'),
                'domains': {
                    'FUNCTION_CERTAINTY.I6' : Concept().get_e55_domain('FUNCTION_CERTAINTY.I6'),
                    'FUNCTION_TYPE.I4' : Concept().get_e55_domain('FUNCTION_TYPE.I4'),
                    'INTERPRETATION_CERTAINTY.I6' : Concept().get_e55_domain('INTERPRETATION_CERTAINTY.I6'),
                    'INTERPRETATION_TYPE.I4' : Concept().get_e55_domain('INTERPRETATION_TYPE.I4'),
                    'CULTURAL_PERIOD_TYPE.I4' : Concept().get_e55_domain('CULTURAL_PERIOD_TYPE.I4'),
                    'CULTURAL_PERIOD_CERTAINTY.I6' : Concept().get_e55_domain('CULTURAL_PERIOD_CERTAINTY.I6'),
                    'CULTURAL_PERIOD_DETAIL_TYPE.E55' : Concept().get_e55_domain('CULTURAL_PERIOD_DETAIL_TYPE.E55')
                }
            }
            
            self.data['FORM_ASSIGNMENT.E13'] = {
                'branch_lists': self.get_nodes('FORM_ASSIGNMENT.E13'),
                'domains': {
                    'FORM_NUMBER.E55' : Concept().get_e55_domain('FORM_NUMBER.E55'),
                    'FORM_ARRANGEMENT.E55' : Concept().get_e55_domain('FORM_ARRANGEMENT.E55'),
                    'FORM_SHAPE_TYPE.E55' : Concept().get_e55_domain('FORM_SHAPE_TYPE.E55'),
                    'FORM_CERTAINTY_BELIEF_VALUE.I6' : Concept().get_e55_domain('FORM_CERTAINTY_BELIEF_VALUE.I6'),
                    'FORM_TYPE_PROPOSITION_SET.I4' : Concept().get_e55_domain('FORM_TYPE_PROPOSITION_SET.I4'),
                }
            }

# --- Condition Assessment -> ConditionAssessmentForm ------------------------------------------
class ConditionAssessmentForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'condition-assessment',
            'icon': 'fa-tasks',
            'name': _('Condition Assessment'),
            'class': ConditionAssessmentForm
        }

    def update(self, data, files):
        data = add_actor('DAMAGE_STATE.E3', 'DISTURBANCE_CAUSE_ASSIGNMENT_ASSESSOR_NAME.E41', data, self.user)
        data = add_actor('THREAT_INFERENCE_MAKING.I5', 'THREAT_INFERENCE_MAKING_ASSESSOR_NAME.E41', data, self.user)
        self.update_nodes('OVERALL_CONDITION_STATE_TYPE.E55', data)
        self.update_nodes('DAMAGE_EXTENT_TYPE.E55', data)
        self.update_nodes('THREAT_INFERENCE_MAKING.I5', data)
        self.update_nodes('DAMAGE_STATE.E3', data)
        self.update_nodes('RECOMMENDATION_PLAN.E100', data)
        self.update_nodes('PRIORITY_ASSIGNMENT.E13', data)
        return
    
    def load(self, lang):
        if self.resource:
            self.data['OVERALL_CONDITION_STATE_TYPE.E55'] = {
                'branch_lists': self.get_nodes('OVERALL_CONDITION_STATE_TYPE.E55'),
                'domains': {
                    'OVERALL_CONDITION_STATE_TYPE.E55' : Concept().get_e55_domain('OVERALL_CONDITION_STATE_TYPE.E55'),
                }
            }

            self.data['DAMAGE_EXTENT_TYPE.E55'] = {
                'branch_lists': self.get_nodes('DAMAGE_EXTENT_TYPE.E55'),
                'domains': {
                    'DAMAGE_EXTENT_TYPE.E55' : Concept().get_e55_domain('DAMAGE_EXTENT_TYPE.E55')
                }
            }

            self.data['THREAT_INFERENCE_MAKING.I5'] = {
                'branch_lists': self.get_nodes('THREAT_INFERENCE_MAKING.I5'),
                'domains': {
                    'THREAT_CATEGORY.I4' : Concept().get_e55_domain('THREAT_CATEGORY.I4'),
                    'THREAT_TYPE.I4' : Concept().get_e55_domain('THREAT_TYPE.I4'),
                    'THREAT_PROBABILITY.I6' : Concept().get_e55_domain('THREAT_PROBABILITY.I6')
                }
            }

            self.data['DAMAGE_STATE.E3'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes('DAMAGE_STATE.E3')),
                'domains': {
                    'DISTURBANCE_CAUSE_CATEGORY_TYPE.E55' : Concept().get_e55_domain('DISTURBANCE_CAUSE_CATEGORY_TYPE.E55'),
                    'DISTURBANCE_CAUSE_TYPE.I4' : Concept().get_e55_domain('DISTURBANCE_CAUSE_TYPE.I4'),
                    'DISTURBANCE_CAUSE_CERTAINTY.I6' : Concept().get_e55_domain('DISTURBANCE_CAUSE_CERTAINTY.I6'),
                    'EFFECT_TYPE.I4' : Concept().get_e55_domain('EFFECT_TYPE.I4'),
                    'EFFECT_CERTAINTY.I6' : Concept().get_e55_domain('EFFECT_CERTAINTY.I6'),
                    'DAMAGE_TREND_TYPE.E55' : Concept().get_e55_domain('DAMAGE_TREND_TYPE.E55'),
                }
            }
            
            self.data['RECOMMENDATION_PLAN.E100'] = {
                'branch_lists': self.get_nodes('RECOMMENDATION_PLAN.E100'),
                'domains': {
                    'RECOMMENDATION_TYPE.E55' : Concept().get_e55_domain('RECOMMENDATION_TYPE.E55'),
                    'INTERVENTION_ACTIVITY_TYPE.E55' : Concept().get_e55_domain('INTERVENTION_ACTIVITY_TYPE.E55'),
                }
            }
            
            self.data['PRIORITY_ASSIGNMENT.E13'] = {
                'branch_lists': self.get_nodes('PRIORITY_ASSIGNMENT.E13'),
                'domains': {
                    'PRIORITY_TYPE.E55' : Concept().get_e55_domain('PRIORITY_TYPE.E55'),
                }
            }

class RelatedFilesForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'related-files',
            'icon': 'fa-file-text-o',
            'name': _('Images and Files'),
            'class': RelatedFilesForm
        }

    def update(self, data, files):
        filedict = {}
        se = SearchEngineFactory().create()
        for name in files:
            for f in files.getlist(name):
                filedict[f.name] = f

        for newfile in data.get('new-files', []):
            if newfile['id'] not in filedict:
                continue
            resource = Resource()
            resource.entitytypeid = 'INFORMATION_RESOURCE.E73'
            resource.set_entity_value('INFORMATION_RESOURCE_TYPE.E55', newfile['title_type']['value'])
            if 'image' in filedict[newfile['id']].content_type:
                resource.set_entity_value('CATALOGUE_ID.E42', newfile['title'])
            else:
                resource.set_entity_value('TITLE.E41', newfile['title'])
            if newfile.get('description') and len(newfile.get('description')) > 0:
#                 resource.set_entity_value('INFORMATION_RESOURCE_TYPE.E55', newfile['description_type']['value'])
                resource.set_entity_value('DESCRIPTION.E62', newfile.get('description'))
            resource.set_entity_value('FILE_PATH.E62', filedict[newfile['id']])            
            thumbnail = generate_thumbnail(filedict[newfile['id']])
            if thumbnail != None:
                resource.set_entity_value('THUMBNAIL.E62', thumbnail)
            resource.save()
            resource.index()
            if self.resource.entityid == '':
                self.resource.save()
            relationship = self.resource.create_resource_relationship(resource.entityid, relationship_type_id=newfile['relationshiptype']['value'])
            se.index_data(index='resource_relations', doc_type='all', body=model_to_dict(relationship), idfield='resourcexid')


        edited_file = data.get('current-files', None)
        if edited_file:
            title = ''
            title_type = ''
            description = ''
            description_type = ''
            is_image = False
            for node in edited_file.get('nodes'):
                if node['entitytypeid'] == 'TITLE.E41' and node.get('value') != '':
                    title = node.get('value')
                if node['entitytypeid'] == 'CATALOGUE_ID.E42' and node.get('value') != '':
                    title = node.get('value')
                    is_image = True
                elif node['entitytypeid'] == 'INFORMATION_RESOURCE_TYPE.E55':
                    title_type = node.get('value')
                elif node['entitytypeid'] == 'DESCRIPTION.E62':
                    description = node.get('value')
                elif node['entitytypeid'] == 'ARCHES_RESOURCE_CROSS-REFERENCE_RELATIONSHIP_TYPES.E55':
                    resourcexid = node.get('resourcexid')            
                    entityid1 = node.get('entityid1')
                    entityid2 = node.get('entityid2')
                    relationship = RelatedResource.objects.get(pk=resourcexid)
                    relationship.relationshiptype = node.get('value')
                    relationship.save()
                    se.delete(index='resource_relations', doc_type='all', id=resourcexid)
                    se.index_data(index='resource_relations', doc_type='all', body=model_to_dict(relationship), idfield='resourcexid')

            relatedresourceid = entityid2 if self.resource.entityid == entityid1 else entityid1
            relatedresource = Resource().get(relatedresourceid)
            relatedresource.set_entity_value('INFORMATION_RESOURCE_TYPE.E55', title_type)
            relatedresource.set_entity_value('CATALOGUE_ID.E42', title) if is_image == True else relatedresource.set_entity_value('TITLE.E41', title)
            if description != '':
#                 relatedresource.set_entity_value('INFORMATION_RESOURCE_TYPE.E55', description_type)
                relatedresource.set_entity_value('DESCRIPTION.E62', description)
            relatedresource.save()
            relatedresource.index()

        return

    def load(self, lang):
        data = []
        for relatedentity in self.resource.get_related_resources(entitytypeid='INFORMATION_RESOURCE.E73'):
            nodes = relatedentity['related_entity'].flatten()
            dummy_relationship_entity = model_to_dict(relatedentity['relationship'])
            dummy_relationship_entity['entitytypeid'] = 'ARCHES_RESOURCE_CROSS-REFERENCE_RELATIONSHIP_TYPES.E55'
            dummy_relationship_entity['value'] = dummy_relationship_entity['relationshiptype']
            dummy_relationship_entity['label'] = ''
            nodes.append(dummy_relationship_entity)
            data.append({'nodes': nodes, 'relationshiptypelabel': get_preflabel_from_valueid(relatedentity['relationship'].relationshiptype, lang)['value']})
        self.data['current-files'] = {
            'branch_lists': data,
            'domains': {
                'RELATIONSHIP_TYPES.E32': Concept().get_e55_domain('ARCHES_RESOURCE_CROSS-REFERENCE_RELATIONSHIP_TYPES.E55'),
                'INFORMATION_RESOURCE_TYPE.E55': Concept().get_e55_domain('INFORMATION_RESOURCE_TYPE.E55'),
            }
        }

        return




class FileUploadForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'file-upload',
            'icon': 'fa-file-text-o',
            'name': _('Other Upload'),
            'class': FileUploadForm
        }
    
    def update(self, data, files):
        self.resource.prune(entitytypes=['FILE_PATH.E62', 'THUMBNAIL.E62'])
        self.resource.trim()

        if files:
            for key, value in files.items():
                self.resource.set_entity_value('FILE_PATH.E62', value)
                thumbnail = generate_thumbnail(value)
                if thumbnail != None:
                    self.resource.set_entity_value('THUMBNAIL.E62', thumbnail)
        return


    def load(self, lang):
        if self.resource:
            self.data['INFORMATION_RESOURCE.E73'] = {
                'branch_lists': self.get_nodes('INFORMATION_RESOURCE.E73'),
#                 'is_image': is_image(self.resource)
            }

        return   



class ManMadeForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'man-made',
            'icon': 'fa-sitemap',
            'name': _('Related Heritage Features'),
            'class': ManMadeForm

        }
        

    def update(self, data, files):
        se = SearchEngineFactory().create()

        resource = Resource()
        resource.entitytypeid = 'HERITAGE_FEATURE.E24'
        self.update_nodes('NAME.E41', data, resource)
        self.update_nodes('INVESTIGATION_ASSESSMENT_ACTIVITY.E7', data, resource)
        self.update_nodes('GEOMETRIC_PLACE_EXPRESSION.SP5', data, resource)
        self.update_nodes('OVERALL_PRIORITY_ASSIGNMENT.E13', data, resource)
        self.update_nodes('CONDITION_REMARKS_ASSIGNMENT.E13', data, resource)
        self.update_nodes('OVERALL_CONDITION_TYPE.E55', data, resource)
        self.update_nodes('HERITAGE_CLASSIFICATION_TYPE.E55', data, resource)
        self.update_nodes('HERITAGE_FEATURE_USE_TYPE.E55', data, resource)
        
        
        resource.save()
        resource.index()
        for relation in data['related-resources']:
            try:
                relation_id=uuid.UUID(relation['nodes'][0]['value'])
            except:
                continue
        relationship = self.resource.create_resource_relationship(resource.entityid, relationship_type_id=relation_id)
        se.index_data(index='resource_relations', doc_type='all', body=model_to_dict(relationship), idfield='resourcexid')

        return

    def update_nodes(self, entitytypeid, data, resource):
        resource.prune(entitytypes=[entitytypeid])
        self.schema = Entity.get_mapping_schema(resource.entitytypeid)

        for value in data[entitytypeid]:
            self.baseentity = None
            for newentity in value['nodes']:
                entity = Entity()
                entity.create_from_mapping(resource.entitytypeid, self.schema[newentity['entitytypeid']]['steps'], newentity['entitytypeid'], newentity['value'], newentity['entityid'])
                if self.baseentity == None:
                    self.baseentity = entity
                else:
                    self.baseentity.merge(entity)

            resource.merge_at(self.baseentity, resource.entitytypeid)

        self.resource.trim()

    def load(self, lang):        
        data = []
        for relatedentity in self.resource.get_related_resources(entitytypeid='HERITAGE_FEATURE.E24'):
            nodes = relatedentity['related_entity'].flatten()
            data.append({
                'nodes': nodes, 
                'relationship': relatedentity['relationship'], 
                'relatedresourcename':relatedentity['related_entity'].get_primary_name(),
                'relatedresourceidlink': '/resources/HERITAGE_FEATURE.E24/default/' + relatedentity['related_entity'].entityid,
                'related': True,
            })

        self.data['related-resources'] = {
            'branch_lists': data,
            'domains': {
                'ARCHES_RESOURCE_CROSS-REFERENCE_RELATIONSHIP_TYPES.E55': Concept().get_e55_domain('ARCHES_RESOURCE_CROSS-REFERENCE_RELATIONSHIP_TYPES.E55')
            },
        }
        geom = self.get_nodes('GEOMETRIC_PLACE_EXPRESSION.SP5')[0]['nodes'][0] if self.get_nodes('GEOMETRIC_PLACE_EXPRESSION.SP5') else ''
        self.data['GEOMETRIC_PLACE_EXPRESSION.SP5'] = {
            'branch_lists': [],
            'domains': {
                'SPATIAL_COORDINATES_REF_SYSTEM.SP4': Concept().get_e55_domain('SPATIAL_COORDINATES_REF_SYSTEM.SP4'),
                'LOCATION_CERTAINTY.I6': Concept().get_e55_domain('LOCATION_CERTAINTY.I6')
            },
            'BingDates': getdates(geom.value) if geom else ''
        }

        self.data['NAME.E41'] = {
            'branch_lists': [],
            'domains': {'NAME_TYPE.E55' : Concept().get_e55_domain('NAME_TYPE.E55')}
        }
        self.data['HERITAGE_FEATURE_USE_TYPE.E55'] = {
            'branch_lists': [],
            'domains': {'HERITAGE_FEATURE_USE_TYPE.E55' : Concept().get_e55_domain('HERITAGE_FEATURE_USE_TYPE.E55')}
        }
        self.data['HERITAGE_CLASSIFICATION_TYPE.E55'] = {
            'branch_lists': [],
            'domains': {'HERITAGE_CLASSIFICATION_TYPE.E55' : Concept().get_e55_domain('HERITAGE_CLASSIFICATION_TYPE.E55')}
        }        
        
        self.data['INVESTIGATION_ASSESSMENT_ACTIVITY.E7'] = {
            'branch_lists': [],
            'domains': {
                'ASSESSMENT_ACTIVITY_TYPE.E55' : Concept().get_e55_domain('ASSESSMENT_ACTIVITY_TYPE.E55'),
                'INVESTIGATOR_ROLE_TYPE.E55' : Concept().get_e55_domain('INVESTIGATOR_ROLE_TYPE.E55'),
            }
        }
        self.data['CONDITION_REMARKS_ASSIGNMENT.E13'] = {
            'branch_lists': [],
            'domains': {
                'OVERALL_CONDITION_REMARKS_TYPE.E55' : Concept().get_e55_domain('OVERALL_CONDITION_REMARKS_TYPE.E55'),
            }
        }
        self.data['OVERALL_PRIORITY_ASSIGNMENT.E13'] = {
            'branch_lists': [],
            'domains': {
                'OVERALL_PRIORITY_TYPE.E55' : Concept().get_e55_domain('OVERALL_PRIORITY_TYPE.E55'),
            }
        }
        self.data['OVERALL_CONDITION_TYPE.E55'] = {
            'branch_lists': [],
            'domains': {
                'OVERALL_CONDITION_TYPE.E55' : Concept().get_e55_domain('OVERALL_CONDITION_TYPE.E55'),
            }
        }      
        return
        
class ManMadeComponentForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'man-made-component',
            'icon': 'fa-sitemap',
            'name': _('Related Heritage Components'),
            'class': ManMadeComponentForm

        }
        
    def update(self, data, files):
        se = SearchEngineFactory().create()

        resource = Resource()
        resource.entitytypeid = 'HERITAGE_COMPONENT.B2'
        self.update_nodes('SPATIAL_COORDINATES.E47', data, resource)
        self.update_nodes('COMPONENT_CLASSIFICATION.E17', data, resource)
        self.update_nodes('INVESTIGATION_ACTIVITY.E7', data, resource)
        
        resource.save()
        resource.index()
        for relation in data['related-resources']:
            try:
                relation_id=uuid.UUID(relation['nodes'][0]['value'])
            except:
                continue
        relationship = self.resource.create_resource_relationship(resource.entityid, relationship_type_id=relation_id)
        se.index_data(index='resource_relations', doc_type='all', body=model_to_dict(relationship), idfield='resourcexid')

        return

    def update_nodes(self, entitytypeid, data, resource):
        resource.prune(entitytypes=[entitytypeid])
        self.schema = Entity.get_mapping_schema(resource.entitytypeid)

        for value in data[entitytypeid]:
            self.baseentity = None
            for newentity in value['nodes']:
                entity = Entity()
                entity.create_from_mapping(resource.entitytypeid, self.schema[newentity['entitytypeid']]['steps'], newentity['entitytypeid'], newentity['value'], newentity['entityid'])
                if self.baseentity == None:
                    self.baseentity = entity
                else:
                    self.baseentity.merge(entity)

            resource.merge_at(self.baseentity, resource.entitytypeid)

        self.resource.trim()

    def load(self, lang):        
        data = []
        for relatedentity in self.resource.get_related_resources(entitytypeid='HERITAGE_COMPONENT.B2'):
            nodes = relatedentity['related_entity'].flatten()
            data.append({
                'nodes': nodes, 
                'relationship': relatedentity['relationship'], 
                'relatedresourcename':relatedentity['related_entity'].get_primary_name(),
                'relatedresourceidlink': '/resources/HERITAGE_COMPONENT.B2/default/' + relatedentity['related_entity'].entityid,
                'related': True,
            })

        self.data['related-resources'] = {
            'branch_lists': data,
            'domains': {
                'ARCHES_RESOURCE_CROSS-REFERENCE_RELATIONSHIP_TYPES.E55': Concept().get_e55_domain('ARCHES_RESOURCE_CROSS-REFERENCE_RELATIONSHIP_TYPES.E55')
            },
        }
        geom = self.get_nodes('SPATIAL_COORDINATES.E47')[0]['nodes'][0] if self.get_nodes('SPATIAL_COORDINATES.E47') else ''
        self.data['SPATIAL_COORDINATES.E47'] = {
            'branch_lists': [],
            'domains': {
                'GEOMETRY_TYPE.E55': Concept().get_e55_domain('GEOMETRY_TYPE.E55')
            },
            'BingDates': getdates(geom.value) if geom else ''
        }

        self.data['COMPONENT_CLASSIFICATION.E17'] = {
            'branch_lists': [],
            'domains': {
                'COMPONENT_TYPE.E55' : Concept().get_e55_domain('COMPONENT_TYPE.E55'),
                'COMPONENT_ORIENTATION.E55' : Concept().get_e55_domain('COMPONENT_ORIENTATION.E55')
            }
        }

        self.data['INVESTIGATION_ACTIVITY.E7'] = {
            'branch_lists': [],
            'domains': {
                'INVESTIGATOR_ROLE_TYPE.E55' : Concept().get_e55_domain('INVESTIGATOR_ROLE_TYPE.E55'),
                'INVESTIGATION_ACTIVITY_TYPE.E55' : Concept().get_e55_domain('INVESTIGATION_ACTIVITY_TYPE.E55')
            }
        }        
        
        return
        
class FeatureConditionAssessmentForm(ResourceForm):

    @staticmethod
    def get_info():
        return {
            'id': 'condition-assessment-feature',
            'icon': 'fa-adjust',
            'name': _('Condition Assessment'),
            'class': FeatureConditionAssessmentForm
        }


    def update(self, data, files):
        data = add_actor( 'DAMAGE_STATE.E3', 'DISTURBANCE_CAUSE_ASSIGNMENT_ASSESSOR_NAME.E41', data, self.user)
        data = add_actor( 'POTENTIAL_STATE_PREDICTION.XX1', 'RISK_EVALUATION_ASSESSOR_NAME.E41', data, self.user)
        ## step 1
        self.update_nodes('DAMAGE_STATE.E3',data)
        self.update_nodes('OVERALL_DAMAGE_SEVERITY_TYPE.E55', data)
        self.update_nodes('DAMAGE_EXTENT_TYPE.E55', data)
        self.update_nodes('RECOMMENDATION_PLAN.E100',data)
        
        ## step 2
        self.update_nodes('POTENTIAL_STATE_PREDICTION.XX1',data)
        self.update_nodes('RISK_PLAN.E100',data)
        
        ## step 3
        self.update_nodes('OVERALL_CONDITION_TYPE.E55',data)

    def load(self, lang):
        if self.resource:
            self.data['DAMAGE_STATE.E3'] = {
                'branch_lists': datetime_nodes_to_dates(exclude_empty_branches(self.get_nodes('DAMAGE_STATE.E3'), 'DISTURBANCE_EVENT.E5')),
                'domains': {
                    'DISTURBANCE_CAUSE_CATEGORY_TYPE.E55' : Concept().get_e55_domain('DISTURBANCE_CAUSE_CATEGORY_TYPE.E55'),
                    'DISTURBANCE_CAUSE_TYPE.I4' : Concept().get_e55_domain('DISTURBANCE_CAUSE_TYPE.I4'),
                    'DISTURBANCE_CAUSE_CERTAINTY.I6' : Concept().get_e55_domain('DISTURBANCE_CAUSE_CERTAINTY.I6'),
                    'EFFECT_TYPE.S9' : Concept().get_e55_domain('EFFECT_TYPE.S9'),
                    'DAMAGE_TREND_TYPE.E55' : Concept().get_e55_domain('DAMAGE_TREND_TYPE.E55'),
                }
            }
            self.data['OVERALL_DAMAGE_SEVERITY_TYPE.E55'] = {
                'branch_lists': self.get_nodes('OVERALL_DAMAGE_SEVERITY_TYPE.E55'),
                'domains': {
                    'OVERALL_DAMAGE_SEVERITY_TYPE.E55' : Concept().get_e55_domain('OVERALL_DAMAGE_SEVERITY_TYPE.E55'),
                }
            }
            self.data['DAMAGE_EXTENT_TYPE.E55'] = {
                'branch_lists': self.get_nodes('DAMAGE_EXTENT_TYPE.E55'),
                'domains': {
                    'DAMAGE_EXTENT_TYPE.E55' : Concept().get_e55_domain('DAMAGE_EXTENT_TYPE.E55'),
                }
            }
            self.data['RECOMMENDATION_PLAN.E100'] = {
                'branch_lists': self.get_nodes('RECOMMENDATION_PLAN.E100'),
                'domains': {
                    'RECOMMENDATION_TYPE.E55' : Concept().get_e55_domain('RECOMMENDATION_TYPE.E55'),
                    'INTERVENTION_ACTIVITY_TYPE.E55' : Concept().get_e55_domain('INTERVENTION_ACTIVITY_TYPE.E55'),
                    'PRIORITY_TYPE.E55' : Concept().get_e55_domain('PRIORITY_TYPE.E55'),
                }                
            }         
            self.data['POTENTIAL_STATE_PREDICTION.XX1'] = {
                'branch_lists': exclude_empty_branches(self.get_nodes('POTENTIAL_STATE_PREDICTION.XX1'), 'POTENTIAL_IMPACT_TYPE.E55'),
                'domains': {
                    'THREAT_TYPE.E55' : Concept().get_e55_domain('THREAT_TYPE.E55'),
                    'POTENTIAL_IMPACT_TYPE.E55' : Concept().get_e55_domain('POTENTIAL_IMPACT_TYPE.E55'),
#                     'SECONDARY_THREAT_TYPE.E55' : Concept().get_e55_domain('SECONDARY_THREAT_TYPE.E55'),
                    'VULNERABILITY_TYPE.E55' : Concept().get_e55_domain('VULNERABILITY_TYPE.E55'),
                    'THREAT_PROBABILITY_TYPE.E55' : Concept().get_e55_domain('THREAT_PROBABILITY_TYPE.E55'),
                    'RISK_EXTENT_TYPE.E55' : Concept().get_e55_domain('RISK_EXTENT_TYPE.E55'),
                    'RISK_SEVERITY_TYPE.E55' : Concept().get_e55_domain('RISK_SEVERITY_TYPE.E55'),
                    'RISK_LEVEL.I4' : Concept().get_e55_domain('RISK_LEVEL.I4'),
                    'RISK_LEVEL_CERTAINTY.I6' : Concept().get_e55_domain('RISK_LEVEL_CERTAINTY.I6'),
                }
            }     
            self.data['RISK_PLAN.E100'] = {
                'branch_lists': exclude_empty_branches(self.get_nodes('RISK_PLAN.E100'), 'MITIGATION_STRATEGY_TYPE.E55'),
                'domains': {
                    'MITIGATION_STRATEGY_TYPE.E55' : Concept().get_e55_domain('MITIGATION_STRATEGY_TYPE.E55'),
                    'MITIGATION_PRIORITY_TYPE.E55' : Concept().get_e55_domain('MITIGATION_PRIORITY_TYPE.E55'),
                }
            }                 
            self.data['OVERALL_CONDITION_TYPE.E55'] = {
                'branch_lists': self.get_nodes( 'OVERALL_CONDITION_TYPE.E55'),
                'domains': {
                    'OVERALL_CONDITION_TYPE.E55' : Concept().get_e55_domain('OVERALL_CONDITION_TYPE.E55')
                }
            }     
            self.data['OVERALL_PRIORITY_TYPE.E55'] = {
                'branch_lists': self.get_nodes( 'OVERALL_PRIORITY_TYPE.E55'),
                'domains': {
                    'OVERALL_PRIORITY_TYPE.E55' : Concept().get_e55_domain('OVERALL_PRIORITY_TYPE.E55')
                }
            }                            
            self.data['NEXT_ASSESSMENT_DATE_TYPE.E55'] = {
                'branch_lists': self.get_nodes( 'NEXT_ASSESSMENT_DATE_TYPE.E55'),
                'domains': {
                    'NEXT_ASSESSMENT_DATE_TYPE.E55' : Concept().get_e55_domain('NEXT_ASSESSMENT_DATE_TYPE.E55')
                }
            }
            self.data['CONDITION_REMARKS_ASSIGNMENT.E13'] = {
                'branch_lists': self.get_nodes('CONDITION_REMARKS_ASSIGNMENT.E13'),
                'domains': {
                    'OVERALL_CONDITION_REMARKS_TYPE.E55' : Concept().get_e55_domain('OVERALL_CONDITION_REMARKS_TYPE.E55')
                }
            }
               
class ExternalReferenceForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'external-reference',
            'icon': 'fa-random',
            'name': _('URLs'),
            'class': ExternalReferenceForm
        }

    def update(self, data, files):
        URLValidation = re.compile(r"(([a-z]{3,6}://)|(^|\s))([a-zA-Z0-9\-]+\.)+[a-z]{2,13}[\.\?\=\&\%\/\w\-]*\b([^@]|$)") #Main URL validation to make sure data includes a real URL
        for branch in data['URL.E51']:
            for node in branch['nodes']:
                if node['entitytypeid'] == 'URL.E51':
                    if URLValidation.match(node['value']) != None: # Checks if string is URL
                        if node['value'][0:4] != 'http': #If string is a URL, but it doesn't begin with the http protocol, it adds http:// at the beginning of the string
                            node['value'] = "http://" + node['value']
                    else: # If not, it removes the branch from the branch list.
                        data['URL.E51'].remove(branch)
                    
                                                
        self.update_nodes('URL.E51', data)
        return

    def load(self, lang):
        if self.resource:
            self.data['URL.E51'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes('URL.E51')),
                'domains': {

                }
            }


class ActivityActionsForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'activity-actions',
            'icon': 'fa-flash',
            'name': _('Actions'),
            'class': ActivityActionsForm
        }

    def update(self, data, files):
        self.update_nodes('PHASE_TYPE_ASSIGNMENT.E17', data)
        return

    def load(self, lang):

        if self.resource:
            phase_type_nodes = datetime_nodes_to_dates(self.get_nodes('PHASE_TYPE_ASSIGNMENT.E17'))

            self.data['PHASE_TYPE_ASSIGNMENT.E17'] = {
                'branch_lists': phase_type_nodes,
                'domains': {
                    'ACTIVITY_TYPE.E55': Concept().get_e55_domain('ACTIVITY_TYPE.E55'),
                }
            }

class ActivitySummaryForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'activity-summary',
            'icon': 'fa-tag',
            'name': _('Resource Summary'),
            'class': ActivitySummaryForm
        }

    def update(self, data, files):
        self.update_nodes('NAME.E41', data)
        self.update_nodes('KEYWORD.E55', data)
        self.update_nodes('BEGINNING_OF_EXISTENCE.E63', data)
        self.update_nodes('END_OF_EXISTENCE.E64', data)

    def load(self, lang):
        if self.resource:

            self.data['NAME.E41'] = {
                'branch_lists': self.get_nodes('NAME.E41'),
                'domains': {'NAME_TYPE.E55' : Concept().get_e55_domain('NAME_TYPE.E55')}
            }

            self.data['KEYWORD.E55'] = {
                'branch_lists': self.get_nodes('KEYWORD.E55'),
                'domains': {'KEYWORD.E55' : Concept().get_e55_domain('KEYWORD.E55')}
            }

            self.data['BEGINNING_OF_EXISTENCE.E63'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes('BEGINNING_OF_EXISTENCE.E63')),
                'domains': {
                    'BEGINNING_OF_EXISTENCE_TYPE.E55' : Concept().get_e55_domain('BEGINNING_OF_EXISTENCE_TYPE.E55')
                }
            }

            self.data['END_OF_EXISTENCE.E64'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes('END_OF_EXISTENCE.E64')),
                'domains': {
                    'END_OF_EXISTENCE_TYPE.E55' : Concept().get_e55_domain('END_OF_EXISTENCE_TYPE.E55')
                }
            }
            try:
                self.data['primaryname_conceptid'] = self.data['NAME.E41']['domains']['NAME_TYPE.E55'][3]['id']
            except IndexError:
                pass






class HistoricalEventSummaryForm(ActivitySummaryForm):
    @staticmethod
    def get_info():
        return {
            'id': 'historical-event-summary',
            'icon': 'fa-tag',
            'name': _('Resource Summary'),
            'class': HistoricalEventSummaryForm
        }    

class InformationResourceSummaryForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'information-resource-summary',
            'icon': 'fa-tag',
            'name': _('Resource Type'),
            'class': InformationResourceSummaryForm
        }   

    def update(self, data, files):
        self.update_nodes('INFORMATION_RESOURCE_TYPE.E55', data)
        self.update_nodes('INFORMATION_CARRIER.E84', data)


    def load(self, lang):
        if self.resource:


            self.data['INFORMATION_CARRIER.E84'] = {
                'branch_lists': self.get_nodes('INFORMATION_CARRIER.E84'),
                'domains': {
                    'INFORMATION_CARRIER_FORMAT_TYPE.E55' : Concept().get_e55_domain('INFORMATION_CARRIER_FORMAT_TYPE.E55')
                }
            }


            self.data['INFORMATION_RESOURCE_TYPE.E55'] = {
                'branch_lists': self.get_nodes('INFORMATION_RESOURCE_TYPE.E55'),
                'domains': {
                    'INFORMATION_RESOURCE_TYPE.E55' : Concept().get_e55_domain('INFORMATION_RESOURCE_TYPE.E55')
                }
            }

            # self.data['primaryname_conceptid'] = self.data['TITLE.E41']['domains']['TITLE_TYPE.E55'][3]['id']
 




class MeasurementForm(ResourceForm):

            
    @staticmethod
    def get_info():
        return {
            'id': 'measurement',
            'icon': 'fa-th-large',
            'name': _('Condition Assessment'),
            'class': MeasurementForm
        }

    def update(self, data, files):
        self.update_nodes('DISTURBANCE_STATE.E3', data)
        self.update_nodes('DISTURBANCE_EXTENT_TYPE.E55', data)
        self.update_nodes('CONDITION_TYPE.E55', data)
        self.update_nodes('THREAT_STATE.E3', data)
        return
    
    def load(self, lang):
        if self.resource:
            self.data['DISTURBANCE_STATE.E3'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes_hierarchical('DISTURBANCE_STATE.E3', 'DISTURBANCE_EFFECT_STATE.E3')),
                'domains': {
                    'DISTURBANCE_CAUSE_TYPE.E55' : Concept().get_e55_domain('DISTURBANCE_CAUSE_TYPE.E55'),
                    'DISTURBANCE_CAUSE_CERTAINTY_TYPE.E55': Concept().get_e55_domain('DISTURBANCE_CAUSE_CERTAINTY_TYPE.E55'),
                    'DISTURBANCE_EFFECT_1_TYPE.E55' : Concept().get_e55_domain('DISTURBANCE_EFFECT_1_TYPE.E55'),
                    'DISTURBANCE_EFFECT_1_CERTAINTY_TYPE.E55': Concept().get_e55_domain('DISTURBANCE_EFFECT_1_CERTAINTY_TYPE.E55'),
                    'DISTURBANCE_TYPE.E55' : Concept().get_e55_domain('DISTURBANCE_TYPE.E55'),
                    'DISTURBANCE_DATE_TYPE.E55' : Concept().get_e55_domain('DISTURBANCE_DATE_TYPE.E55'),
                    'DISTURBANCE_DATE_START.E49' : Concept().get_e55_domain('DISTURBANCE_DATE_START.E49'),
                    'DISTURBANCE_DATE_END.E49' : Concept().get_e55_domain('DISTURBANCE_DATE_END.E49'),
                }
            }
            
            self.data['THREAT_STATE.E3'] = {
                'branch_lists': self.get_nodes('THREAT_STATE.E3'),
                'domains': {
                    'THREAT_CAUSE_CERTAINTY_TYPE.E55' : Concept().get_e55_domain('THREAT_CAUSE_CERTAINTY_TYPE.E55'),
                    'THREAT_CAUSE_TYPE.E55' : Concept().get_e55_domain('THREAT_CAUSE_TYPE.E55'),
                    'THREAT_CERTAINTY_TYPE.E55' : Concept().get_e55_domain('THREAT_CERTAINTY_TYPE.E55'),
                    'THREAT_TYPE.E55' : Concept().get_e55_domain('THREAT_TYPE.E55'),                }
            }
            
            self.data['DISTURBANCE_EXTENT_TYPE.E55'] = {
                'branch_lists': self.get_nodes('DISTURBANCE_EXTENT_TYPE.E55'),
                'domains': {
                    'DISTURBANCE_EXTENT_TYPE.E55' : Concept().get_e55_domain('DISTURBANCE_EXTENT_TYPE.E55'),
                }
            }

            
            self.data['CONDITION_TYPE.E55'] = {
                'branch_lists': self.get_nodes('CONDITION_TYPE.E55'),
                'domains': {
                    'CONDITION_TYPE.E55' : Concept().get_e55_domain('CONDITION_TYPE.E55'),
                }
            }

class Classification1Form(ResourceForm):
    
    
    @staticmethod
    def get_info():
        return {
            'id': 'class',
            'icon': 'fa-th-large',
            'name': _('Forms and Interpretations'),
            'class': Classification1Form
        }

    def update(self, data, files):
        self.update_nodes('FEATURE_EVIDENCE_ASSIGNMENT.E17', data)
        self.update_nodes('FEATURE_EVIDENCE_INTERPRETATION_ASSIGNMENT.E17', data)
        return
    
    def load(self, lang):
        if self.resource:
            self.data['FEATURE_EVIDENCE_ASSIGNMENT.E17'] = {
                'branch_lists': self.get_nodes('FEATURE_EVIDENCE_ASSIGNMENT.E17'),
                'domains': {
                    'FEATURE_EVIDENCE_TYPE.E55' : Concept().get_e55_domain('FEATURE_EVIDENCE_TYPE.E55'),
                    'FEATURE_EVIDENCE_TYPE_CERTAINTY_TYPE.E55': Concept().get_e55_domain('FEATURE_EVIDENCE_TYPE_CERTAINTY_TYPE.E55'),
                    'FEATURE_EVIDENCE_SHAPE_TYPE.E55' : Concept().get_e55_domain('FEATURE_EVIDENCE_SHAPE_TYPE.E55'),
                    'FEATURE_EVIDENCE_ARRANGEMENT_TYPE.E55': Concept().get_e55_domain('FEATURE_EVIDENCE_ARRANGEMENT_TYPE.E55'),
                    'FEATURE_EVIDENCE_NUMBER_TYPE.E55' : Concept().get_e55_domain('FEATURE_EVIDENCE_NUMBER_TYPE.E55'),
                }
            }
        
            self.data['FEATURE_EVIDENCE_INTERPRETATION_ASSIGNMENT.E17'] = {
                'branch_lists': self.get_nodes('FEATURE_EVIDENCE_INTERPRETATION_ASSIGNMENT.E17'),
                'domains': {
                    'FEATURE_EVIDENCE_INTERPRETATION_TYPE.E55' : Concept().get_e55_domain('FEATURE_EVIDENCE_INTERPRETATION_TYPE.E55'),
                    'FEATURE_EVIDENCE_INTERPRETATION_CERTAINTY_TYPE.E55': Concept().get_e55_domain('FEATURE_EVIDENCE_INTERPRETATION_CERTAINTY_TYPE.E55'),
                    'FEATURE_EVIDENCE_INTERPRETATION_NUMBER_TYPE.E55' : Concept().get_e55_domain('FEATURE_EVIDENCE_INTERPRETATION_NUMBER_TYPE.E55'),
                }
            }



class LocationForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'location',
            'icon': 'fa-map-marker',
            'name': _('Location'),
            'class': LocationForm
        }

    def update(self, data, files):

        self.update_nodes('GEOMETRIC_PLACE_EXPRESSION.SP5', data)
        self.update_nodes('GEOMETRY_EXTENT_CERTAINTY.I6', data)

        self.update_nodes('GRID_ID.E42', data)
        self.update_nodes('SITE_OVERALL_SHAPE_TYPE.E55', data)
        
        self.update_nodes('TOPOGRAPHY_TYPE.E55', data)
        self.update_nodes('ADMINISTRATIVE_DIVISION.E53', data)
        self.update_nodes('ADDRESS.E45', data)
        self.update_nodes('CADASTRAL_REFERENCE.E44', data)        
        
        return

    def load(self, lang):
    
        geom = self.get_nodes('GEOMETRIC_PLACE_EXPRESSION.SP5')[0]['nodes'][0] if self.get_nodes('GEOMETRIC_PLACE_EXPRESSION.SP5') else ''
        self.data['GEOMETRIC_PLACE_EXPRESSION.SP5'] = {
            'branch_lists': self.get_nodes('GEOMETRIC_PLACE_EXPRESSION.SP5'),
            'domains': {
                'LOCATION_CERTAINTY.I6': Concept().get_e55_domain('LOCATION_CERTAINTY.I6')
            },
            'BingDates': getdates(geom.value) if geom else ''
        }
        
        
        
        self.data['GEOMETRY_EXTENT_CERTAINTY.I6'] = {
            'branch_lists': self.get_nodes('GEOMETRY_EXTENT_CERTAINTY.I6'),
            'domains': {
                'GEOMETRY_EXTENT_CERTAINTY.I6': Concept().get_e55_domain('GEOMETRY_EXTENT_CERTAINTY.I6')
            }
        }
        
        self.data['GRID_ID.E42'] = {
                'branch_lists': self.get_nodes('GRID_ID.E42'),
                'domains': {}
        }
            
        self.data['SITE_OVERALL_SHAPE_TYPE.E55'] = {
            'branch_lists': self.get_nodes('SITE_OVERALL_SHAPE_TYPE.E55'),
            'domains': {
                'SITE_OVERALL_SHAPE_TYPE.E55': Concept().get_e55_domain('SITE_OVERALL_SHAPE_TYPE.E55')
            }
        }
        
        self.data['TOPOGRAPHY_TYPE.E55'] = {
            'branch_lists': self.get_nodes('TOPOGRAPHY_TYPE.E55'),
            'domains': {
                'TOPOGRAPHY_TYPE.E55': Concept().get_e55_domain('TOPOGRAPHY_TYPE.E55')
            }
        }



        self.data['ADMINISTRATIVE_DIVISION.E53'] = {
            'branch_lists': self.get_nodes('ADMINISTRATIVE_DIVISION.E53'),
            'domains': {
                'ADMINISTRATIVE_DIVISION_TYPE.E55': Concept().get_e55_domain('ADMINISTRATIVE_DIVISION_TYPE.E55'),
                
            }
        }

        self.data['ADDRESS.E45'] = {
            'branch_lists': self.get_nodes('ADDRESS.E45'),
            'domains': {
                'ADDRESS_TYPE.E55': Concept().get_e55_domain('ADDRESS_TYPE.E55'),
            }
        }

        self.data['CADASTRAL_REFERENCE.E44'] = {
            'branch_lists': self.get_nodes('CADASTRAL_REFERENCE.E44'),
            'domains': {
                'CADASTRAL_REFERENCE.E44': Concept().get_e55_domain('CADASTRAL_REFERENCE.E44'),
            }
        }
        
        
        self.data['ADMINISTRATIVE_DIVISION.E53'] = {
            'branch_lists': self.get_nodes('ADMINISTRATIVE_DIVISION.E53'),
            'domains': {
                'ADMINISTRATIVE_DIVISION_TYPE.E55': Concept().get_e55_domain('ADMINISTRATIVE_DIVISION_TYPE.E55')
            }
        }


        return

class ComponentLocationForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'location-component',
            'icon': 'fa-map-marker',
            'name': _('Location'),
            'class': ComponentLocationForm
        }

    def update(self, data, files):

        self.update_nodes('SPATIAL_COORDINATES.E47', data)
        
        return

    def load(self, lang):
    
        geom = self.get_nodes('SPATIAL_COORDINATES.E47')[0]['nodes'][0] if self.get_nodes('SPATIAL_COORDINATES.E47') else ''
        self.data['SPATIAL_COORDINATES.E47'] = {
            'branch_lists': self.get_nodes('SPATIAL_COORDINATES.E47'),
            'domains': {
                'GEOMETRY_TYPE.E55': Concept().get_e55_domain('GEOMETRY_TYPE.E55'),
            },
            'BingDates': getdates(geom.value) if geom else ''
        }

class CoverageForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'coverage',
            'icon': 'fa-crosshairs',
            'name': _('Geometry Upload'),
            'class': CoverageForm
        }

    def update(self, data, files):
        self.update_nodes('SPATIAL_COORDINATES_GEOMETRY.E47', data)
        return

    def load(self, lang):
        geom = self.get_nodes('SPATIAL_COORDINATES_GEOMETRY.E47')[0]['nodes'][0] if self.get_nodes('SPATIAL_COORDINATES_GEOMETRY.E47') else ''
        self.data['SPATIAL_COORDINATES_GEOMETRY.E47'] = {
            'branch_lists': self.get_nodes('SPATIAL_COORDINATES_GEOMETRY.E47'),
            'domains': {
            },
            'BingDates': getdates(geom.value) if geom else ''
        }
        

        return






class ActorSummaryForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'actor-summary',
            'icon': 'fa-tag',
            'name': _('Actor Summary'),
            'class': ActorSummaryForm
        }

    def update(self, data, files):
        self.update_nodes('ACTOR_APPELLATION.E82', data)
        self.update_nodes('ORGANISATION_TYPE.E55', data)
        self.update_nodes('MODERN_COUNTRY_TERRITORY.E55', data)
        return
        
    def load(self, lang):
        if self.resource:
            self.data['ACTOR_APPELLATION.E82'] = {
                'branch_lists': self.get_nodes('ACTOR_APPELLATION.E82'),
                'domains': {
                }
            }
            self.data['ORGANISATION_TYPE.E55'] = {
                'branch_lists': self.get_nodes('ORGANISATION_TYPE.E55'),
                'domains': {
                    'ORGANISATION_TYPE.E55': Concept().get_e55_domain('ORGANISATION_TYPE.E55')
                }
            }
            self.data['MODERN_COUNTRY_TERRITORY.E55'] = {
                'branch_lists': self.get_nodes('MODERN_COUNTRY_TERRITORY.E55'),
                'domains': {
                    'MODERN_COUNTRY_TERRITORY.E55': Concept().get_e55_domain('MODERN_COUNTRY_TERRITORY.E55')
                }
            }

class PhaseForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'phase',
            'icon': 'fa-flash',
            'name': _('Phase'),
            'class': PhaseForm
        }

    def update(self, data, files):
        self.update_nodes('PHASE_TYPE_ASSIGNMENT.E17', data)
        return


    def load(self, lang):
        if self.resource:
            self.data['PHASE_TYPE_ASSIGNMENT.E17'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes('PHASE_TYPE_ASSIGNMENT.E17')),
                'domains': {
                    'HISTORICAL_EVENT_TYPE.E55' : Concept().get_e55_domain('HISTORICAL_EVENT_TYPE.E55'),
                    'CULTURAL_PERIOD.E55' : Concept().get_e55_domain('CULTURAL_PERIOD.E55')
                }
            }

        return



class RelatedResourcesForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'related-resources',
            'icon': 'fa-exchange',
            'name': _('Related Resources'),
            'class': RelatedResourcesForm
        }

    def update(self, data, files):
        logging.warning('------> RelatedResourcesForm update1: %s', JSONResponse(data, indent=4))
        se = SearchEngineFactory().create()
        related_resources_data = data.get('related-resources', [])
        original_relations = self.resource.get_related_resources()
        if self.resource.entityid == '':
            self.resource.save()
        relationship_ids = []

        for related_resource in related_resources_data:
            relationship_id = related_resource['relationship']['resourcexid']
            relationship_ids.append(relationship_id)
            resource_id = related_resource['relatedresourceid']
            relationship_type_id = related_resource['relationship']['relationshiptype']
            if isinstance(relationship_type_id, dict):
                relationship_type_id = relationship_type_id['value']
            notes = related_resource['relationship']['notes']
            date_started = related_resource['relationship']['datestarted']
            date_ended = related_resource['relationship']['dateended']
            if not relationship_id:
                relationship = self.resource.create_resource_relationship(resource_id, relationship_type_id=relationship_type_id, notes=notes, date_started=date_started, date_ended=date_ended)
            else:
                relationship = RelatedResource.objects.get(pk=relationship_id)
                relationship.relationshiptype = relationship_type_id
                relationship.notes = notes
                relationship.datestarted = date_started
                relationship.dateended = date_ended
                relationship.save()
                se.delete(index='resource_relations', doc_type='all', id=relationship_id)
            se.index_data(index='resource_relations', doc_type='all', body=model_to_dict(relationship), idfield='resourcexid')

        for relatedentity in original_relations:
            if relatedentity['relationship'].resourcexid not in relationship_ids:
                se.delete(index='resource_relations', doc_type='all', id=relatedentity['relationship'].resourcexid)
                relatedentity['relationship'].delete()

    def load(self, lang):
        data = []
        for relatedentity in self.resource.get_related_resources():
            nodes = relatedentity['related_entity'].flatten()

            data.append({
                'nodes': nodes, 
                'relationship': relatedentity['relationship'], 
                'relationshiptypelabel': get_preflabel_from_valueid(relatedentity['relationship'].relationshiptype, lang)['value'],
                'relatedresourcename':relatedentity['related_entity'].get_primary_name(),
                'relatedresourcetype':relatedentity['related_entity'].entitytypeid,
                'relatedresourceid':relatedentity['related_entity'].entityid,
                'related': True,
            })

        relationship_types = Concept().get_e55_domain('ARCHES_RESOURCE_CROSS-REFERENCE_RELATIONSHIP_TYPES.E55')

#         try:
#             default_relationship_type = relationship_types[0]['id']
#             if len(relationship_types) > 6:
#                 default_relationship_type = relationship_types[6]['id']

        self.data['related-resources'] = {
            'branch_lists': data,
            'domains': {
                'RELATIONSHIP_TYPES.E32': relationship_types
            },
#                 'default_relationship_type':  default_relationship_type
        }
        self.data['resource-id'] = self.resource.entityid
        
        return


class PublicationForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'publication',
            'icon': 'fa-flash',
            'name': _('Bibliography'),
            'class': PublicationForm
        }

    def update(self, data, files):
        self.update_nodes('CREATOR_APPELLATION.E82', data)
        self.update_nodes('EDITOR_APPELLATION.E82', data)
        self.update_nodes('TITLE.E41', data)
        self.update_nodes('SOURCE_APPELLATION.E82', data)
        self.update_nodes('BIBLIO_PLACE_APPELLATION.E44', data)
        self.update_nodes('PUBLISHER_APPELLATION.E82', data)
        self.update_nodes('VOLUME.E62', data)
        self.update_nodes('ISSUE.E62', data)
        self.update_nodes('PAGES.E62', data)
        self.update_nodes('FIGURE.E62', data)
        self.update_nodes('DATE_OF_PUBLICATION.E50', data)

        
        return

    def load(self, lang):
        if self.resource:
            
            self.data['TITLE.E41'] = {
                'branch_lists': self.get_nodes('TITLE.E41'),
                'domains': {'TITLE_TYPE.E55' : Concept().get_e55_domain('TITLE_TYPE.E55')
                 }
            }
            
            self.data['CREATOR_APPELLATION.E82'] = {
                'branch_lists': self.get_nodes('CREATOR_APPELLATION.E82'),
                'domains': {
                }
            }
            
            self.data['EDITOR_APPELLATION.E82'] = {
                'branch_lists': self.get_nodes('EDITOR_APPELLATION.E82'),
                'domains': {
                }
            }

            self.data['SOURCE_APPELLATION.E82'] = {
                'branch_lists': self.get_nodes('SOURCE_APPELLATION.E82'),
                'domains': {
                }
            }
            
            self.data['BIBLIO_PLACE_APPELLATION.E44'] = {
                'branch_lists': self.get_nodes('BIBLIO_PLACE_APPELLATION.E44'),
                'domains': {
                }
            }

            self.data['PUBLISHER_APPELLATION.E82'] = {
                'branch_lists': self.get_nodes('PUBLISHER_APPELLATION.E82'),
                'domains': {
                }
            }
            
            self.data['VOLUME.E62'] = {
                'branch_lists': self.get_nodes('VOLUME.E62'),
                'domains': {
                }
            }

            self.data['ISSUE.E62'] = {
                'branch_lists': self.get_nodes('ISSUE.E62'),
                'domains': {
                }
            }
            
            self.data['PAGES.E62'] = {
                'branch_lists': self.get_nodes('PAGES.E62'),
                'domains': {
                }
            }
                
            self.data['FIGURE.E62'] = {
                'branch_lists': self.get_nodes('FIGURE.E62'),
                'domains': {
                }
            }
            
            self.data['DATE_OF_PUBLICATION.E50'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes('DATE_OF_PUBLICATION.E50')),
                'domains': {
                }
            }

        return


class SharedDataForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'SharedData',
            'icon': 'fa-flash',
            'name': _('Shared Data'),
            'class': SharedDataForm
        }

    def update(self, data, files):
        self.update_nodes('SHARED_DATA_SOURCE_APPELLATION.E82', data)
        self.update_nodes('SHARED_DATA_SOURCE_AFFILIATION.E82', data)
        self.update_nodes('SHARED_DATA_SOURCE_CREATOR_APPELLATION.E82', data)
        self.update_nodes('SHARED_DATA_SOURCE_DATE_OF_CREATION.E50', data)
        return

    def load(self, lang):
        if self.resource:
            
            self.data['SHARED_DATA_SOURCE_APPELLATION.E82'] = {
                'branch_lists': self.get_nodes('SHARED_DATA_SOURCE_APPELLATION.E82'),
                'domains': {
                }
            }
            self.data['SHARED_DATA_SOURCE_AFFILIATION.E82'] = {
                'branch_lists': self.get_nodes('SHARED_DATA_SOURCE_AFFILIATION.E82'),
                'domains': {
                }
            }            
            self.data['SHARED_DATA_SOURCE_CREATOR_APPELLATION.E82'] = {
                'branch_lists': self.get_nodes('SHARED_DATA_SOURCE_CREATOR_APPELLATION.E82'),
                'domains': {
                }
            }

            self.data['SHARED_DATA_SOURCE_DATE_OF_CREATION.E50'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes('SHARED_DATA_SOURCE_DATE_OF_CREATION.E50')),
                'domains': {
                }
            }
                
        return





            
class CartographyForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'cartography',
            'icon': 'fa-flash',
            'name': _('Cartography'),
            'class': CartographyForm
        }


    def update(self, data, files):
        self.update_nodes('MAP_SOURCE_TYPE.E55',data)
        self.update_nodes('TILE_SQUARE_DETAILS.E44', data)
        self.update_nodes('TILE_SQUARE_APPELLATION.E44', data)
        self.update_nodes('MAP_PLACE_APPELLATION.E44', data)
        self.update_nodes('MAP_SOURCE_TYPE.E55', data)
        self.update_nodes('SERIES_TYPE.E55', data)
        self.update_nodes('DATE_OF_CREATION.E50', data)
        self.update_nodes('SCALE_TYPE.E55', data)
        self.update_nodes('CONTRIBUTOR_APPELLATION.E82', data)
        self.update_nodes('EDITION.E62', data)
        self.update_nodes('PROJECTION_TYPE.E55', data)
        return

    def load(self, lang):
        if self.resource:
            
            
            self.data['MAP_PLACE_APPELLATION.E44'] = {
                'branch_lists': self.get_nodes('MAP_PLACE_APPELLATION.E44'),
                'domains': {
                }
            }

            self.data['SCALE_TYPE.E55'] = {
                'branch_lists': self.get_nodes('SCALE_TYPE.E55'),
                'domains': {'SCALE_TYPE.E55' : Concept().get_e55_domain('SCALE_TYPE.E55')
                }
            }
            
            
            self.data['TILE_SQUARE_DETAILS.E44'] = {
                'branch_lists': self.get_nodes('TILE_SQUARE_DETAILS.E44'),
                'domains': {
                }
            }

            self.data['DATE_OF_CREATION.E50'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes('DATE_OF_CREATION.E50')),
                'domains': {
                }
            }


            self.data['TILE_SQUARE_APPELLATION.E44'] = {
                'branch_lists': self.get_nodes('TILE_SQUARE_APPELLATION.E44'),
                'domains': {
                }
            }

            self.data['SERIES_TYPE.E55'] = {
                'branch_lists': self.get_nodes('SERIES_TYPE.E55'),
                'domains': {
                    'SERIES_TYPE.E55' : Concept().get_e55_domain('SERIES_TYPE.E55')
                }
            }


            self.data['MAP_SOURCE_TYPE.E55'] = {
                'branch_lists': self.get_nodes('MAP_SOURCE_TYPE.E55'),
                'domains': {
                    'MAP_SOURCE_TYPE.E55' : Concept().get_e55_domain('MAP_SOURCE_TYPE.E55')
                }
            }

            self.data['CONTRIBUTOR_APPELLATION.E82'] = {
                'branch_lists': self.get_nodes('CONTRIBUTOR_APPELLATION.E82'),
                'domains': {
                }
            }
            self.data['EDITION.E62'] = {
                'branch_lists': self.get_nodes('EDITION.E62'),
                'domains': {
                }
            }
            
            self.data['PROJECTION_TYPE.E55'] = {
                'branch_lists': self.get_nodes('PROJECTION_TYPE.E55'),
                'domains': {
                    'PROJECTION_TYPE.E55' : Concept().get_e55_domain('PROJECTION_TYPE.E55')
                }
            }

        return

class ImageryForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'imagery',
            'icon': 'fa-flash',
            'name': _('Imagery'),
            'class': ImageryForm
        }


    def update(self, data, files):
        self.update_nodes('IMAGERY_CREATOR_APPELLATION.E82', data)
        self.update_nodes('CATALOGUE_ID.E42', data)
        self.update_nodes('IMAGERY_SOURCE_TYPE.E55', data)
        self.update_nodes('RIGHT_TYPE.E55', data)
        self.update_nodes('PROCESSING_TYPE.E55', data)
        self.update_nodes('DATE_OF_ACQUISITION.E50', data)
        self.update_nodes('IMAGERY_DATE_OF_PUBLICATION.E50', data)
        self.update_nodes('ACQUISITION_ASSIGNMENT.E17', data)
        self.update_nodes('IMAGERY_SAMPLED_RESOLUTION_TYPE.E55', data)
        return

    def load(self, lang):
        if self.resource:
            

            self.data['IMAGERY_SAMPLED_RESOLUTION_TYPE.E55'] = {
                'branch_lists': self.get_nodes('IMAGERY_SAMPLED_RESOLUTION_TYPE.E55'),
                'domains': {'IMAGERY_SAMPLED_RESOLUTION_TYPE.E55' : Concept().get_e55_domain('IMAGERY_SAMPLED_RESOLUTION_TYPE.E55')
                }
            }
            
            
            self.data['IMAGERY_CREATOR_APPELLATION.E82'] = {
                'branch_lists': self.get_nodes('IMAGERY_CREATOR_APPELLATION.E82'),
                'domains': {
                }
            }

            self.data['DATE_OF_ACQUISITION.E50'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes('DATE_OF_ACQUISITION.E50')),
                'domains': {
                }
            }


            self.data['IMAGERY_DATE_OF_PUBLICATION.E50'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes('IMAGERY_DATE_OF_PUBLICATION.E50')),
                'domains': {
                }
            }

            self.data['CATALOGUE_ID.E42'] = {
                'branch_lists': self.get_nodes('CATALOGUE_ID.E42'),
                'domains': {
                }
            }


            self.data['PROCESSING_TYPE.E55'] = {
                'branch_lists': self.get_nodes('PROCESSING_TYPE.E55'),
                'domains': {
                    'PROCESSING_TYPE.E55' : Concept().get_e55_domain('PROCESSING_TYPE.E55')
                }
            }

            self.data['RIGHT_TYPE.E55'] = {
                'branch_lists': self.get_nodes('RIGHT_TYPE.E55'),
                'domains': {
                    'RIGHT_TYPE.E55' : Concept().get_e55_domain('RIGHT_TYPE.E55')
                }
            }

            self.data['IMAGERY_SOURCE_TYPE.E55'] = {
                'branch_lists': self.get_nodes('IMAGERY_SOURCE_TYPE.E55'),
                'domains': {
                    'IMAGERY_SOURCE_TYPE.E55' : Concept().get_e55_domain('IMAGERY_SOURCE_TYPE.E55')
                }
            }

            self.data['ACQUISITION_ASSIGNMENT.E17'] = {
                'branch_lists': self.get_nodes('ACQUISITION_ASSIGNMENT.E17'),
                'domains': {
                    'IMAGERY_PLATFORM_TYPE.E55' : Concept().get_e55_domain('IMAGERY_PLATFORM_TYPE.E55'),
                    'IMAGERY_SENSOR_TYPE.E55': Concept().get_e55_domain('IMAGERY_SENSOR_TYPE.E55'),
                    'IMAGERY_BANDS_TYPE.E55' : Concept().get_e55_domain('IMAGERY_BANDS_TYPE.E55'),
                    'IMAGERY_CAMERA_SENSOR_TYPE.E55': Concept().get_e55_domain('IMAGERY_CAMERA_SENSOR_TYPE.E55'),
                    'IMAGERY_CAMERA_SENSOR_RESOLUTION_TYPE.E55' : Concept().get_e55_domain('IMAGERY_CAMERA_SENSOR_RESOLUTION_TYPE.E55'),

                }
            }

        return
        
class RoleForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'roles',
            'icon': 'fa-flash',
            'name': _('Role'),
            'class': RoleForm
        }

    def update(self, data, files):
        self.update_nodes('PHASE_TYPE_ASSIGNMENT.E17', data)
        return


    def load(self, lang):
        if self.resource:
            self.data['PHASE_TYPE_ASSIGNMENT.E17'] = {
                'branch_lists': datetime_nodes_to_dates(self.get_nodes('PHASE_TYPE_ASSIGNMENT.E17')),
                'domains': {
                    'ACTOR_TYPE.E55' : Concept().get_e55_domain('ACTOR_TYPE.E55'),
                    'ACTOR_TYPE_CERTAINTY_TYPE.E55': Concept().get_e55_domain('ACTOR_TYPE_CERTAINTY_TYPE.E55'),
            }
          }

        return
        
class DescriptionForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'description',
            'icon': 'fa-picture-o',
            'name': _('Additional Information'),
            'class': DescriptionForm
        }

    def update(self, data, files):
        self.update_nodes('DESCRIPTION.E62', data)

    def load(self, lang):
        description_types = Concept().get_e55_domain('DESCRIPTION_TYPE.E55')
        try:
            default_description_type = description_types[2]
            if self.resource:
                self.data['DESCRIPTION.E62'] = {
                    'branch_lists': self.get_nodes('DESCRIPTION.E62'),
                    'domains': {'DESCRIPTION_TYPE.E55' : description_types},
                    'defaults': {
                        'DESCRIPTION_TYPE.E55': default_description_type['id'],
                    }
                }
        except IndexError:
            pass

      
class EditHistory(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'edit-history',
            'icon': 'fa-step-backward',
            'name': _('Review Edit History'),
            'class': EditHistory
        }

class DeleteResourceForm(ResourceForm):
    @staticmethod
    def get_info():
        return {
            'id': 'delete-resource',
            'icon': 'fa-times-circle',
            'name': _('Delete Resource'),
            'class': DeleteResourceForm
        }
