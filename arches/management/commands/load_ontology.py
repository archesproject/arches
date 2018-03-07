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

"""This module contains commands for building Arches."""

import os
import uuid
from django.utils.translation import ugettext as _
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.db import transaction
from arches.app.models import models

from arches.app.models.system_settings import settings
# from rdflib import *  
from rdflib import Graph, RDF, RDFS
from rdflib.resource import Resource   
from rdflib.namespace import Namespace, NamespaceManager

class Command(BaseCommand):
    """
    Commands for managing the loading and running of packages in Arches

    """

    def add_arguments(self, parser):
        parser.add_argument('-r', '--reload', action='store_true', dest='reload', default=None,
            help='Reloads an ontology from disk.')
        parser.add_argument('-s', '--source', action='store', dest='source', default=None,
            help='An XML file of describing an ontology graph')
        parser.add_argument('-vn', '--vernum', action='store', dest='version', default=None,
            help='The version of the ontology being loaded')
        parser.add_argument('-n', '--name', action='store', dest='ontology_name', default=None,
            help='Name to use to identify the ontology')
        parser.add_argument('-id', '--id', action='store', dest='id', default=None,
            help='UUID to use as the primary key to the ontology')
        parser.add_argument('-x', '--extensions', action='store', dest='extensions', default=None,
            help='Extensions to append to the base ontology')

    def handle(self, *args, **options):
        def choose_ontology(message):
            available_ontologies = []
            for ontology in models.Ontology.objects.filter(parentontology=None):
                available_ontologies.append(ontology)

            if len(available_ontologies) > 0:
                selections = []
                for index, ontology in enumerate(available_ontologies, start=1):
                    selections.append(('%s. %s (%s)') % (index, ontology.name, ontology.pk))    
                selected_ontology = raw_input(message + '\n'.join(selections)+'\n')
                return available_ontologies[int(selected_ontology)-1]
            else:
                return None
            
        if options['reload']:
            ontology = None
            if options['source'] is not None:
                path = '.%s' % os.path.abspath(options['source']).replace(models.get_ontology_storage_system().location, '')
                ontology = models.Ontology.objects.get(parentontology=None, path=path)
            else:
                ontology = choose_ontology(_('Select the number corresponding to the\nbase ontology which you want to reload.\n'))
            
            if ontology:
                self.run_loader(data_source=ontology.path.path, name=ontology.name, version=ontology.version, id=ontology.pk, extensions=None, verbosity=options['verbosity'])
            return

        if options['version'] is None:
            print _('You must supply a version number using the -vn/--version argument.')
            return 

        if options['source'] is not None:
            self.run_loader(data_source=options['source'], name=options['ontology_name'], version=options['version'], id=options['id'], extensions=options['extensions'], verbosity=options['verbosity'])
            return

        if options['extensions'] is not None:
            ontology = choose_ontology(_('Select the number corresponding to the\nbase ontology to which you want to add the extension.\n'))
            if ontology:
                for extension in options['extensions'].split(','):
                    path_to_check = self.get_relative_path(extension)
                    try:
                        proposed_path = models.Ontology.objects.get(path=path_to_check).path.path
                        print ''
                        print _('It looks like an ontology file has already been loaded with the same name.')
                        print _('The file currently loaded is located here:')
                        print '   %s' % proposed_path
                        print _('If you would simply like to reload the current ontology, you can run this command with the dash r (-r) flag')
                        print 'eg:    python manage.py load_ontology -r\n'
                        return
                    except:
                        pass
                self.run_loader(data_source=ontology.path.path, version=options['version'], id=ontology.pk, extensions=options['extensions'], verbosity=options['verbosity'])
            else:
                print _('You must first define a base ontology (using -s) before loading an extension using the (-x) argument')
            return

    def run_loader(self, data_source=None, version=None, name=None, id=None, extensions=None, verbosity=1):
        """
        load the given ontology file in xml format into the database

        Keyword Arguments:
        data_source -- path to the source file

        version -- version of the ontology being loaded

        """

        if verbosity > 0:
            print ''
            print 'Loading Source Ontology: "%s"' % data_source

        if data_source is not None and version is not None:
            self.graph = Graph()
            self.namespace_manager = NamespaceManager(self.graph)
            self.subclass_cache = {}
            
            with transaction.atomic():
                ontology = self.add_ontology(id=id, data_source=data_source, version=version, name=name)
                loaded_extensions = [extension.path.path for extension in models.Ontology.objects.filter(parentontology=ontology)]

                if extensions is None:
                    extensions = loaded_extensions
                else:
                    extensions = extensions.split(',') + loaded_extensions

                for extension in set(extensions):
                    if verbosity > 0:
                        print 'Loading Extension: "%s"' % extension
                    if os.path.isfile(extension):
                        self.add_ontology(data_source=extension, version=version, name=name, parentontology=ontology)
                    else:
                        # delete references to ontolgy files that don't exist on disk
                        models.Ontology.objects.filter(path=self.get_relative_path(extension)).delete()

                models.OntologyClass.objects.filter(ontology=ontology).delete()
                for ontology_class, data in self.crawl_graph().iteritems():
                    models.OntologyClass.objects.update_or_create(source=ontology_class, ontology=ontology, defaults={'target': data})
                
    def add_ontology(self, id=None, data_source=None, version=None, name=None, parentontology=None):
        self.graph.parse(data_source)

        filepath = os.path.split(os.path.abspath(data_source))[0]
        filename = os.path.split(data_source)[1]
        if name is None:
            name = os.path.splitext(filename)[0]

        if models.get_ontology_storage_system().location in filepath:
            # if the file we're referencing already exists in the location where we 
            # usually store them then leave it there and just save a reference to it
            path = self.get_relative_path(data_source)
        else:
            # need to add the name argument for this to work like it used too
            # see: https://code.djangoproject.com/ticket/26644
            # and this: https://github.com/django/django/commit/914c72be2abb1c6dd860cb9279beaa66409ae1b2#diff-d6396b594a8f63ee1e12a9278e1999edL57
            path = File(open(data_source), name=filename)

        ontology, created = models.Ontology.objects.get_or_create(path=path, parentontology=parentontology, defaults={'version': version, 'name': name, 'path': path, 'pk': id})

        return ontology

    def crawl_graph(self):
        ret = {}
        for ontology_property,p,o in self.graph.triples((None, None, RDF.Property)):
            for s,p,domain_class in self.graph.triples((ontology_property, RDFS.domain, None)):
                domain_class = Resource(self.graph, domain_class)
                for domain_subclass in domain_class.transitive_subjects(RDFS.subClassOf):
                    if domain_subclass.identifier not in ret:
                        ret[domain_subclass.identifier] = {'down':[], 'up':[]}
                    for s,p,range_class in self.graph.triples((ontology_property, RDFS.range, None)):
                        ret[domain_subclass.identifier]['down'].append({
                            'ontology_property':ontology_property,
                            'ontology_classes':self.get_subclasses(range_class)
                        })

            for s,p,range_class in self.graph.triples((ontology_property, RDFS.range, None)):
                range_class = Resource(self.graph, range_class)
                for range_subclass in range_class.transitive_subjects(RDFS.subClassOf):
                    if range_subclass.identifier not in ret:
                        ret[range_subclass.identifier] = {'down':[], 'up':[]}
                    for s,p,o in self.graph.triples((ontology_property, RDFS.domain, None)):
                        ret[range_subclass.identifier]['up'].append({
                            'ontology_property':ontology_property,
                            'ontology_classes':self.get_subclasses(o)
                        })
        return ret

    def get_subclasses(self, ontology_class):
        if ontology_class not in self.subclass_cache:
            ontology_class_resource = Resource(self.graph, ontology_class)
            self.subclass_cache[ontology_class] = [subclass.identifier for subclass in ontology_class_resource.transitive_subjects(RDFS.subClassOf)]
        return self.subclass_cache[ontology_class]

    def get_relative_path(self, data_source):
        """
        get's a path suitable for saving in a FileField column (mimics what Django does to create a path reference from a File object)

        """

        ret = None
        try:
            if models.get_ontology_storage_system().location in os.path.abspath(data_source):
                ret = '.%s' % os.path.abspath(data_source).replace(models.get_ontology_storage_system().location,'')
            else:
                ret ='./%s' % os.path.split(data_source)[1]
        except:
            try:
                ret = data_source.path
            except:
                pass 
        return ret