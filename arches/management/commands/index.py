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
import sys
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
import arches.app.models.models as archesmodels
from arches.app.models.concept import Concept
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from arches.app.search.search_engine_factory import SearchEngineFactory

class Command(BaseCommand):
    """A general command used index Arches data into Elasticsearch."""

    def add_arguments(self, parser):
        parser.add_argument('-d', '--delete', action='store', dest='delete', default='',
            choices=['all', 'maplayers', 'entity', 'term', 'concept', ''],
            help='Delete Type; all=Deletes the "maplayers, entity, term, and concept" indexes from Elasticsearch, ' +
            '\'maplayers\'=Deletes just the maplayers index, ' +
            '\'entity\'=Deletes just the entity index, ' +
            '\'term\'=Deletes just the term index, ')

        parser.add_argument('-i', '--index', action='store', dest='index', default='',
            choices=['concept', ''],
            help='Index Type; concept=Indexes just the concepts, ')

    def handle(self, *args, **options):
        if options['delete'] != '':
            print 'delete: '+ options['delete']
            if options['delete'] == 'all':
                self.delete_index('maplayers')
                self.delete_index('entity')
                self.delete_index('term')
                self.delete_index('concept')
            else:
                self.delete_index(options['delete'])

        if options['index'] != '':
            print 'index: '+ options['index']
            cursor = connection.cursor()

            if options['index'] == 'concept' or options['index'] == 'all':
                self.index_concepts_for_search()
                sql = """
                    SELECT a.entitytypeid
                    FROM data.entity_types a;
                    """
                cursor.execute(sql)
                entitytypeids = cursor.fetchall()
                for entitytypeid in entitytypeids:
                    self.index_concepts_by_entitytypeid(entitytypeid[0])

    def index_concepts_for_search(self):
        # see http://sqlblog.com/blogs/adam_machanic/archive/2006/07/12/swinging-from-tree-to-tree-using-ctes-part-1-adjacency-to-nested-sets.aspx
        # Value of Lft for the root node is 1
        # Value of Rgt for the root node is 2 * (Number of nodes)
        # Value of Lft for any node is ((Number of nodes visited) * 2) - (Level of current node)
        # Value of Rgt for any node is (Lft value) + ((Number of subnodes) * 2) + 1


        sys.setrecursionlimit(3000)
        se = SearchEngineFactory().create()
        se.create_mapping('concept', 'all', 'conceptid', 'string', 'not_analyzed')
        se.create_mapping('concept', 'all', 'labelid', 'string', 'not_analyzed')

        def _findNarrowerConcept(conceptid, ret=None, limit=200000, level=1):
            returnobj = {'subnodes': 0}
            if ret == None: # the root node
                labels = archesmodels.Value.objects.filter(concept = conceptid)
                ret = {}
                nodesvisited = len(ret) + 1
                ret[conceptid] = {'labels': [], 'left': (nodesvisited*2)-level, 'right': 0}
                for label in labels:
                    ret[conceptid]['labels'].append({'labelid': label.pk, 'label': label.value})
                level = level + 1

            conceptrealations = archesmodels.ConceptRelations.objects.filter(conceptfrom = conceptid)
            for relation in conceptrealations:
                nodesvisited = len(ret) + 1
                labels = archesmodels.Value.objects.filter(concept = relation.conceptto)
                ret[relation.conceptto_id] = {'labels': [], 'left': (nodesvisited*2)-level, 'right': 0}
                for label in labels:
                    ret[relation.conceptto_id]['labels'].append({'labelid': label.pk, 'label': label.value})
                returnobj = _findNarrowerConcept(relation.conceptto_id, ret=ret, level=level+1)

            subnodes = returnobj['subnodes']
            if subnodes == 0: # meaning we're at a leaf node
                ret[conceptid]['right'] = ret[conceptid]['left'] + 1
            else:
                ret[conceptid]['right'] = subnodes + 1
            return {'all_concepts': ret, 'subnodes': ret[conceptid]['right']}

        concepts = _findNarrowerConcept('00000000-0000-0000-0000-000000000003')

        all_concepts = []
        for key, concept in concepts['all_concepts'].iteritems():
            all_concepts.append({'conceptid': key, 'labels': concept['labels'], 'left': concept['left'], 'right': concept['right']})

        self.index(all_concepts, 'concept', 'all', 'conceptid')

    def index(self, documents, index, type, idfield, processdoc=None, getid=None, bulk=False):
        detail = ''
        bulkitems = []
        errorlist = []
        se = SearchEngineFactory().create()
        if not isinstance(documents, list):
            documents = [documents]
        for document in documents:
            #print "inserting document: %s" % (document)
            sys.stdout.write('.')
            if processdoc == None:
                data = document
            else:
                data = processdoc(document)
            id = None
            if getid != None:
                id = getid(document, data)
            try:
                if bulk:
                    bulkitem = se.create_bulk_item(index=index, doc_type=type, id=id, data=data)
                    bulkitems.append(bulkitem[0])
                    bulkitems.append(bulkitem[1])
                else:
                    se.index_data(index, type, data, idfield=idfield, id=id)
            except Exception as detail:
                errorlist.append(id)
        if bulk:
            try:
                se.bulk_index(index, type, bulkitems)
            except Exception as detail:
                errorlist = bulkitems
                print 'bulk inset failed'

        if detail != '':
            print "\n\nException detail: %s " % (detail)
            print "There was a problem indexing the following items:"
            print errorlist

    def index_concepts_by_entitytypeid(self, entitytypeid):
        entitytype = archesmodels.EntityTypes.objects.get(pk = entitytypeid)
        conceptid = entitytype.conceptid_id
        concept_graph = Concept().get(id=conceptid, include_subconcepts=True, exclude=['note'])
        if len(concept_graph.subconcepts) > 0:
            data = JSONSerializer().serializeToPython(concept_graph, ensure_ascii=True, indent=4)
            self.index(data, 'concept', entitytypeid, 'id', processdoc=None, getid=None, bulk=False)

    def delete_index(self, index):
        se = SearchEngineFactory().create()
        se.delete_index(index=index)

