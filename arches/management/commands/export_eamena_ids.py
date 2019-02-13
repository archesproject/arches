import os
import unicodecsv
import uuid
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from arches.app.models.entity import Entity
from arches.app.models.models import Entities

from arches.app.utils.skos import SKOSReader

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('-d', '--destination', action='store', default=None,
            help="path to skosfile"),
    )

    def handle(self, *args, **options):

        if options['destination'] is None:
            outpath = "eamena_ids_by_uuids.csv"

        else:
            outpath = options['destination']

        self.export_eamena_ids(outpath)

    def export_eamena_ids(self,outpath):

        lookup = dict()
        resconfigs = settings.RESOURCE_TYPE_CONFIGS()

        for res, configs in resconfigs.iteritems():
            uniqueid = configs['primary_name_lookup']['entity_type']
            entities = Entities.objects.filter(entitytypeid=res)
            for e in entities:
                entity = Entity().get(e.pk)
                eam = [i.value for i in entity.child_entities if i.entitytypeid == uniqueid][0]
                lookup[eam] = e.pk

        with open(outpath, "wb") as opencsv:
            writer = unicodecsv.writer(opencsv)
            writer.writerow(["eamena id", "postload_uuid"])
            for k in sorted(lookup):
                writer.writerow([k, lookup[k]])
