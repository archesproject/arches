import os, sys, copy
#from django.conf import settings
from django.template import Template
from django.template import Context
from django.utils.module_loading import import_string
from arches.management.commands import utils

class AppSettings(object):

    def __init__(self, path_to_settings_file='arches.settings'):
        settings = import_string(path_to_settings_file)
        #settings = reload(import_string(path_to_settings_file))
        #print id(settings)

        self.load(settings)
        #print 'mode=%s' % self.settings['MODE']

    def load(self, settings):
        self.settings = settings.__dict__.copy()
        #print id(self.settings)

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value

    def update(self, new_settings):
        for key, value in new_settings:
            self.set(key, value)
        self.save()

    def save(self):
        self.create_setingsfile(self.settings, os.path.join(self.settings['PACKAGE_ROOT'], 'settings_local.py'))

    def create_setingsfile(self, data, path_to_file):
        context = Context(data)

        t = Template(
        "MODE = '{{ MODE }}'\n"
        "DEBUG = {{ DEBUG }}\n"
        "\n"
        "\n"
        )

        utils.write_to_file(path_to_file, t.render(context));