import uuid

from django.core.management.base import BaseCommand
import django.apps


class Command(BaseCommand):

    help = "finds any arches objects whose primary key is the input uuid and" "returns these objects in the form of a list."

    def add_arguments(self, parser):
        parser.add_argument("uuid", help="input the uuid string to find")

    def handle(self, *args, **options):
        self.find_uuid(options["uuid"])

    def find_uuid(self, in_uuid):

        ## check for valid uuid input
        try:
            val = uuid.UUID(in_uuid, version=4)
        except ValueError:
            self.stdout.write("  -- this is not a valid uuid")
            return False

        ## search all models and see if the UUID matches an existing object
        objs = []
        for m in django.apps.apps.get_models():
            if not m.__module__.startswith("arches"):
                continue
            if m._meta.pk.get_internal_type() != "UUIDField":
                continue
            ob = m.objects.filter(pk=in_uuid)
            objs += ob

        ## return False if nothing was found
        if not objs:
            self.stdout.write("  -- this uuid doesn't match any objects in your database")
            return False

        ## print summary of found objects
        self.stdout.write(80 * "=")
        self.stdout.write("This UUID is the primary key for {} object{}:".format(len(objs), "s" if len(objs) > 1 else ""))
        for o in objs:
            self.stdout.write(80 * "-")
            self.stdout.write(str(o))
            keys = list(vars(o).keys())
            keys.sort()
            for k in keys:
                self.stdout.write(k)
                self.stdout.write("  {}".format(vars(o)[k]))
        self.stdout.write(80 * "=")
        return objs
