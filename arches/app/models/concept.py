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

import re
import uuid
import copy
from operator import itemgetter
from operator import methodcaller
from django.db import transaction, connection
from django.db.models import Q
from arches.app.models import models
from arches.app.models.system_settings import settings
from arches.app.search.search_engine_factory import SearchEngineInstance as se
from arches.app.search.elasticsearch_dsl_builder import Term, Query, Bool, Match, Terms
from arches.app.search.mappings import CONCEPTS_INDEX
from arches.app.utils.betterJSONSerializer import JSONSerializer, JSONDeserializer
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from django.db import IntegrityError
import logging


logger = logging.getLogger(__name__)

CORE_CONCEPTS = (
    "00000000-0000-0000-0000-000000000001",
    "00000000-0000-0000-0000-000000000004",
    "00000000-0000-0000-0000-000000000005",
    "00000000-0000-0000-0000-000000000006",
)


class Concept(object):
    def __init__(self, *args, **kwargs):
        self.id = ""
        self.nodetype = ""
        self.legacyoid = ""
        self.relationshiptype = ""
        self.values = []
        self.subconcepts = []
        self.parentconcepts = []
        self.relatedconcepts = []
        self.hassubconcepts = False

        if len(args) != 0:
            if isinstance(args[0], str):
                try:
                    uuid.UUID(args[0])
                    self.get(args[0])
                except (ValueError):
                    self.load(JSONDeserializer().deserialize(args[0]))
            elif isinstance(args[0], dict):
                self.load(args[0])
            elif isinstance(args[0], object):
                self.load(args[0])

    def __unicode__(self):
        return ("%s - %s") % (self.get_preflabel().value, self.id)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, x):
        return hash(self) == hash(x)

    def __ne__(self, x):
        return hash(self) != hash(x)

    def load(self, value):
        if isinstance(value, dict):
            self.id = str(value["id"]) if "id" in value else ""
            self.nodetype = value["nodetype"] if "nodetype" in value else ""
            self.legacyoid = value["legacyoid"] if "legacyoid" in value else ""
            self.relationshiptype = value["relationshiptype"] if "relationshiptype" in value else ""
            if "values" in value:
                for val in value["values"]:
                    self.addvalue(val)
            if "subconcepts" in value:
                for subconcept in value["subconcepts"]:
                    self.addsubconcept(subconcept)
            if "parentconcepts" in value:
                for parentconcept in value["parentconcepts"]:
                    self.addparent(parentconcept)
            if "relatedconcepts" in value:
                for relatedconcept in value["relatedconcepts"]:
                    self.addrelatedconcept(relatedconcept)

        if isinstance(value, models.Concept):
            self.id = str(value.pk)
            self.nodetype = value.nodetype_id
            self.legacyoid = value.legacyoid

    def get(
        self,
        id="",
        legacyoid="",
        include_subconcepts=False,
        include_parentconcepts=False,
        include_relatedconcepts=False,
        exclude=[],
        include=[],
        depth_limit=None,
        up_depth_limit=None,
        lang=settings.LANGUAGE_CODE,
        semantic=True,
        pathway_filter=None,
        **kwargs,
    ):

        if id != "":
            self.load(models.Concept.objects.get(pk=id))
        elif legacyoid != "":
            self.load(models.Concept.objects.get(legacyoid=legacyoid))

        _cache = kwargs.pop("_cache", {})
        _cache[self.id] = self.__class__(
            {"id": self.id, "nodetype": self.nodetype, "legacyoid": self.legacyoid, "relationshiptype": self.relationshiptype}
        )

        if semantic == True:
            pathway_filter = (
                pathway_filter
                if pathway_filter
                else Q(relationtype__category="Semantic Relations") | Q(relationtype__category="Properties")
            )
        else:
            pathway_filter = pathway_filter if pathway_filter else Q(relationtype="member") | Q(relationtype="hasCollection")

        if self.id != "":
            nodetype = kwargs.pop("nodetype", self.nodetype)
            uplevel = kwargs.pop("uplevel", 0)
            downlevel = kwargs.pop("downlevel", 0)
            depth_limit = depth_limit if depth_limit is None else int(depth_limit)
            up_depth_limit = up_depth_limit if up_depth_limit is None else int(up_depth_limit)

            if include is not None:
                if len(include) > 0 and len(exclude) > 0:
                    raise Exception(_("Only include values for include or exclude, but not both"))
                include = (
                    include if len(include) != 0 else models.DValueType.objects.distinct("category").values_list("category", flat=True)
                )
                include = set(include).difference(exclude)
                exclude = []

                if len(include) > 0:
                    values = models.Value.objects.filter(concept=self.id)
                    for value in values:
                        if value.valuetype.category in include:
                            self.values.append(ConceptValue(value))

            hassubconcepts = models.Relation.objects.filter(Q(conceptfrom=self.id), pathway_filter, ~Q(relationtype="related"))[0:1]
            if len(hassubconcepts) > 0:
                self.hassubconcepts = True

            if include_subconcepts:
                conceptrealations = models.Relation.objects.filter(Q(conceptfrom=self.id), pathway_filter, ~Q(relationtype="related"))
                if depth_limit is None or downlevel < depth_limit:
                    if depth_limit is not None:
                        downlevel = downlevel + 1
                    for relation in conceptrealations:
                        subconcept = (
                            _cache[str(relation.conceptto_id)]
                            if str(relation.conceptto_id) in _cache
                            else self.__class__().get(
                                id=relation.conceptto_id,
                                include_subconcepts=include_subconcepts,
                                include_parentconcepts=include_parentconcepts,
                                include_relatedconcepts=include_relatedconcepts,
                                exclude=exclude,
                                include=include,
                                depth_limit=depth_limit,
                                up_depth_limit=up_depth_limit,
                                downlevel=downlevel,
                                uplevel=uplevel,
                                nodetype=nodetype,
                                semantic=semantic,
                                pathway_filter=pathway_filter,
                                _cache=_cache.copy(),
                                lang=lang,
                            )
                        )
                        subconcept.relationshiptype = relation.relationtype_id
                        self.subconcepts.append(subconcept)

                    self.subconcepts = sorted(
                        self.subconcepts, key=lambda concept: self.natural_keys(concept.get_sortkey(lang)), reverse=False
                    )
                    # self.subconcepts = sorted(self.subconcepts, key=methodcaller(
                    #     'get_sortkey', lang=lang), reverse=False)

            if include_parentconcepts:
                conceptrealations = models.Relation.objects.filter(Q(conceptto=self.id), pathway_filter, ~Q(relationtype="related"))
                if up_depth_limit is None or uplevel < up_depth_limit:
                    if up_depth_limit is not None:
                        uplevel = uplevel + 1
                    for relation in conceptrealations:
                        parentconcept = (
                            _cache[str(relation.conceptfrom_id)]
                            if str(relation.conceptfrom_id) in _cache
                            else self.__class__().get(
                                id=relation.conceptfrom_id,
                                include_subconcepts=False,
                                include_parentconcepts=include_parentconcepts,
                                include_relatedconcepts=include_relatedconcepts,
                                exclude=exclude,
                                include=include,
                                depth_limit=depth_limit,
                                up_depth_limit=up_depth_limit,
                                downlevel=downlevel,
                                uplevel=uplevel,
                                nodetype=nodetype,
                                semantic=semantic,
                                pathway_filter=pathway_filter,
                                _cache=_cache.copy(),
                                lang=lang,
                            )
                        )
                        parentconcept.relationshiptype = relation.relationtype_id

                        self.parentconcepts.append(parentconcept)

            if include_relatedconcepts:
                conceptrealations = models.Relation.objects.filter(
                    Q(relationtype="related") | Q(relationtype__category="Mapping Properties"),
                    Q(conceptto=self.id) | Q(conceptfrom=self.id),
                )
                relations = []
                for relation in conceptrealations:
                    if str(relation.conceptto_id) != self.id and str(relation.relationid) not in relations:
                        relations.append(str(relation.relationid))
                        relatedconcept = self.__class__().get(relation.conceptto_id, include=["label"], lang=lang)
                        relatedconcept.relationshiptype = relation.relationtype_id

                        self.relatedconcepts.append(relatedconcept)
                    if str(relation.conceptfrom_id) != self.id and str(relation.relationid) not in relations:
                        relations.append(str(relation.relationid))
                        relatedconcept = self.__class__().get(relation.conceptfrom_id, include=["label"], lang=lang)
                        relatedconcept.relationshiptype = relation.relationtype_id

                        self.relatedconcepts.append(relatedconcept)

        return self

    def save(self):
        self.id = self.id if (self.id != "" and self.id is not None) else str(uuid.uuid4())
        concept, created = models.Concept.objects.get_or_create(
            pk=self.id, defaults={"legacyoid": self.legacyoid if self.legacyoid != "" else self.id, "nodetype_id": self.nodetype}
        )

        for value in self.values:
            if not isinstance(value, ConceptValue):
                value = ConceptValue(value)
            value.conceptid = self.id
            value.save()

        for parentconcept in self.parentconcepts:
            parentconcept.save()
            parentconcept.add_relation(self, parentconcept.relationshiptype)

        for subconcept in self.subconcepts:
            subconcept.save()
            self.add_relation(subconcept, subconcept.relationshiptype)

        # if we're moving a Concept Scheme below another Concept or Concept Scheme
        if len(self.parentconcepts) > 0 and concept.nodetype_id == "ConceptScheme":
            concept.nodetype_id = "Concept"
            concept.save()
            self.load(concept)

            for relation in models.Relation.objects.filter(conceptfrom=concept, relationtype_id="hasTopConcept"):
                relation.relationtype_id = "narrower"
                relation.save()

        for relatedconcept in self.relatedconcepts:
            self.add_relation(relatedconcept, relatedconcept.relationshiptype)

            if relatedconcept.relationshiptype == "member":
                child_concepts = relatedconcept.get(include_subconcepts=True)

                def applyRelationship(concept):
                    for subconcept in concept.subconcepts:
                        concept.add_relation(subconcept, relatedconcept.relationshiptype)

                child_concepts.traverse(applyRelationship)

        return concept

    def delete(self, delete_self=False):
        """
        Deletes any subconcepts associated with this concept and additionally this concept if 'delete_self' is True
        If any parentconcepts or relatedconcepts are included then it will only delete the relationship to those concepts but not the concepts themselves
        If any values are passed, then those values as well as the relationship to those values will be deleted

        Note, django will automatically take care of deleting any db models that have a foreign key relationship to the model being deleted
        (eg: deleting a concept model will also delete all values and relationships), but because we need to manage deleting
        parent concepts and related concepts and values we have to do that here too

        """

        for subconcept in self.subconcepts:
            concepts_to_delete = Concept.gather_concepts_to_delete(subconcept)
            for key, concept in concepts_to_delete.items():
                models.Concept.objects.get(pk=key).delete()

        for parentconcept in self.parentconcepts:
            relations_filter = (
                (Q(relationtype__category="Semantic Relations") | Q(relationtype="hasTopConcept"))
                & Q(conceptfrom=parentconcept.id)
                & Q(conceptto=self.id)
            )
            conceptrelations = models.Relation.objects.filter(relations_filter)
            for relation in conceptrelations:
                relation.delete()

            if models.Relation.objects.filter(relations_filter).count() == 0:
                # we've removed all parent concepts so now this concept needs to be promoted to a Concept Scheme
                concept = models.Concept.objects.get(pk=self.id)
                concept.nodetype_id = "ConceptScheme"
                concept.save()
                self.load(concept)

                for relation in models.Relation.objects.filter(conceptfrom=concept, relationtype_id="narrower"):
                    relation.relationtype_id = "hasTopConcept"
                    relation.save()

        deletedrelatedconcepts = []
        for relatedconcept in self.relatedconcepts:
            conceptrelations = models.Relation.objects.filter(
                Q(relationtype="related") | Q(relationtype="member") | Q(relationtype__category="Mapping Properties"),
                conceptto=relatedconcept.id,
                conceptfrom=self.id,
            )
            for relation in conceptrelations:
                relation.delete()
                deletedrelatedconcepts.append(relatedconcept)

            conceptrelations = models.Relation.objects.filter(
                Q(relationtype="related") | Q(relationtype="member") | Q(relationtype__category="Mapping Properties"),
                conceptfrom=relatedconcept.id,
                conceptto=self.id,
            )
            for relation in conceptrelations:
                relation.delete()
                deletedrelatedconcepts.append(relatedconcept)

        for deletedrelatedconcept in deletedrelatedconcepts:
            if deletedrelatedconcept in self.relatedconcepts:
                self.relatedconcepts.remove(deletedrelatedconcept)

        for value in self.values:
            if not isinstance(value, ConceptValue):
                value = ConceptValue(value)
            value.delete()

        if delete_self:
            concepts_to_delete = Concept.gather_concepts_to_delete(self)
            for key, concept in concepts_to_delete.items():
                # delete only member relationships if the nodetype == Collection
                if concept.nodetype == "Collection":
                    concept = Concept().get(
                        id=concept.id,
                        include_subconcepts=True,
                        include_parentconcepts=True,
                        include=["label"],
                        up_depth_limit=1,
                        semantic=False,
                    )

                    def find_concepts(concept):
                        if len(concept.parentconcepts) <= 1:
                            for subconcept in concept.subconcepts:
                                conceptrelation = models.Relation.objects.get(
                                    conceptfrom=concept.id, conceptto=subconcept.id, relationtype="member"
                                )
                                conceptrelation.delete()
                                find_concepts(subconcept)

                    find_concepts(concept)
                    # if the concept is a collection, loop through the nodes and delete their rdmCollection values
                    for node in models.Node.objects.filter(config__rdmCollection=concept.id):
                        node.config["rdmCollection"] = None
                        node.save()

                models.Concept.objects.get(pk=key).delete()
        return

    def add_relation(self, concepttorelate, relationtype):
        """
        Relates this concept to 'concepttorelate' via the relationtype

        """

        relation, created = models.Relation.objects.get_or_create(
            conceptfrom_id=self.id, conceptto_id=concepttorelate.id, relationtype_id=relationtype
        )
        return relation

    @staticmethod
    def gather_concepts_to_delete(concept, lang=settings.LANGUAGE_CODE):
        """
        Gets a dictionary of all the concepts ids to delete
        The values of the dictionary keys differ somewhat depending on the node type being deleted
        If the nodetype == 'Concept' then return ConceptValue objects keyed to the concept id
        If the nodetype == 'ConceptScheme' then return a ConceptValue object with the value set to any ONE prefLabel keyed to the concept id
        We do this because it takes so long to gather the ids of the concepts when deleting a Scheme or Group

        """

        concepts_to_delete = {}

        # Here we have to worry about making sure we don't delete nodes that have more than 1 parent
        if concept.nodetype == "Concept":
            concept = Concept().get(
                id=concept.id, include_subconcepts=True, include_parentconcepts=True, include=["label"], up_depth_limit=1
            )

            def find_concepts(concept):
                if len(concept.parentconcepts) <= 1:
                    concepts_to_delete[concept.id] = concept
                    for subconcept in concept.subconcepts:
                        find_concepts(subconcept)

            find_concepts(concept)
            return concepts_to_delete

        # here we can just delete everything and so use a recursive CTE to get the concept ids much more quickly
        if concept.nodetype == "ConceptScheme":
            concepts_to_delete[concept.id] = concept
            rows = Concept().get_child_concepts(concept.id)
            for row in rows:
                if row[0] not in concepts_to_delete:
                    concepts_to_delete[row[0]] = Concept({"id": row[0]})

                concepts_to_delete[row[0]].addvalue({"id": row[2], "conceptid": row[0], "value": row[1]})

        if concept.nodetype == "Collection":
            concepts_to_delete[concept.id] = concept
            rows = Concept().get_child_collections(concept.id)
            for row in rows:
                if row[0] not in concepts_to_delete:
                    concepts_to_delete[row[0]] = Concept({"id": row[0]})

                concepts_to_delete[row[0]].addvalue({"id": row[2], "conceptid": row[0], "value": row[1]})

        return concepts_to_delete

    def get_child_collections_hierarchically(self, conceptid, child_valuetypes=None, offset=0, limit=50, query=None):
        child_valuetypes = child_valuetypes if child_valuetypes else ["prefLabel"]
        columns = "valueidto::text, conceptidto::text, valueto, valuetypeto, depth, count(*) OVER() AS full_count, collector"
        return self.get_child_edges(
            conceptid, ["member"], child_valuetypes, offset=offset, limit=limit, order_hierarchically=True, query=query, columns=columns
        )

    def get_child_collections(self, conceptid, child_valuetypes=None, parent_valuetype="prefLabel", columns=None, depth_limit=""):
        child_valuetypes = child_valuetypes if child_valuetypes else ["prefLabel"]
        columns = columns if columns else "conceptidto::text, valueto, valueidto::text"
        return self.get_child_edges(conceptid, ["member"], child_valuetypes, parent_valuetype, columns, depth_limit)

    def get_child_concepts(self, conceptid, child_valuetypes=None, parent_valuetype="prefLabel", columns=None, depth_limit=""):
        columns = columns if columns else "conceptidto::text, valueto, valueidto::text"
        return self.get_child_edges(conceptid, ["narrower", "hasTopConcept"], child_valuetypes, parent_valuetype, columns, depth_limit)

    def get_child_concepts_for_indexing(self, conceptid, child_valuetypes=None, parent_valuetype="prefLabel", depth_limit=""):
        columns = "valueidto::text, conceptidto::text, valuetypeto, categoryto, valueto, languageto"
        data = self.get_child_edges(conceptid, ["narrower", "hasTopConcept"], child_valuetypes, parent_valuetype, columns, depth_limit)
        return [dict(list(zip(["id", "conceptid", "type", "category", "value", "language"], d)), top_concept="") for d in data]

    def get_child_edges(
        self,
        conceptid,
        relationtypes,
        child_valuetypes=None,
        parent_valuetype="prefLabel",
        columns=None,
        depth_limit=None,
        offset=None,
        limit=20,
        order_hierarchically=False,
        query=None,
        languageid=None,
    ):
        """
        Recursively builds a list of concept relations for a given concept and all it's subconcepts based on its relationship type and valuetypes.

        """

        languageid = get_language() if languageid is None else languageid
        relationtypes = " or ".join(["r.relationtype = '%s'" % (relationtype) for relationtype in relationtypes])
        depth_limit = "and depth < %s" % depth_limit if depth_limit else ""
        child_valuetypes = ("','").join(
            child_valuetypes if child_valuetypes else models.DValueType.objects.filter(category="label").values_list("valuetype", flat=True)
        )
        limit_clause = " limit %s offset %s" % (limit, offset) if offset is not None else ""

        if order_hierarchically:
            sql = """
                WITH RECURSIVE

                 ordered_relationships AS (
                    (
                        SELECT r.conceptidfrom, r.conceptidto, r.relationtype, (
                            SELECT value
                            FROM values
                            WHERE conceptid=r.conceptidto
                            AND valuetype in ('prefLabel')
                            ORDER BY (
                                CASE WHEN languageid = '{languageid}' THEN 10
                                WHEN languageid like '{short_languageid}%' THEN 5
                                WHEN languageid like '{default_languageid}%' THEN 2
                                ELSE 0
                                END
                            ) desc limit 1
                        ) as valuesto,
                        (
                            SELECT value::int
                            FROM values
                            WHERE conceptid=r.conceptidto
                            AND valuetype in ('sortorder')
                            limit 1
                        ) as sortorder,
                        (
                            SELECT value
                            FROM values
                            WHERE conceptid=r.conceptidto
                            AND valuetype in ('collector')
                            limit 1
                        ) as collector
                        FROM relations r
                        WHERE r.conceptidfrom = '{conceptid}'
                        and ({relationtypes})
                        ORDER BY sortorder, valuesto
                    )
                    UNION
                    (
                        SELECT r.conceptidfrom, r.conceptidto, r.relationtype,(
                            SELECT value
                            FROM values
                            WHERE conceptid=r.conceptidto
                            AND valuetype in ('prefLabel')
                            ORDER BY (
                                CASE WHEN languageid = '{languageid}' THEN 10
                                WHEN languageid like '{short_languageid}%' THEN 5
                                WHEN languageid like '{default_languageid}%' THEN 2
                                ELSE 0
                                END
                            ) desc limit 1
                        ) as valuesto,
                        (
                            SELECT value::int
                            FROM values
                            WHERE conceptid=r.conceptidto
                            AND valuetype in ('sortorder')
                            limit 1
                        ) as sortorder,
                        (
                            SELECT value
                            FROM values
                            WHERE conceptid=r.conceptidto
                            AND valuetype in ('collector')
                            limit 1
                        ) as collector
                        FROM relations r
                        JOIN ordered_relationships b ON(b.conceptidto = r.conceptidfrom)
                        WHERE ({relationtypes})
                        ORDER BY sortorder, valuesto
                    )
                ),

                children AS (
                    SELECT r.conceptidfrom, r.conceptidto,
                        to_char(row_number() OVER (), 'fm000000') as row,
                        r.collector,
                        1 AS depth       ---|NonRecursive Part
                        FROM ordered_relationships r
                        WHERE r.conceptidfrom = '{conceptid}'
                        and ({relationtypes})
                    UNION
                        SELECT r.conceptidfrom, r.conceptidto,
                        row || '-' || to_char(row_number() OVER (), 'fm000000'),
                        r.collector,
                        depth+1      ---|RecursivePart
                        FROM ordered_relationships r
                        JOIN children b ON(b.conceptidto = r.conceptidfrom)
                        WHERE ({relationtypes})
                        {depth_limit}
                )

                {subquery}

                SELECT
                (
                    select row_to_json(d)
                    FROM (
                        SELECT *
                        FROM values
                        WHERE conceptid={recursive_table}.conceptidto
                        AND valuetype in ('prefLabel')
                        ORDER BY (
                            CASE WHEN languageid = '{languageid}' THEN 10
                            WHEN languageid like '{short_languageid}%' THEN 5
                            WHEN languageid like '{default_languageid}%' THEN 2
                            ELSE 0
                            END
                        ) desc limit 1
                    ) d
                ) as valueto,
                depth, collector, count(*) OVER() AS full_count

               FROM {recursive_table} order by row {limit_clause};

            """

            subquery = (
                """, results as (
                SELECT c.conceptidfrom, c.conceptidto, c.row, c.depth, c.collector
                FROM children c
                JOIN values ON(values.conceptid = c.conceptidto)
                WHERE LOWER(values.value) like '%%%s%%'
                AND values.valuetype in ('prefLabel')
                    UNION
                SELECT c.conceptidfrom, c.conceptidto, c.row, c.depth, c.collector
                FROM children c
                JOIN results r on (r.conceptidfrom=c.conceptidto)
            )"""
                % query.lower()
                if query is not None
                else ""
            )

            recursive_table = "results" if query else "children"

            sql = sql.format(
                conceptid=conceptid,
                relationtypes=relationtypes,
                child_valuetypes=child_valuetypes,
                parent_valuetype=parent_valuetype,
                depth_limit=depth_limit,
                limit_clause=limit_clause,
                subquery=subquery,
                recursive_table=recursive_table,
                languageid=languageid,
                short_languageid=languageid.split("-")[0],
                default_languageid=settings.LANGUAGE_CODE,
            )

        else:
            sql = """
                WITH RECURSIVE
                    children AS (
                        SELECT r.conceptidfrom, r.conceptidto, r.relationtype, 1 AS depth
                            FROM relations r
                            WHERE r.conceptidfrom = '{conceptid}'
                            AND ({relationtypes})
                        UNION
                            SELECT r.conceptidfrom, r.conceptidto, r.relationtype, depth+1
                            FROM relations r
                            JOIN children c ON(c.conceptidto = r.conceptidfrom)
                            WHERE ({relationtypes})
                            {depth_limit}
                    ),
                    results AS (
                        SELECT
                            valuefrom.value as valuefrom, valueto.value as valueto,
                            valuefrom.valueid as valueidfrom, valueto.valueid as valueidto,
                            valuefrom.valuetype as valuetypefrom, valueto.valuetype as valuetypeto,
                            valuefrom.languageid as languagefrom, valueto.languageid as languageto,
                            dtypesfrom.category as categoryfrom, dtypesto.category as categoryto,
                            c.conceptidfrom, c.conceptidto
                        FROM values valueto
                            JOIN d_value_types dtypesto ON(dtypesto.valuetype = valueto.valuetype)
                            JOIN children c ON(c.conceptidto = valueto.conceptid)
                            JOIN values valuefrom ON(c.conceptidfrom = valuefrom.conceptid)
                            JOIN d_value_types dtypesfrom ON(dtypesfrom.valuetype = valuefrom.valuetype)
                        WHERE valueto.valuetype in ('{child_valuetypes}')
                        AND valuefrom.valuetype in ('{child_valuetypes}')
                    )
                    SELECT distinct {columns}
                    FROM results {limit_clause}

            """

            if not columns:
                columns = """
                    conceptidfrom::text, conceptidto::text,
                    valuefrom, valueto,
                    valueidfrom::text, valueidto::text,
                    valuetypefrom, valuetypeto,
                    languagefrom, languageto,
                    categoryfrom, categoryto
                """

            sql = sql.format(
                conceptid=conceptid,
                relationtypes=relationtypes,
                child_valuetypes=child_valuetypes,
                columns=columns,
                depth_limit=depth_limit,
                limit_clause=limit_clause,
            )

        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        return rows

    def traverse(self, func, direction="down", scope=None, **kwargs):
        """
        Traverses a concept graph from self to leaf (direction='down') or root (direction='up') calling
        the given function on each node, passes an optional scope to each function

        Return a value from the function to prematurely end the traversal

        """

        _cache = kwargs.pop("_cache", [])
        if self.id not in _cache:
            _cache.append(self.id)

            if scope is None:
                ret = func(self, **kwargs)
            else:
                ret = func(self, scope, **kwargs)

            # break out of the traversal if the function returns a value
            if ret is not None:
                return ret

            if direction == "down":
                for subconcept in self.subconcepts:
                    ret = subconcept.traverse(func, direction, scope, _cache=_cache, **kwargs)
                    if ret is not None:
                        return ret
            else:
                for parentconcept in self.parentconcepts:
                    ret = parentconcept.traverse(func, direction, scope, _cache=_cache, **kwargs)
                    if ret is not None:
                        return ret

    def get_sortkey(self, lang=settings.LANGUAGE_CODE):
        for value in self.values:
            if value.type == "sortorder":
                try:
                    return float(value.value)
                except:
                    return None

        return self.get_preflabel(lang=lang).value

    def natural_keys(self, text):
        """
        alist.sort(key=natural_keys) sorts in human order
        http://nedbatchelder.com/blog/200712/human_sorting.html
        (See Toothy's implementation in the comments)
        float regex comes from https://stackoverflow.com/a/12643073/190597
        """

        def atof(text):
            try:
                retval = float(text)
            except ValueError:
                retval = text
            return retval

        return [atof(c) for c in re.split(r"[+-]?([0-9]+(?:[.][0-9]*)?|[.][0-9]+)", str(text))]

    def get_preflabel(self, lang=settings.LANGUAGE_CODE):
        score = 0
        ranked_labels = []
        if self.values == []:
            concept = Concept().get(id=self.id, include_subconcepts=False, include_parentconcepts=False, include=["label"])
        else:
            concept = self

        for value in concept.values:
            ranked_label = {"weight": 1, "value": value}
            if value.type == "prefLabel":
                ranked_label["weight"] = ranked_label["weight"] * 10
            elif value.type == "altLabel":
                ranked_label["weight"] = ranked_label["weight"] * 4

            if value.language == lang:
                ranked_label["weight"] = ranked_label["weight"] * 10
            elif value.language.split("-")[0] == lang.split("-")[0]:
                ranked_label["weight"] = ranked_label["weight"] * 5

            ranked_labels.append(ranked_label)

        ranked_labels = sorted(ranked_labels, key=lambda label: label["weight"], reverse=True)
        if len(ranked_labels) == 0:
            ranked_labels.append({"weight": 1, "value": ConceptValue()})

        return ranked_labels[0]["value"]

    def flatten(self, ret=None):
        """
        Flattens the graph into a unordered list of concepts

        """

        if ret is None:
            ret = []

        ret.append(self)
        for subconcept in self.subconcepts:
            subconcept.flatten(ret)

        return ret

    def addparent(self, value):
        if isinstance(value, dict):
            self.parentconcepts.append(Concept(value))
        elif isinstance(value, Concept):
            self.parentconcepts.append(value)
        else:
            raise Exception("Invalid parent concept definition: %s" % (value))

    def addsubconcept(self, value):
        if isinstance(value, dict):
            self.subconcepts.append(Concept(value))
        elif isinstance(value, Concept):
            self.subconcepts.append(value)
        else:
            raise Exception(_("Invalid subconcept definition: %s") % (value))

    def addrelatedconcept(self, value):
        if isinstance(value, dict):
            self.relatedconcepts.append(Concept(value))
        elif isinstance(value, Concept):
            self.relatedconcepts.append(value)
        else:
            raise Exception(_("Invalid related concept definition: %s") % (value))

    def addvalue(self, value):
        if isinstance(value, dict):
            value["conceptid"] = self.id
            self.values.append(ConceptValue(value))
        elif isinstance(value, ConceptValue):
            self.values.append(value)
        elif isinstance(value, models.Value):
            self.values.append(ConceptValue(value))
        else:
            raise Exception(_("Invalid value definition: %s") % (value))

    def index(self, scheme=None):
        if scheme is None:
            scheme = self.get_context()
        for value in self.values:
            value.index(scheme=scheme)

        if self.nodetype == "ConceptScheme":
            scheme = None

        for subconcept in self.subconcepts:
            subconcept.index(scheme=scheme)

    def bulk_index(self):
        concept_docs = []

        if self.nodetype == "ConceptScheme":
            concept = Concept().get(id=self.id, values=["label"])
            concept.index()
            for topConcept in self.get_child_concepts_for_indexing(self.id, depth_limit=1):
                concept = Concept().get(id=topConcept["conceptid"])
                scheme = concept.get_context()
                topConcept["top_concept"] = scheme.id
                concept_docs.append(se.create_bulk_item(index=CONCEPTS_INDEX, id=topConcept["id"], data=topConcept))
                for childConcept in concept.get_child_concepts_for_indexing(topConcept["conceptid"]):
                    childConcept["top_concept"] = scheme.id
                    concept_docs.append(se.create_bulk_item(index=CONCEPTS_INDEX, id=childConcept["id"], data=childConcept))

        if self.nodetype == "Concept":
            concept = Concept().get(id=self.id, values=["label"])
            scheme = concept.get_context()
            concept.index(scheme)
            for childConcept in concept.get_child_concepts_for_indexing(self.id):
                childConcept["top_concept"] = scheme.id
                concept_docs.append(se.create_bulk_item(index=CONCEPTS_INDEX, id=childConcept["id"], data=childConcept))

        se.bulk_index(concept_docs)

    def delete_index(self, delete_self=False):
        def delete_concept_values_index(concepts_to_delete):
            for concept in concepts_to_delete.values():
                query = Query(se, start=0, limit=10000)
                term = Term(field="conceptid", term=concept.id)
                query.add_query(term)
                query.delete(index=CONCEPTS_INDEX)

        if delete_self:
            concepts_to_delete = Concept.gather_concepts_to_delete(self)
            delete_concept_values_index(concepts_to_delete)
        else:
            for subconcept in self.subconcepts:
                concepts_to_delete = Concept.gather_concepts_to_delete(subconcept)
                delete_concept_values_index(concepts_to_delete)

    def concept_tree(
        self, top_concept="00000000-0000-0000-0000-000000000001", lang=settings.LANGUAGE_CODE, mode="semantic",
    ):
        class concept(object):
            def __init__(self, *args, **kwargs):
                self.label = ""
                self.labelid = ""
                self.id = ""
                self.sortorder = None
                self.load_on_demand = False
                self.children = []

        def _findNarrowerConcept(conceptid, depth_limit=None, level=0):
            labels = models.Value.objects.filter(concept=conceptid)
            ret = concept()
            temp = Concept()
            for label in labels:
                temp.addvalue(label)
                if label.valuetype_id == "sortorder":
                    try:
                        ret.sortorder = float(label.value)
                    except:
                        ret.sortorder = None

            label = temp.get_preflabel(lang=lang)
            ret.label = label.value
            ret.id = label.conceptid
            ret.labelid = label.id

            if mode == "semantic":
                conceptrealations = models.Relation.objects.filter(
                    Q(conceptfrom=conceptid), Q(relationtype__category="Semantic Relations") | Q(relationtype__category="Properties")
                )
            if mode == "collections":
                conceptrealations = models.Relation.objects.filter(
                    Q(conceptfrom=conceptid), Q(relationtype="member") | Q(relationtype="hasCollection")
                )
            if depth_limit is not None and len(conceptrealations) > 0 and level >= depth_limit:
                ret.load_on_demand = True
            else:
                if depth_limit is not None:
                    level = level + 1
                for relation in conceptrealations:
                    ret.children.append(_findNarrowerConcept(relation.conceptto_id, depth_limit=depth_limit, level=level))

                ret.children = sorted(
                    ret.children,
                    key=lambda concept: self.natural_keys(concept.sortorder if concept.sortorder else concept.label),
                    reverse=False,
                )
            return ret

        def _findBroaderConcept(conceptid, child_concept, depth_limit=None, level=0):
            conceptrealations = models.Relation.objects.filter(
                Q(conceptto=conceptid), ~Q(relationtype="related"), ~Q(relationtype__category="Mapping Properties")
            )
            if len(conceptrealations) > 0 and conceptid != top_concept:
                labels = models.Value.objects.filter(concept=conceptrealations[0].conceptfrom_id)
                ret = concept()
                temp = Concept()
                for label in labels:
                    temp.addvalue(label)
                label = temp.get_preflabel(lang=lang)
                ret.label = label.value
                ret.id = label.conceptid
                ret.labelid = label.id

                ret.children.append(child_concept)
                return _findBroaderConcept(conceptrealations[0].conceptfrom_id, ret, depth_limit=depth_limit, level=level)
            else:
                return child_concept

        graph = []
        if self.id is None or self.id == "" or self.id == "None" or self.id == top_concept:
            if mode == "semantic":
                concepts = models.Concept.objects.filter(nodetype="ConceptScheme")
                for conceptmodel in concepts:
                    graph.append(_findNarrowerConcept(conceptmodel.pk, depth_limit=1))
            if mode == "collections":
                concepts = models.Concept.objects.filter(nodetype="Collection")
                for conceptmodel in concepts:
                    graph.append(_findNarrowerConcept(conceptmodel.pk, depth_limit=0))

                graph = sorted(graph, key=lambda concept: concept.label)
                # graph = _findNarrowerConcept(concepts[0].pk, depth_limit=1).children

        else:
            graph = _findNarrowerConcept(self.id, depth_limit=1).children
            # concepts = _findNarrowerConcept(self.id, depth_limit=1)
            # graph = [_findBroaderConcept(self.id, concepts, depth_limit=1)]

        return graph

    def get_paths(self, lang=settings.LANGUAGE_CODE):
        def graph_to_paths(current_concept, path=[], path_list=[], _cache=[]):
            if len(path) == 0:
                current_path = []
            else:
                current_path = path[:]

            current_path.insert(
                0,
                {
                    "label": current_concept.get_preflabel(lang=lang).value,
                    "relationshiptype": current_concept.relationshiptype,
                    "id": current_concept.id,
                },
            )

            if len(current_concept.parentconcepts) == 0 or current_concept.id in _cache:
                path_list.append(current_path[:])
            else:
                _cache.append(current_concept.id)
                for parent in current_concept.parentconcepts:
                    ret = graph_to_paths(parent, current_path, path_list, _cache)

            return path_list

        # def graph_to_paths(current_concept, **kwargs):
        #     path = kwargs.get('path', [])
        #     path_list = kwargs.get('path_list', [])

        #     if len(path) == 0:
        #         current_path = []
        #     else:
        #         current_path = path[:]

        #     current_path.insert(0, {'label': current_concept.get_preflabel(lang=lang).value, 'relationshiptype': current_concept.relationshiptype, 'id': current_concept.id})

        #     if len(current_concept.parentconcepts) == 0:
        #         path_list.append(current_path[:])
        #     # else:
        #     #     for parent in current_concept.parentconcepts:
        #     #         ret = graph_to_paths(parent, current_path, path_list, _cache)

        #     #return path_list

        # self.traverse(graph_to_paths, direction='up')

        return graph_to_paths(self)

    def get_node_and_links(self, lang=settings.LANGUAGE_CODE):
        nodes = [{"concept_id": self.id, "name": self.get_preflabel(lang=lang).value, "type": "Current"}]
        links = []

        def get_parent_nodes_and_links(current_concept, _cache=[]):
            if current_concept.id not in _cache:
                _cache.append(current_concept.id)
                parents = current_concept.parentconcepts
                for parent in parents:
                    nodes.append(
                        {
                            "concept_id": parent.id,
                            "name": parent.get_preflabel(lang=lang).value,
                            "type": "Root" if len(parent.parentconcepts) == 0 else "Ancestor",
                        }
                    )
                    links.append(
                        {"target": current_concept.id, "source": parent.id, "relationship": "broader", }
                    )
                    get_parent_nodes_and_links(parent, _cache)

        get_parent_nodes_and_links(self)

        # def get_parent_nodes_and_links(current_concept):
        #     parents = current_concept.parentconcepts
        #     for parent in parents:
        #         nodes.append({'concept_id': parent.id, 'name': parent.get_preflabel(lang=lang).value, 'type': 'Root' if len(parent.parentconcepts) == 0 else 'Ancestor'})
        #         links.append({'target': current_concept.id, 'source': parent.id, 'relationship': 'broader' })

        # self.traverse(get_parent_nodes_and_links, direction='up')

        for child in self.subconcepts:
            nodes.append(
                {"concept_id": child.id, "name": child.get_preflabel(lang=lang).value, "type": "Descendant", }
            )
            links.append({"source": self.id, "target": child.id, "relationship": "narrower"})

        for related in self.relatedconcepts:
            nodes.append(
                {"concept_id": related.id, "name": related.get_preflabel(lang=lang).value, "type": "Related", }
            )
            links.append({"source": self.id, "target": related.id, "relationship": "related"})

        # get unique node list and assign unique integer ids for each node (required by d3)
        nodes = list({node["concept_id"]: node for node in nodes}.values())
        for i in range(len(nodes)):
            nodes[i]["id"] = i
            for link in links:
                link["source"] = i if link["source"] == nodes[i]["concept_id"] else link["source"]
                link["target"] = i if link["target"] == nodes[i]["concept_id"] else link["target"]

        return {"nodes": nodes, "links": links}

    def get_context(self):
        """
        get the Top Concept that the Concept particpates in

        """

        if self.nodetype == "Concept" or self.nodetype == "Collection":
            concept = Concept().get(id=self.id, include_parentconcepts=True, include=None)

            def get_scheme_id(concept):
                for parentconcept in concept.parentconcepts:
                    if parentconcept.relationshiptype == "hasTopConcept":
                        return concept

            if len(concept.parentconcepts) > 0:
                return concept.traverse(get_scheme_id, direction="up")
            else:
                return self

        else:  # like ConceptScheme or EntityType
            return self

    def get_scheme(self):
        """
        get the ConceptScheme that the Concept particpates in

        """

        topConcept = self.get_context()
        if len(topConcept.parentconcepts) == 1:
            if topConcept.parentconcepts[0].nodetype == "ConceptScheme":
                return topConcept.parentconcepts[0]

        return None

    def check_if_concept_in_use(self):
        """Checks  if a concept or any of its subconcepts is in use by a resource instance"""

        in_use = False
        cursor = connection.cursor()
        for value in self.values:
            sql = (
                """
                SELECT count(*) from tiles t, jsonb_each_text(t.tiledata) as json_data
                WHERE json_data.value = '%s'
            """
                % value.id
            )
            cursor.execute(sql)
            rows = cursor.fetchall()
            if rows[0][0] > 0:
                in_use = True
                break
        if in_use is not True:
            for subconcept in self.subconcepts:
                in_use = subconcept.check_if_concept_in_use()
                if in_use == True:
                    return in_use
        return in_use

    def get_e55_domain(self, conceptid):
        """
        For a given entitytypeid creates a dictionary representing that entitytypeid's concept graph (member pathway) formatted to support
        select2 dropdowns

        """
        cursor = connection.cursor()

        sql = """
        WITH RECURSIVE children AS (
            SELECT d.conceptidfrom, d.conceptidto, c2.value, c2.valueid as valueid, c.value as valueto, c.valueid as valueidto, c.valuetype as vtype, 1 AS depth, array[d.conceptidto] AS conceptpath, array[c.valueid] AS idpath        ---|NonRecursive Part
                FROM relations d
                JOIN values c ON(c.conceptid = d.conceptidto)
                JOIN values c2 ON(c2.conceptid = d.conceptidfrom)
                WHERE d.conceptidfrom = '{0}'
                and c2.valuetype = 'prefLabel'
                and c.valuetype in ('prefLabel', 'sortorder', 'collector')
                and (d.relationtype = 'member' or d.relationtype = 'hasTopConcept')
                UNION
                SELECT d.conceptidfrom, d.conceptidto, v2.value, v2.valueid as valueid, v.value as valueto, v.valueid as valueidto, v.valuetype as vtype, depth+1, (conceptpath || d.conceptidto), (idpath || v.valueid)   ---|RecursivePart
                FROM relations  d
                JOIN children b ON(b.conceptidto = d.conceptidfrom)
                JOIN values v ON(v.conceptid = d.conceptidto)
                JOIN values v2 ON(v2.conceptid = d.conceptidfrom)
                WHERE  v2.valuetype = 'prefLabel'
                and v.valuetype in ('prefLabel','sortorder', 'collector')
                and (d.relationtype = 'member' or d.relationtype = 'hasTopConcept')
            ) SELECT conceptidfrom::text, conceptidto::text, value, valueid::text, valueto, valueidto::text, depth, idpath::text, conceptpath::text, vtype FROM children ORDER BY depth, conceptpath;
        """.format(
            conceptid
        )

        column_names = [
            "conceptidfrom",
            "conceptidto",
            "value",
            "valueid",
            "valueto",
            "valueidto",
            "depth",
            "idpath",
            "conceptpath",
            "vtype",
        ]
        cursor.execute(sql)
        rows = cursor.fetchall()

        class Val(object):
            def __init__(self, conceptid):
                self.text = ""
                self.conceptid = conceptid
                self.id = ""
                self.sortorder = ""
                self.collector = ""
                self.children = []

        result = Val(conceptid)

        def _findNarrower(val, path, rec):
            for conceptid in path:
                childids = [child.conceptid for child in val.children]
                if conceptid not in childids:
                    new_val = Val(rec["conceptidto"])
                    if rec["vtype"] == "sortorder":
                        new_val.sortorder = rec["valueto"]
                    elif rec["vtype"] == "prefLabel":
                        new_val.text = rec["valueto"]
                        new_val.id = rec["valueidto"]
                    elif rec["vtype"] == "collector":
                        new_val.collector = "collector"
                    val.children.append(new_val)
                else:
                    for child in val.children:
                        if conceptid == child.conceptid:
                            if conceptid == path[-1]:
                                if rec["vtype"] == "sortorder":
                                    child.sortorder = rec["valueto"]
                                elif rec["vtype"] == "prefLabel":
                                    child.text = rec["valueto"]
                                    child.id = rec["valueidto"]
                                elif rec["vtype"] == "collector":
                                    child.collector = "collector"
                            path.pop(0)
                            _findNarrower(child, path, rec)
                val.children.sort(key=lambda x: (x.sortorder, x.text))

        for row in rows:
            rec = dict(list(zip(column_names, row)))
            path = rec["conceptpath"][1:-1].split(",")
            _findNarrower(result, path, rec)

        return JSONSerializer().serializeToPython(result)["children"]

    def make_collection(self):
        if len(self.values) == 0:
            raise Exception(_("Need to include values when creating a collection"))
        values = JSONSerializer().serializeToPython(self.values)
        for value in values:
            value["id"] = ""
        collection_concept = Concept({"nodetype": "Collection", "values": values})

        def create_collection(conceptfrom):
            for relation in models.Relation.objects.filter(
                Q(conceptfrom_id=conceptfrom.id),
                Q(relationtype__category="Semantic Relations") | Q(relationtype__category="Properties"),
                ~Q(relationtype="related"),
            ):
                conceptto = Concept(relation.conceptto)
                if conceptfrom == self:
                    collection_concept.add_relation(conceptto, "member")
                else:
                    conceptfrom.add_relation(conceptto, "member")
                create_collection(conceptto)

        with transaction.atomic():
            collection_concept.save()
            create_collection(self)

        return collection_concept


