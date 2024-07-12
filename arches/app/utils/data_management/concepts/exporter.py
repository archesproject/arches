"""
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
"""

import os
import uuid
from arches.app.models.concept import Concept, ConceptValue
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer


def get_reference_data_for_export(conceptids=None):
    reference_data_dict = {}
    reference_data = []
    if conceptids is None or conceptids[0] == "all" or conceptids == [""]:
        reference_data.append(
            Concept().get(
                "00000000-0000-0000-0000-000000000001",
                include_subconcepts=True,
                semantic=True,
            )
        )
    else:
        for conceptid in conceptids:
            reference_data.append(
                Concept().get(
                    uuid.UUID(str(conceptid)), include_subconcepts=True, semantic=True
                )
            )
    reference_data_dict["reference_data"] = reference_data
    return reference_data_dict
