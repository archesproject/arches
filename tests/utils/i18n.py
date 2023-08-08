from django.test import SimpleTestCase
from django.utils import translation

from arches.app.models.system_settings import settings
from arches.app.utils.i18n import rank_label


class I18nTests(SimpleTestCase):
    def test_rank_label(self):
        translation.activate("es-ES")
        self.addCleanup(translation.activate, "en")

        old_system_lang = settings.LANGUAGE_CODE
        settings.LANGUAGE_CODE = "en-US"
        self.addCleanup(setattr, settings, "LANGUAGE_CODE", old_system_lang)

        cases = [
            # Match an explicitly given language
            (100, "prefLabel", "fr-CA", "fr-CA"),
            (40, "altLabel", "fr-CA", "fr-CA"),
            (10, "", "fr-CA", "fr-CA"),
            # ...inexactly
            (50, "prefLabel", "fr-FR", "fr-CA"),
            (20, "altLabel", "fr-fr", "fr-CA"),
            (5, "", "fr", "fr-CA"),

            # Otherwise fall back to user language (es-ES)
            # Good values
            (100, "prefLabel", "es-ES", ""),
            (40, "altLabel", "es-ES", ""),
            (10, "", "es-ES", ""),
            # Pretty good, but inexact
            (50, "prefLabel", "es-MX", ""),
            (20, "altLabel", "es-MX", ""),
            (5, "", "es-MX", ""),
            # Mediocre values: they at least match system language (en-US)
            (30, "prefLabel", "en-US", ""),
            (12, "altLabel", "en-US", ""),
            (3, "", "en-US", ""),
            # Mediocre and inexact
            (20, "prefLabel", "en-GB", ""),
            (8, "altLabel", "en-GB", ""),
            (2, "", "en-GB", ""),

            # Poor values: no relationship to any desired language,
            # but at least preferred/alt labels are better than
            # non-preferred labels
            (10, "prefLabel", "", ""),
            (4, "altLabel", "", ""),
            (1, "", "", ""),
        ]

        # TODO(jtw): when we drop nose, add subTest for friendlier output
        for case in cases:
            score, kind, label_lang, sought_lang = case
            result = rank_label(kind, label_lang, sought_lang)
            self.assertEqual(score, result)
