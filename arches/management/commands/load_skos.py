import os
import csv
import uuid
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from arches.app.models.concept import Concept
from arches.app.models.models import ConceptRelations

from arches.app.utils.skos import SKOSReader

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        # make_option('-o', '--operation', action='store',
            # type='choice', 
            # choices=['load','link'],
            # help="path to skosfile"),
        make_option('-s', '--source', action='store', default=None,
            help="path to skosfile"),
    )

    def handle(self, *args, **options):

        if options['source'] is None:
            filepath = settings.SKOS_FILE_LOCATION

        else:
            if not os.path.isfile(options['source']):
                print "invalid source."
                exit()
            filepath = options['source']

        schemeid = self.load_skos(filepath)
        self.link_dropdowns(schemeid)

    def load_skos(self,skosfile):

        print "loading skos: " + os.path.basename(skosfile)
        skos = SKOSReader()
        rdf = skos.read_file(skosfile)
        ret = skos.save_concepts_from_skos(rdf)

        schemeid = [i.id for i in ret.nodes if i.nodetype == "ConceptScheme"][0]
        print "DONE"

        return schemeid

    def link_dropdowns(self,schemeid):

        print "linking topconcepts with dropdown lists"
        lookups = {}
        lfile = r"C:\arches\eamena\RESOURCE_GRAPHS\concept_dropdown_lookup.csv"

        with open(lfile, "rb") as openfile:
            reader = csv.reader(openfile)
            headers = reader.next()
            for row in reader:
                if row[1] != "":
                    lookups[row[0]] = row[1]

        # make the graph of the full scheme
        full_graph = Concept().get(
                id=schemeid,
                include_subconcepts=True,
                depth_limit=2,
            )

        # make a dictionary of all the top concepts
        topconcepts = {}
        missing_tc = []
        for tc in full_graph.subconcepts:
            for v in tc.values:
                if v.category == "label" and v.language == "en-US":
                    topconcepts[v.value] = tc
                    if not v.value in lookups.values():
                        missing_tc.append(v.value)

        # these are the relations from the dropdown scheme to actual collections
        dropdown_relations = ConceptRelations.objects.filter(
            conceptidfrom_id="00000000-0000-0000-0000-000000000003"
        )

        # these are the ids of all the collections themselves
        collection_ids = [i.conceptidto_id for i in dropdown_relations]

        # iterate the collection ids. For each get the actual concept,
        # then its name, and then, if it's been linked with a topconcept,
        # add the subconcepts of that topconcept to the dropdown by saving
        # a new ConceptRelations object for the link.
        missing_n = []
        for cid in collection_ids:

            cconcept = Concept().get(id=cid)
            name = cconcept.legacyoid

            if name in lookups:

                tc = topconcepts[lookups[name]]
                for sc in tc.subconcepts:
                    newrelation = ConceptRelations(
                        relationid = uuid.uuid4(),
                        conceptidfrom_id=cid,
                        conceptidto_id=sc.id,
                        relationtype_id="member"
                    )
                    newrelation.save()
            else:
                missing_n.append(name)

        # print a summary of the missing linkages
        missing_n.sort()
        print "these nodes have no dropdown contents associated with them:"
        for i in missing_n:
            print " ",i
        missing_tc.sort()
        print "these top concepts are not associated with any nodes:"
        for i in missing_tc:
            print " ", i

        print "DONE"