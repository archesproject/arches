"""Backwards compatibility for applications that moved into arches.extensions.

Until 8.2 these were separately distributed top-level packages. Projects refer
to them by module path in more places than their own imports: INSTALLED_APPS,
ELASTICSEARCH_CUSTOM_INDEXES, TERM_SEARCH_TYPES and ES_MAPPING_MODIFIER_CLASSES
all name dotted paths that Django resolves with import_module. The finder
installed here keeps every one of those working, with a DeprecationWarning.
"""

import importlib
import importlib.abc
import importlib.machinery
import sys
import warnings

from django.core.checks import Tags, Warning as CheckWarning, register

from arches.extensions import BUNDLED_APPLICATIONS

#: Former top-level module path -> current one. Identical to
#: BUNDLED_APPLICATIONS because each application's label is its former name.
MOVED_MODULES = dict(BUNDLED_APPLICATIONS)


class _MovedModuleLoader(importlib.abc.Loader):
    def __init__(self, new_name):
        self.new_name = new_name

    def create_module(self, spec):
        return importlib.import_module(self.new_name)

    def exec_module(self, module):
        """The target module is already executed by create_module()."""


class BundledApplicationFinder(importlib.abc.MetaPathFinder):
    """Resolve former top-level module paths to their arches.extensions home."""

    def find_spec(self, fullname, path=None, target=None):
        root, _, remainder = fullname.partition(".")
        if root not in MOVED_MODULES:
            return None
        new_name = MOVED_MODULES[root] + ("." + remainder if remainder else "")
        warnings.warn(
            f"{fullname!r} has moved to {new_name!r}. The compatibility alias "
            f"will be removed in Arches 9.0; update imports, INSTALLED_APPS and "
            f"any dotted paths in your settings.",
            DeprecationWarning,
            stacklevel=2,
        )
        return importlib.machinery.ModuleSpec(
            fullname, _MovedModuleLoader(new_name), is_package=not remainder
        )


def install():
    """Install the finder ahead of the standard path finders.

    It has to precede PathFinder. A submodule lookup such as
    arches_querysets.models is resolved against the parent module's __path__,
    which points into arches/extensions; PathFinder would find the file there
    and load it a second time under the legacy name, leaving two module objects
    and two copies of every class.
    """
    if not any(isinstance(f, BundledApplicationFinder) for f in sys.meta_path):
        sys.meta_path.insert(0, BundledApplicationFinder())


@register(Tags.compatibility)
def check_legacy_application_paths(app_configs, **kwargs):
    """Flag INSTALLED_APPS entries still naming the pre-8.2 module paths.

    These keep working through the finder above, but only until 9.0.
    """
    from django.conf import settings

    return [
        CheckWarning(
            f"{entry!r} in INSTALLED_APPS has moved to {MOVED_MODULES[entry]!r}.",
            hint=(
                "The old path resolves through a compatibility alias that will be "
                "removed in Arches 9.0. Update INSTALLED_APPS, and any dotted "
                "module paths elsewhere in your settings."
            ),
            obj=entry,
            id="arches.W002",
        )
        for entry in getattr(settings, "INSTALLED_APPS", ())
        if entry in MOVED_MODULES
    ]
