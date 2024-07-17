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

from contextlib import contextmanager

from arches.app.models.system_settings import settings
from arches.app.utils.context_processors import app_settings
from django.test.runner import DiscoverRunner

from arches.app.search.mappings import (
    prepare_terms_index,
    delete_terms_index,
    prepare_concepts_index,
    delete_concepts_index,
    prepare_search_index,
    delete_search_index,
)

# these tests can be run from the command line via
# python manage.py test tests --pattern="*.py" --settings="tests.test_settings"


class ArchesTestRunner(DiscoverRunner):
    def __init__(self, *args, **kwargs) -> None:
        kwargs["debug_mode"] = True
        # Unless the user has something other than the Django default, give them
        # what they probably want.
        if kwargs["pattern"] == "test*.py":
            kwargs["pattern"] = "*.py"
        super().__init__(*args, **kwargs)

    def setup_databases(self, **kwargs):
        ret = super().setup_databases(**kwargs)

        app_settings()  # adds languages to system
        prepare_terms_index(create=True)
        prepare_concepts_index(create=True)
        prepare_search_index(create=True)

        return ret

    def teardown_databases(self, old_config, **kwargs):
        delete_terms_index()
        delete_concepts_index()
        delete_search_index()

        super().teardown_databases(old_config, **kwargs)


@contextmanager
def sync_overridden_test_settings_to_arches():
    """Django's @override_settings test util acts on django.conf.settings,
    which is not enough for us, because we use SystemSettings at runtime.

    This context manager swaps in the overridden django.conf.settings for SystemSettings.
    """
    from django.conf import settings as patched_settings

    original_settings_wrapped = settings._wrapped
    try:
        settings._wrapped = patched_settings._wrapped
        yield
    finally:
        settings._wrapped = original_settings_wrapped
