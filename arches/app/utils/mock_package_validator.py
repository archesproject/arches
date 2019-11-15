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

from arches.management.commands import utils


class Validation_Errors(object):
    def __init__(self, *args):
        # Create lists for specific error types here and reference them when using the append_error function below.
        self.example_error_list = []


validation_errors = Validation_Errors()


# # EXAMPLE:
# def example_validation_function(resource):
# 	if resource does not pass some test:
# 		append_error('My error text', 'example_error_list')


# def append_error(text, error_type):
# 	# Use this function to append error text to an error_type_list that can be printed to a log file.
# 	# text = the error text you would like to append.
# 	# error_type = the error type list from the validation_errors object.
# 	error_type_list = getattr(validation_errors, error_type)
# 	error_type_list.append(text)


def validate_resource(resource):
    pass
    # Use this function to call specific validation functions.
    # example_validation_function(resource)