class ConceptValue(object):
    def __init__(self, *args, **kwargs):
        self.id = ""
        self.conceptid = ""
        self.type = ""
        self.category = ""
        self.value = ""
        self.language = ""

        if len(args) != 0:
            if isinstance(args[0], str):
                try:
                    uuid.UUID(args[0])
                    self.get(args[0])
                except (ValueError):
                    self.load(JSONDeserializer().deserialize(args[0]))
            elif isinstance(args[0], object):
                self.load(args[0])

    def __repr__(self):
        return ('%s: %s = "%s" in lang %s') % (self.__class__, self.type, self.value, self.language)

    def get(self, id=""):
        self.load(models.Value.objects.get(pk=id))
        return self

    def save(self):
        if self.value.strip() != "":
            self.id = self.id if (self.id != "" and self.id is not None) else str(uuid.uuid4())
            value = models.Value()
            value.pk = self.id
            value.value = self.value
            value.concept_id = self.conceptid  # models.Concept.objects.get(pk=self.conceptid)
            value.valuetype_id = self.type  # models.DValueType.objects.get(pk=self.type)

            if self.language != "":
                # need to normalize language ids to the form xx-XX
                lang_parts = self.language.lower().replace("_", "-").split("-")
                try:
                    lang_parts[1] = lang_parts[1].upper()
                except:
                    pass
                self.language = "-".join(lang_parts)
                value.language_id = self.language  # models.DLanguage.objects.get(pk=self.language)
            else:
                value.language_id = settings.LANGUAGE_CODE

            value.save()
            self.category = value.valuetype.category

    def delete(self):
        if self.id != "":
            newvalue = models.Value.objects.get(pk=self.id)
            if newvalue.valuetype.valuetype == "image":
                newvalue = models.FileValue.objects.get(pk=self.id)
            newvalue.delete()
            self = ConceptValue()
            return self

    def load(self, value):
        if isinstance(value, models.Value):
            self.id = str(value.pk)
            self.conceptid = str(value.concept_id)
            self.type = value.valuetype_id
            self.category = value.valuetype.category
            self.value = value.value
            self.language = value.language_id

        if isinstance(value, dict):
            self.id = str(value["id"]) if "id" in value else ""
            self.conceptid = str(value["conceptid"]) if "conceptid" in value else ""
            self.type = value["type"] if "type" in value else ""
            self.category = value["category"] if "category" in value else ""
            self.value = value["value"] if "value" in value else ""
            self.language = value["language"] if "language" in value else ""

    def index(self, scheme=None):
        if self.category == "label":
            data = JSONSerializer().serializeToPython(self)
            if scheme is None:
                scheme = self.get_scheme_id()
            if scheme is None:
                raise Exception(_("Index of label failed.  Index type (scheme id) could not be derived from the label."))

            data["top_concept"] = scheme.id
            se.index_data(index=CONCEPTS_INDEX, body=data, idfield="id")

    def delete_index(self):
        query = Query(se, start=0, limit=10000)
        term = Term(field="id", term=self.id)
        query.add_query(term)
        query.delete(index=CONCEPTS_INDEX)

    def get_scheme_id(self):
        result = se.search(index=CONCEPTS_INDEX, id=self.id)
        if result["found"]:
            return Concept(result["top_concept"])
        else:
            return None


