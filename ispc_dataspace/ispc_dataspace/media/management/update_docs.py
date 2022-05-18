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

import os
import json
import time
import re
import csv

from arches.app.models import models as archesmodels
from django.core.management.base import BaseCommand
from django.db import transaction
from arches.app.models.resource import Resource

from arches.app.models.models import TileModel
from arches.app.datatypes.datatypes import DataTypeFactory
from arches.app.search.search_engine_factory import SearchEngineInstance
from arches.app.models.system_settings import settings


try:
    graph_uuid_map = settings.MODEL_NAME_UUID_MAP
except:
    graph_uuid_map = {}


fieldre = re.compile("\* FieldId:(.*?)$", flags=re.DOTALL)
branchre = re.compile("\* BranchId:(.*?)$", flags=re.DOTALL)
notere = re.compile("# Arches Note:(.*?)$", flags=re.DOTALL)
generalre = re.compile("# General:(.*?)$", flags=re.DOTALL)
specificre = re.compile("# Specific:(.*?)$", flags=re.DOTALL)


class Command(BaseCommand):
    """
    Command for importing JSON-LD data into Arches
    """

    def add_arguments(self, parser):

        parser.add_argument("-s", "--source", default="node_descs.csv", action="store", dest="source", help="TSV file to read data from")
        parser.add_argument("-d", "--dest", default="node_descs.csv", action="store", dest="dest", help="TSV filename to write to")
        parser.add_argument("-o", "--operation", default="export", action="store", dest="op", help="One of: update, export")
        parser.add_argument("-g", "--graph", action="store", dest="model", help="slug or uuid for graph to export")

        parser.add_argument("--count", action="store_true", dest="count", help="include count of tiles in export")

    def handle(self, *args, **options):
        if options["op"] == "update":
            self.handle_update(options)
        elif options["op"] == "export":
            self.handle_export(options)
        elif options["op"] == "copy":
            self.handle_copy(options)
        else:
            print("Unknown operation. Available: update, export")

    def handle_update(self, options):
        template = """# Specific:
{spec}

# General:
{desc}

# Arches Note:
{note}

* BranchId: {bid}
* FieldId: {fid}
"""

        with open(options["source"]) as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            for rec in reader:
                node = archesmodels.Node.objects.get(pk=rec["NodeId"])
                if rec["Node Name"]:
                    node.name = rec["Node Name"]
                desc = template.format(spec=rec["Specific"], desc=rec["General"], note=rec["Note"], bid=rec["BranchId"], fid=rec["FieldId"])
                node.description = desc
                node.save()

    def handle_copy(self, options):
        # Try to force insert the docs into the target database using
        # https://docs.djangoproject.com/en/2.2/topics/db/multi-db/

        self.forced_target_source = {
            "28a4ae07-c062-11e9-a11d-a4d18cec433a": "d515c3a8-bbd8-11ea-b6b2-3af9d3b32b71",
            "741d3687-bfb4-11e9-bcc1-a4d18cec433a": "292cf278-bb15-11ea-85a6-3af9d3b32b71",
            "83cf1bdc-bfb4-11e9-8f51-a4d18cec433a": "3a5bc0a6-bb15-11ea-85a6-3af9d3b32b71",
        }

        m = options["model"]
        if not m:
            # do all of them
            graphs = [x for x in archesmodels.GraphModel.objects.using("target").all()]
        else:
            graphid = graph_uuid_map.get(m, None)
            if not graphid:
                # Check slug
                try:
                    graph = archesmodels.GraphModel.objects.using("target").get(slug=m)
                except:
                    print(f"Couldn't find a model definition for {m}; skipping")
                    return
            else:
                try:
                    graph = archesmodels.GraphModel.objects.using("target").get(pk=graphid)
                except:
                    print(f"Couldn't find a model for {graphid}; skipping")
                    return
            graphs = [graph]

        graph_alignment = {
            "b6c819b8-99f6-11ea-a9b7-3af9d3b32b71": "1810d182-b4b5-11ea-84f7-3af9d3b32b71",  # Instrument
            "9519cb4f-b25b-11e9-8c7b-a4d18cec433a": "1810d182-b4b5-11ea-84f7-3af9d3b32b71",  # Physical Thing
            "f71f7b9c-b25b-11e9-901e-a4d18cec433a": "9ffb6fcc-b4b4-11ea-84f7-3af9d3b32b71",  # Person
            "07883c9e-b25c-11e9-975a-a4d18cec433a": "d6774bfc-b4b4-11ea-84f7-3af9d3b32b71",  # Group
            "1b210ef3-b25c-11e9-a037-a4d18cec433a": "bdba56bc-b4b5-11ea-84f7-3af9d3b32b71",  # Collection or Set
            "707cbd78-ca7a-11e9-990b-a4d18cec433a": "0044f7da-b4b6-11ea-84f7-3af9d3b32b71",  # Digital Resources
            "cc8ed633-b25b-11e9-a13a-a4d18cec433a": "f6e89030-b4b4-11ea-84f7-3af9d3b32b71",  # Place
            "31e6b222-066c-11ea-b592-acde48001122": "3d461890-b4b5-11ea-84f7-3af9d3b32b71",  # Provenance Activity
            "a7b1a7c5-b25b-11e9-8a4e-a4d18cec433a": "6dad61aa-b4b5-11ea-84f7-3af9d3b32b71",  # Textual Work
            "ba892214-b25b-11e9-bf3e-a4d18cec433a": "933ee880-b4b5-11ea-84f7-3af9d3b32b71",  # Visual Work
            "0b9235d9-ca85-11e9-9fa2-a4d18cec433a": "734d1558-bfad-11ea-a62b-3af9d3b32b71",  # Activity
            "615b11ee-c457-11e9-910c-a4d18cec433a": "18faa214-c2c3-11ea-af13-3af9d3b32b71",  # Observation
            "5bece219-c456-11e9-8dcd-a4d18cec433a": "2022f91c-c2c1-11ea-af13-3af9d3b32b71",  # Modification
        }

        for tgraph in graphs:
            tgname = tgraph.name
            tgid = tgraph.pk
            if tgname == "Arches System Settings":
                continue
            sgid = graph_alignment.get(str(tgid), None)
            if not sgid:
                continue
            sgraph = archesmodels.GraphModel.objects.using("default").get(pk=sgid)

            print(f"Processing {sgraph.name} into {tgraph.name}")

            s_topnode = archesmodels.Node.objects.using("default").filter(graph=sgraph, istopnode=True)[0]
            t_topnode = archesmodels.Node.objects.using("target").filter(graph=tgraph, istopnode=True)[0]
            self.align_branches(s_topnode, t_topnode)

    def align_branches(self, snode, tnode):
        s_edges = archesmodels.Edge.objects.using("default").filter(domainnode=snode.pk)
        t_edges = archesmodels.Edge.objects.using("target").filter(domainnode=tnode.pk)
        for te in t_edges:
            poss = []
            tn = te.rangenode

            snid = self.forced_target_source.get(str(tn.pk), None)
            if snid:
                sn = archesmodels.Node.objects.using("default").get(pk=snid)
                poss = [sn]
            else:
                # Search for it
                for se in s_edges:
                    sn = se.rangenode
                    if se.ontologyproperty == te.ontologyproperty and sn.ontologyclass == tn.ontologyclass:
                        sdt = sn.datatype
                        tdt = tn.datatype
                        if sdt == tdt:
                            poss.append(sn)
                        elif sdt.startswith("concept") and tdt.startswith("concept"):
                            # just concept/concept-list difference
                            poss.append(sn)
                        elif sdt.startswith("resource-instance") and tdt.startswith("resource-instance"):
                            # ditto
                            poss.append(sn)
                        # else discard as not a match

            if len(poss) == 1:
                # We have a match, copy the description
                matchn = poss[0]
                # print(f"Match {tn.name} <--> {matchn.name}")
                tn.description = matchn.description
                tn.save(using="target")
                self.align_branches(matchn, tn)
            elif not poss:
                # No match
                if not tn.name.strip().endswith("source"):
                    print(f'*** No match in source data graph for "{tn.name}"')
            else:
                # Multiple
                print(f"!!! Ambiguous match in source data graph for {tn.name}")

    def handle_export(self, options):
        m = options["model"]
        if not m:
            # do all of them
            graphs = [x for x in archesmodels.GraphModel.objects.filter()]
        else:
            graphid = graph_uuid_map.get(m, None)
            if not graphid:
                # Check slug
                try:
                    graph = archesmodels.GraphModel.objects.get(slug=m)
                except:
                    print(f"Couldn't find a model definition for {m}; skipping")
                    return
            else:
                try:
                    graph = archesmodels.GraphModel.objects.get(pk=graphid)
                except:
                    print(f"Couldn't find a model for {graphid}; skipping")
                    return
            graphs = [graph]

        print(f"Exporting Documentation Fields to {options['dest']}")

        with open(options["dest"], "w") as cfh:
            writer = csv.writer(cfh, delimiter="\t",)
            writer.writerow(
                (
                    "Graph",
                    "NodeId",
                    "Node Name",
                    "Specific",
                    "General",
                    "Note",
                    "BranchId",
                    "FieldId",
                    "Class",
                    "Property",
                    "DataType",
                    "Count",
                    "Path",
                )
            )

            for graph in graphs:
                gname = graph.name
                if gname == "Arches System Settings":
                    continue
                print(f"Processing {gname}...")
                nodes = archesmodels.Node.objects.filter(graph_id=graph.pk)
                for node in nodes:
                    name = node.name
                    desc = node.description
                    dfields = self.parse_description(desc)
                    # Now write line to a CSV
                    inbound = archesmodels.Edge.objects.filter(rangenode=node.pk)
                    if inbound:
                        prop = self.make_readable(inbound[0].ontologyproperty)
                    else:
                        prop = ""
                    path = self.get_inbound_path(node)

                    if options["count"] and graph.isresource:
                        c = archesmodels.TileModel.objects.filter(nodegroup=node.nodegroup).count()
                    else:
                        c = -1
                    writer.writerow(
                        (
                            gname,
                            node.pk,
                            name,
                            dfields["specific"],
                            dfields["general"],
                            dfields["note"],
                            dfields["branchId"],
                            dfields["fieldId"],
                            self.make_readable(node.ontologyclass),
                            prop,
                            node.datatype,
                            c,
                            path,
                        )
                    )

    def get_inbound_path(self, node):
        plist = []
        inbound = archesmodels.Edge.objects.filter(rangenode=node.pk)
        while inbound:
            prop = self.make_readable(inbound[0].ontologyproperty)
            clss = self.make_readable(node.ontologyclass)
            plist.insert(0, f"{prop}[{clss}]")
            node = inbound[0].domainnode
            inbound = archesmodels.Edge.objects.filter(rangenode=node.pk)
        return "/".join(plist)

    def make_readable(self, prop):
        if prop:
            prop = prop.replace("http://www.cidoc-crm.org/cidoc-crm/", "crm:")
            prop = prop.replace("https://linked.art/ns/terms/", "la:")
            prop = prop.replace("http://www.w3.org/2001/XMLSchema#", "xsd:")
            prop = prop.replace("http://www.w3.org/2000/01/rdf-schema#", "rdfs:")
            prop = prop.replace("http://www.ics.forth.gr/isl/CRMdig/", "crmdig:")
            prop = prop.replace("http://www.ics.forth.gr/isl/CRMsci/", "crmsci:")
            prop = prop.replace("http://www.w3.org/2004/02/skos/core#", "skos:")
        else:
            prop = ""
        return prop

    def parse_description(self, desc):
        # Accept single string, return partitioned dict

        d = {"specific": "", "general": "", "note": "", "branchId": "", "fieldId": ""}

        if not desc:
            return d

        desc = desc.strip()
        if desc.startswith("# Specific:"):
            # Pop the fields off the end in turn
            re_order = [("fieldId", fieldre), ("branchId", branchre), ("note", notere), ("general", generalre), ("specific", specificre)]
            for (name, regex) in re_order:
                m = regex.search(desc)
                if m:
                    d[name] = m.group(1).strip()
                    desc = desc[: m.start()]
        else:
            d["specific"] = desc
        return d
