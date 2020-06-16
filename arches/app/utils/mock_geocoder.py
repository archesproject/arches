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


def find_candidates(search_string):
    # use search string to retrieve candidate list from data source.
    # return data as follows:
    return [
        {
            "id": 1,
            "text": "100 Main St., San Francisco CA 94109",
            "geometry": {"type": "Point", "coordinates": [-118.45089, 34.08702]},
            "score": 99,
        },
        {
            "id": 2,
            "text": "101 Main St., San Francisco CA 94109",
            "geometry": {"type": "Point", "coordinates": [-118.45089, 34.08702]},
            "score": 99,
        },
        {
            "id": 3,
            "text": "102 Main St., San Francisco CA 94109",
            "geometry": {"type": "Point", "coordinates": [-118.45089, 34.08702]},
            "score": 99,
        },
        {
            "id": 4,
            "text": "103 Main St., San Francisco CA 94109",
            "geometry": {"type": "Point", "coordinates": [-118.45089, 34.08702]},
            "score": 99,
        },
    ]
