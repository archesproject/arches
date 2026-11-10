from django.core.management.base import BaseCommand, CommandError

from arches.app.models.models import LocalBasemap
from arches.app.utils.local_basemap_extractor import extract_local_basemap
from arches.app.utils.local_basemap_installer import (
    LocalBasemapInstallError,
    install_local_basemap,
)
from arches.app.utils.local_basemap_manager import (
    basemap_summaries,
    remove_local_basemap,
    restore_online_basemaps,
    set_default_basemap,
)

OPERATIONS_NEEDING_A_NAME = ["extract", "install", "remove", "set-default"]


class Command(BaseCommand):
    help = (
        "Manages basemaps served by this instance from PMTiles archives under "
        "LOCAL_BASEMAPS_ROOT. `extract` downloads an area of OpenStreetMap from "
        "a Protomaps daily build and installs it, or refreshes it when run again "
        "with the same --name; `install` installs an archive you already have; "
        "`list`, `remove` and `set-default` manage basemaps; `restore-online` "
        "brings back the online basemaps an --offline install removed."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "operation",
            choices=[*OPERATIONS_NEEDING_A_NAME, "list", "restore-online"],
        )
        parser.add_argument(
            "archive_path",
            nargs="?",
            help="install: a Protomaps .pmtiles archive, such as one made by pmtiles extract",
        )
        parser.add_argument(
            "--name",
            help=(
                "A short name for the basemap, also its folder under "
                "LOCAL_BASEMAPS_ROOT. set-default also takes an online basemap's title."
            ),
        )
        parser.add_argument(
            "--title",
            help="The name shown in the basemap list (default: --name, or the current title)",
        )
        parser.add_argument(
            "--flavor",
            choices=LocalBasemap.FLAVORS,
            help="(default: light, or the current flavor)",
        )
        parser.add_argument(
            "--bbox", help="extract: the area as west,south,east,north in degrees"
        )
        parser.add_argument(
            "--region",
            dest="region_path",
            help="extract: the area as a GeoJSON file of a Polygon or MultiPolygon",
        )
        parser.add_argument(
            "--from-default-bounds",
            action="store_true",
            dest="use_default_bounds",
            help="extract: the area of the DEFAULT_BOUNDS System Setting",
        )
        parser.add_argument(
            "--maxzoom",
            type=int,
            default=15,
            dest="max_zoom",
            help="extract: the most detailed zoom (default and most detailed: 15)",
        )
        parser.add_argument(
            "--build",
            help="extract: the Protomaps daily build, as YYYYMMDD (default: the latest)",
        )
        parser.add_argument(
            "--no-overview",
            action="store_false",
            dest="with_overview",
            help="extract: skip the shared world overview of zooms 0-6 (about 45 MB)",
        )
        parser.add_argument(
            "--refresh-overview",
            action="store_true",
            help="extract: extract the shared world overview again from this build",
        )
        parser.add_argument(
            "--overview",
            dest="overview_archive_path",
            help="install: a world archive with low zooms, drawn where the basemap's archive stops",
        )
        parser.add_argument(
            "--assets",
            dest="assets_directory",
            help="install: a folder with the fonts/ and sprites/ the style uses, copied into LOCAL_BASEMAPS_ROOT",
        )
        parser.add_argument(
            "--default",
            action="store_true",
            dest="make_default",
            help="Show this basemap when maps open",
        )
        parser.add_argument(
            "--offline",
            action="store_true",
            help="Remove basemaps, sources and sprites that load from the internet",
        )
        parser.add_argument(
            "--fit-default-bounds",
            action="store_true",
            dest="fit_bounds",
            help="Make maps open on the basemap's area",
        )
        parser.add_argument(
            "--noinput",
            action="store_false",
            dest="interactive",
            help="extract: don't ask before downloading",
        )

    def handle(self, *args, **options):
        operation = options["operation"]
        if operation in OPERATIONS_NEEDING_A_NAME and not options["name"]:
            raise CommandError(f"{operation} needs --name.")
        try:
            if operation == "list":
                self.list_basemaps()
            elif operation == "remove":
                remove_local_basemap(options["name"], self.stdout.write)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Removed the local basemap '{options['name']}'."
                    )
                )
            elif operation == "set-default":
                map_layer = set_default_basemap(options["name"])
                self.stdout.write(
                    self.style.SUCCESS(f"'{map_layer.name}' is the default basemap.")
                )
            elif operation == "restore-online":
                restore_online_basemaps(self.stdout.write)
            else:
                local_basemap = self.install(options)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Installed the local basemap '{local_basemap.name}'."
                    )
                )
        except LocalBasemapInstallError as error:
            raise CommandError(error)

    def install(self, options):
        install_options = {
            "title": options["title"],
            "flavor": options["flavor"],
            "make_default": options["make_default"],
            "offline": options["offline"],
            "fit_bounds": options["fit_bounds"],
        }
        if options["operation"] == "extract":
            return extract_local_basemap(
                options["name"],
                self.stdout.write,
                lambda estimated_size: self.confirm_download(
                    estimated_size, options["interactive"]
                ),
                bbox=options["bbox"],
                region_path=options["region_path"],
                use_default_bounds=options["use_default_bounds"],
                max_zoom=options["max_zoom"],
                build=options["build"],
                with_overview=options["with_overview"],
                refresh_overview=options["refresh_overview"],
                **install_options,
            )
        if not options["archive_path"]:
            raise CommandError("install needs the path of a .pmtiles archive.")
        return install_local_basemap(
            options["archive_path"],
            options["name"],
            self.stdout.write,
            overview_archive_path=options["overview_archive_path"],
            assets_directory=options["assets_directory"],
            **install_options,
        )

    def list_basemaps(self):
        summaries = basemap_summaries()
        if not summaries:
            self.stdout.write("No basemaps.")
            return
        columns = ["default", "name", "title", "flavor", "build", "size", "area"]
        rows = [
            [
                "*" if summary["default"] else "",
                summary["name"],
                summary["title"],
                summary.get("flavor", "online"),
                summary.get("build", ""),
                summary.get("size", ""),
                summary.get("area", ""),
            ]
            for summary in summaries
        ]
        column_widths = [
            max(len(row[column_index]) for row in [columns, *rows])
            for column_index in range(len(columns))
        ]
        for row in [columns, *rows]:
            self.stdout.write(
                "  ".join(
                    cell.ljust(column_width)
                    for cell, column_width in zip(row, column_widths)
                ).rstrip()
            )

    @staticmethod
    def confirm_download(estimated_size, interactive):
        if not interactive:
            return True
        answer = input(f"Download about {estimated_size}? [y/N] ")
        return answer.strip().lower() in ("y", "yes")
