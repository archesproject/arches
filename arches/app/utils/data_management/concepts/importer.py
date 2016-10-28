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

from arches.app.models.concept import Concept, ConceptValue
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.models import models
from django.db import transaction

# def import_concepts(reference_data):
#     concepts = reference_data[0]['concepts']
#     values = reference_data[1]['values']
#     relations = reference_data[2]['relations']
#
#     concept_objs = {}
#     for concept in concepts:
#         concept_obj = Concept()
#         concept_obj.id = concept['conceptid']
#         concept_obj.nodetype = concept['nodetype']
#         concept_obj.legacyoid = concept['legacyoid']
#         concept_obj.save()
#
#         concept_objs[concept_obj.id] = concept_obj
#
#     existing_valuetypes = [o.valuetype for o in models.DValueType.objects.all()]
#     for value in values:
#         if value['valuetype'] not in existing_valuetypes:
#             models.DValueType.objects.create(valuetype = value['valuetype'], category = 'undefined', namespace = 'arches')
#             existing_valuetypes.append(value['valuetype'])
#
#         conceptvalue_obj = ConceptValue()
#         conceptvalue_obj.id = value['valueid']
#         conceptvalue_obj.conceptid = value['conceptid']
#         conceptvalue_obj.type = value['valuetype']
#         conceptvalue_obj.value = value['value']
#         conceptvalue_obj.language = value['languageid']
#         conceptvalue_obj.save()
#
#     for relation in relations:
#         if relation['conceptidfrom'] in concept_objs and relation['conceptidto'] in concept_objs:
#             conceptfrom = concept_objs[relation['conceptidfrom']]
#             conceptto = concept_objs[relation['conceptidto']]
#             conceptfrom.add_relation(conceptto, relation['relationtype'])

def import_reference_data(reference_data):
    # with transaction.atomic():
    if reference_data != '':
        print '\nLOADING REFERENCE DATA FROM ARCHES JSON'
        print '-----------------------'
    for data in reference_data:
        print data['legacyoid']
        concept = Concept(data)
        concept.save()
