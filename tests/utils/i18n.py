from django.test import SimpleTestCase
from django.utils import translation

from arches.app.models.system_settings import settings
from arches.app.utils.i18n import rank_label

# these tests can be run from the command line via
# python manage.py test tests.utils.i18n --settings="tests.test_settings"

class I18nTests(SimpleTestCase):
    def test_rank_label(self):
        translation.activate("es-ES")
        self.addCleanup(translation.activate, "en")

        old_system_lang = settings.LANGUAGE_CODE
        settings.LANGUAGE_CODE = "en-US"
        self.addCleanup(setattr, settings, "LANGUAGE_CODE", old_system_lang)

        # Match against explicitly specified language (fr-CA)
        self.assertGreater(rank_label("prefLabel", "fr-CA", "fr-CA"), rank_label("prefLabel", "fr", "fr-CA"))
        self.assertGreater(rank_label("prefLabel", "fr", "fr-CA"), rank_label("altLabel", "fr", "fr-CA"))
        self.assertGreater(rank_label("altLabel", "fr", "fr-CA"), rank_label("", "fr", "fr-CA"))

        # Match against user language (es-ES)
        self.assertGreater(rank_label("prefLabel", "es-ES"), rank_label("prefLabel", "es-MX"))
        self.assertGreater(rank_label("prefLabel", "es-ES"), rank_label("prefLabel", "en-US"))  # red herring (system)
        self.assertGreater(rank_label("prefLabel", "es"), rank_label("prefLabel", "de"))
        self.assertGreater(rank_label("prefLabel", "es"), rank_label("altLabel", "es"))
        self.assertGreater(rank_label("prefLabel", "es"), rank_label("altLabel", "en-US"))

        # Match against system language (en-US)
        self.assertGreater(rank_label("prefLabel", "en-US"), rank_label("prefLabel", "en-GB"))
        self.assertGreater(rank_label("prefLabel", "en"), rank_label("prefLabel", "de"))
        self.assertGreater(rank_label("prefLabel", "en"), rank_label("altLabel", "en"))
        self.assertGreater(rank_label("prefLabel", "en"), rank_label("altLabel", "en-US"))

        # Edge cases
        self.assertGreater(rank_label("prefLabel", "es"), rank_label("altLabel", "en-US"))
        self.assertGreater(rank_label("altLabel", "en-US"), rank_label("prefLabel", "de"))
