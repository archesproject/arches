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


# From https://towardsdatascience.com/how-to-flatten-deeply-nested-json-objects-in-non-recursive-elegant-python-55f96533103d
def flatten_dict(nested_dict, separator="_"):
    """
    Flatten dict object with nested keys into a single level.
    Args:
        nested_dict: A nested dict object.
        separator: a string used to denote hierarchical
    Returns:
        The flattened dict object if successful, None otherwise.
    """
    out = {}

    def flatten(x, name=""):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + separator)
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + separator)
                i += 1
        else:
            out[name[:-1]] = x

    flatten(nested_dict)
    return out
