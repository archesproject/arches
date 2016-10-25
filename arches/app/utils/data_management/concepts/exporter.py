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

import os
import uuid
from arches.app.models.concept import Concept, ConceptValue
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer


def get_reference_data_for_export(conceptids=None):
    reference_data = []
    if conceptids is None:
        reference_data.append(Concept().get('00000000-0000-0000-0000-000000000001', include_subconcepts=True, semantic=True))
    else:
        for conceptid in conceptids:
            reference_data.append(Concept().get(uuid.UUID(str(conceptid)), include_subconcepts=True, semantic=True))
    return reference_data

def write_reference_data(export_dir, conceptids):
    reference_data = get_reference_data_for_export(conceptids)
    reference_data_dict = {}
    reference_data_dict['reference_data'] = reference_data

    with open(os.path.join(export_dir, 'reference_data_export.json'), 'w') as reference_data_json:
        reference_data_json.write(JSONSerializer().serialize(reference_data_dict))
