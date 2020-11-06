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

"""This module contains commands for building Arches."""

import json
import os
import uuid
import shutil
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
        parser.add_argument("-s", "--source", action="store", dest="source", default=None, help="Ontology configuration file")

    def handle(self, *args, **options):
        def choose_ontology(message):
            available_ontologies = []
            for ontology in models.Ontology.objects.filter(parentontology=None):
                available_ontologies.append(ontology)

            if len(available_ontologies) > 0:
                selections = []
                for index, ontology in enumerate(available_ontologies, start=1):
                    selections.append(("%s. %s (%s)") % (index, ontology.name, ontology.pk))
                selected_ontology = input(message + "\n".join(selections) + "\n")
                return available_ontologies[int(selected_ontology) - 1]
            else:
                return None

        ontology_version = None
        ontology_src = None

        if options["source"]:
            config_file = os.path.join(options["source"], "ontology_config.json")
            if not os.path.exists(config_file):
                # try from the cwd
                config_file = os.path.join(os.getcwd(), options["source"], "ontology_config.json")

            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    configs = json.load(f)
                    ontology_exists = models.Ontology.objects.filter(pk=configs["base_id"]).exists()
                    if ontology_exists:
                        print("reloading")
                    base_id = configs["base_id"]
                    ontology_name = configs["base_name"]
                    ontology_version = configs["base_version"]
                    ontology_extensions = extension_paths = [os.path.join(options["source"], ext) for ext in configs["extensions"]]
                    ontology_src = os.path.join(options["source"], configs["base"])
            else:
                print(_("You must supply an ontology_config.json within your ontology source directory."))
                print(_("'{config_file}' was not found.").format(**locals()))
                return

        if ontology_version is None:
            print(_("You must supply a version number using the -vn/--version argument."))
            return

        if ontology_src is not None:
            self.run_loader(
                data_source=ontology_src,
                name=ontology_name,
                version=ontology_version,
                id=base_id,
                extensions=ontology_extensions,
                verbosity=options["verbosity"],
            )
            return

    def run_loader(self, data_source=None, version=None, name=None, id=None, extensions=None, verbosity=1):
        """
        load the given ontology file in xml format into the database

        Keyword Arguments:
        data_source -- path to the source file

        version -- version of the ontology being loaded

        """

        if verbosity > 0:
            print("")
            print('Loading Source Ontology: "%s"' % data_source)

        if data_source is not None and version is not None:
            self.graph = Graph()
            self.namespace_manager = NamespaceManager(self.graph)
            self.subclass_cache = {}

            with transaction.atomic():
                ontology = self.add_ontology(id=id, data_source=data_source, version=version, name=name)
                loaded_extensions = [extension.path for extension in models.Ontology.objects.filter(parentontology=ontology)]
                extensions = loaded_extensions if extensions is None else extensions + loaded_extensions

                for extension in set(extensions):
                    if verbosity > 0:
                        print('Loading Extension: "%s"' % extension)
                    if os.path.isfile(extension):
                        self.add_ontology(data_source=extension, version=version, name=name, parentontology=ontology)

                models.OntologyClass.objects.filter(ontology=ontology).delete()
                for ontology_class, data in self.crawl_graph().items():
                    models.OntologyClass.objects.update_or_create(source=ontology_class, ontology=ontology, defaults={"target": data})

    def add_ontology(self, id=None, data_source=None, version=None, name=None, parentontology=None):
        self.graph.parse(data_source)
        filename = os.path.split(data_source)[1]
        namespaces = {str(namespace[1]): str(namespace[0]) for namespace in self.graph.namespaces()}
        if name is None:
            name = os.path.splitext(filename)[0]
        ontology, created = models.Ontology.objects.get_or_create(
            path=filename,
            parentontology=parentontology,
            defaults={"version": version, "name": name, "namespaces": namespaces, "path": filename, "pk": id},
        )
        return ontology

    def crawl_graph(self):
        ret = {}
        for ontology_property, p, o in self.graph.triples((None, None, RDF.Property)):
            for s, p, domain_class in self.graph.triples((ontology_property, RDFS.domain, None)):
                domain_class = Resource(self.graph, domain_class)
                for domain_subclass in domain_class.transitive_subjects(RDFS.subClassOf):
                    if domain_subclass.identifier not in ret:
                        ret[domain_subclass.identifier] = {"down": [], "up": []}
                    for s, p, range_class in self.graph.triples((ontology_property, RDFS.range, None)):
                        ret[domain_subclass.identifier]["down"].append(
                            {"ontology_property": ontology_property, "ontology_classes": self.get_subclasses(range_class)}
                        )

            for s, p, range_class in self.graph.triples((ontology_property, RDFS.range, None)):
                range_class = Resource(self.graph, range_class)
                for range_subclass in range_class.transitive_subjects(RDFS.subClassOf):
                    if range_subclass.identifier not in ret:
                        ret[range_subclass.identifier] = {"down": [], "up": []}
                    for s, p, o in self.graph.triples((ontology_property, RDFS.domain, None)):
                        ret[range_subclass.identifier]["up"].append(
                            {"ontology_property": ontology_property, "ontology_classes": self.get_subclasses(o)}
                        )
        return ret

    def get_subclasses(self, ontology_class):
        if ontology_class not in self.subclass_cache:
            ontology_class_resource = Resource(self.graph, ontology_class)
            self.subclass_cache[ontology_class] = [
                subclass.identifier for subclass in ontology_class_resource.transitive_subjects(RDFS.subClassOf)
            ]
        return self.subclass_cache[ontology_class]

    def get_relative_path(self, data_source):
        """
        get's a relative path where the ontology file is located

        """

        ret = None
        try:
            if settings.ONTOLOGY_DIR in os.path.abspath(data_source):
                ret = os.path.abspath(data_source).replace(settings.ONTOLOGY_DIR, "").lstrip(os.sep)
        except Exception as e:
            print("Something when wrong in getting the path to the ontology file", e)

        return ret
