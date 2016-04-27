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

def import_concepts(reference_data):
    concepts = reference_data[0]['concepts']
    values = reference_data[1]['values']
    relations = reference_data[2]['relations']

    keys = []
    def validate_recursion(conceptid):
        if conceptid in keys:
            print conceptid + ' has been referenced twice.'
            return True
        else:
            keys.append(conceptid)
            for relation in relations:
                if relation['conceptidfrom'] == conceptid:
                    validate_recursion(relation['conceptidto'])

    validate_recursion('00000000-0000-0000-0000-000000000002')

    def get_concept_values(conceptid):
        related_values = []
        for value in values:
            if 'i_' not in value['value']:
                if value['conceptid'] == conceptid:
                    conceptvalue_obj = ConceptValue()
                    conceptvalue_obj.id = value['valueid']
                    conceptvalue_obj.type = value['valuetype']
                    conceptvalue_obj.value = value['value']
                    conceptvalue_obj.language = value['languageid']
                    related_values.append(conceptvalue_obj)

        return related_values

    concept_objs = {}
    for concept in concepts:
        if 'i_' not in concept['legacyoid']:
            concept_obj = Concept()
            concept_obj.id = concept['conceptid']
            concept_obj.nodetype = concept['nodetype']
            concept_obj.legacyoid = concept['legacyoid']
            concept_obj.values = get_concept_values(concept['conceptid'])
            concept_obj.save()

            concept_objs[concept_obj.id] = concept_obj


    for relation in relations:
        if relation['conceptidfrom'] in concept_objs and relation['conceptidto'] in concept_objs:
            conceptfrom = concept_objs[relation['conceptidfrom']]
            conceptto = concept_objs[relation['conceptidto']]
            conceptfrom.add_relation(conceptto, relation['relationtype'])



