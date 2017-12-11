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

from arches.management.commands import utils
from arches.app.models import models
from django.core.management.base import BaseCommand, CommandError
import arches.app.utils.data_management.resources.remover as resource_remover


class Command(BaseCommand):
    """
    Commands for managing Arches functions

    """

    def add_arguments(self, parser):
        parser.add_argument('operation', nargs='?')

        parser.add_argument('-y', '--yes', action='store_true', dest='yes',
            help='used to force a yes answer to any user input "continue? y/n" prompt')

    def handle(self, *args, **options):
        if options['operation'] == 'remove_resources':
            self.remove_resources(force=options['yes'])

    def remove_resources(self, load_id='', force=False):
        """
        Runs the resource_remover command found in data_management.resources
        """
        # resource_remover.delete_resources(load_id)
        if not force:
            if not utils.get_yn_input("all resources will be removed. continue?"):
                return

        resource_remover.clear_resources()
        return
