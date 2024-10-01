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

import json
import os
import uuid
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from arches.app.models.models import ETLModule


class Command(BaseCommand):
    """
    Commands for managing Arches etl modules

    """

    def add_arguments(self, parser):
        etl_modules = [module.componentname for module in ETLModule.objects.all()]
        parser.add_argument("module", nargs="?", choices=etl_modules)
        parser.add_argument(
            "-s",
            "--source",
            action="store",
            dest="source",
            default="",
            help="Extension file to be loaded",
        )
        parser.add_argument(
            "-c",
            "--config",
            action="store",
            dest="config",
            default="",
            help="The configuration for the etl-module to run",
        )

    def handle(self, *args, **options):
        self.run(
            module=options["module"], source=options["source"], config=options["config"]
        )

    def run(self, module, source, config):
        """
        Run the specified module
        Params --source(-s), and --config(-c)

        """
        loadid = str(uuid.uuid4())
        if os.path.exists(config):
            with open(config) as f:
                config = json.load(f)
        else:
            config = {}
        try:
            etl_module = ETLModule.objects.get(componentname=module)
            config["module"] = etl_module.etlmoduleid
            EtlModule = etl_module.get_class_module()(loadid=loadid, params=config)
        except ETLModule.DoesNotExist:
            try:
                moduleid = uuid.UUID(module)
                config["module"] = moduleid
                EtlModule = ETLModule.objects.get(pk=moduleid).get_class_module()(
                    loadid=loadid, params=config
                )
            except (ValueError, TypeError):
                etl_modules = ETLModule.objects.all()
                self.stdout.write(
                    _("You must supply the valid name or the uuid for the etl module.")
                )
                for etl_module in etl_modules:
                    self.stdout.write(
                        "\t{0}\t{1}\n".format(
                            etl_module.componentname, etl_module.etlmoduleid
                        )
                    )
                return

        import_function = getattr(EtlModule, "cli")
        response = import_function(source)
        if response["success"]:
            self.stdout.write(_("succeeded"))
        else:
            self.stdout.write(response["data"]["message"])
