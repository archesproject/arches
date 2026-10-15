from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import SimpleTestCase

from arches.management.commands.reseed_metadata_sequences import TABLES


class ReseedMetadataSequencesCommandTest(SimpleTestCase):
    @patch("arches.management.commands.reseed_metadata_sequences.connection.cursor")
    def test_reseeds_both_sequences_without_moving_them_backwards(self, cursor_mock):
        cursor = MagicMock()
        cursor_mock.return_value.__enter__.return_value = cursor

        call_command("reseed_metadata_sequences")

        self.assertEqual(cursor.execute.call_count, 2)
        for (table, sequence), call in zip(TABLES, cursor.execute.call_args_list):
            self.assertIn(table, call.args[0])
            self.assertIn(sequence, call.args[0])
            self.assertIn("GREATEST", call.args[0])
