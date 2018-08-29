import arches
import json
import os
import subprocess
from arches.management.commands import utils
from arches.app.models import models
from arches.app.models.system_settings import settings
from django.core.management.base import BaseCommand, CommandError
import urllib, json


class Command(BaseCommand):
    """
    Commands for managing Arches functions

    """

    def add_arguments(self, parser):
        parser.add_argument('operation', nargs='?', help='operation \'livereload\' starts livereload for this project on port 35729')

    def handle(self, *args, **options):
        if arches.__version__ == '4.2':
            self.upgrade_to_v4_2_0()
        if arches.__version__ == '4.3':
            self.upgrade_to_v4_3_0()

    def overwite_existing_file(self, path, message):
        write_file = False
        if os.path.exists(path) == True:
            if not utils.get_yn_input(message):
                return write_file
            else:
                write_file = True
        else:
            write_file = True
        return write_file

    def update_yarn_depenencies(self, version):
        packages_path = os.path.join(settings.APP_ROOT, 'package.json')
        yarn_config_path = os.path.join(settings.APP_ROOT, '.yarnrc')

        if self.overwite_existing_file(yarn_config_path, "A .yarnrc file already exists. Would you like to overwrite it with the latest? If you have not manually modified this file since creating this project, the answer is probably 'yes'") == True:
            with open(yarn_config_path, 'w') as f:
                content = '--install.modules-folder "./media/packages"\n--add.modules-folder "./media/packages"'
                f.write(content)

        if self.overwite_existing_file(packages_path, "A package.json file already exists. Would you like to overwrite it with the latest? If you have not manually modified this file since creating this project, the answer is probably 'yes'") == True:
            url = "https://raw.githubusercontent.com/archesproject/arches/stable/{0}/package.json".format(version)
            response = urllib.urlopen(url)
            data = json.loads(response.read())
            with open(packages_path, 'w') as f:
                json.dump(data, f, indent=4)

        if utils.get_yn_input("Would you like to update your javascript packages using yarn? Yarn v1.5.1 or greater is required") == True:
            try:
                os.chdir(settings.APP_ROOT)
                subprocess.call("yarn install", shell=True)
            except Exception as e:
                print e

    def upgrade_to_v4_2_0(self):
        self.update_yarn_depenencies('4.2.x')

    def upgrade_to_v4_3_0(self):
        self.update_yarn_depenencies('4.3.x')