def get_preflabel_from_conceptid(conceptid, lang):
    ret = None
    default = {
        "category": "",
        "conceptid": "",
        "language": "",
        "value": "",
        "type": "",
        "id": "",
    }
    query = Query(se)
    bool_query = Bool()
    bool_query.must(Match(field="type", query="prefLabel", type="phrase"))
    bool_query.filter(Terms(field="conceptid", terms=[conceptid]))
    query.add_query(bool_query)
    preflabels = query.search(index=CONCEPTS_INDEX)["hits"]["hits"]
    for preflabel in preflabels:
        default = preflabel["_source"]
        if preflabel["_source"]["language"] is not None and lang is not None:
            # get the label in the preferred language, otherwise get the label in the default language
            if preflabel["_source"]["language"] == lang:
                return preflabel["_source"]
            if preflabel["_source"]["language"].split("-")[0] == lang.split("-")[0]:
                ret = preflabel["_source"]
            if preflabel["_source"]["language"] == settings.LANGUAGE_CODE and ret is None:
                ret = preflabel["_source"]
    return default if ret is None else ret


def get_valueids_from_concept_label(label, conceptid=None, lang=None):

    def exact_val_match(val, conceptid=None):
        # exact term match, don't care about relevance ordering.
        # due to language formating issues, and with (hopefully) small result sets
        # easier to have filter logic in python than to craft it in dsl
        if conceptid is None:
            return {"query": {"bool": {"filter": {"match_phrase": {"value": val}}}}}
        else:
            return {
                "query": {
                    "bool": {"filter": [{"match_phrase": {"value": val}}, {"term": {"conceptid": conceptid}}, ]}
                }
            }

    concept_label_results = se.search(index=CONCEPTS_INDEX, body=exact_val_match(label, conceptid))
    if concept_label_results is None:
        print("Found no matches for label:'{0}' and concept_id: '{1}'".format(label, conceptid))
        return
    return [
        res["_source"]
        for res in concept_label_results["hits"]["hits"]
        if lang is None or res["_source"]["language"].lower() == lang.lower()
    ]


def get_preflabel_from_valueid(valueid, lang):
    concept_label = se.search(index=CONCEPTS_INDEX, id=valueid)
    if concept_label["found"]:
        return get_preflabel_from_conceptid(concept_label["_source"]["conceptid"], lang)
