"""
Test custom django management commands
"""

from unittest.mock import patch
from psycopg2 import OperationalError as Psycopg2Error
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    # test commands
    def test_wait_for_db_ready(self, patched_check):
        # test waiting for db if it's ready
        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        # test waiting for db when getting OperationalError
        # deliberately throw 5 fake errors when getting OperationalError
        # and the for the sixth time I'm getting True
        patched_check.side_effect = [Psycopg2Error]*2 + \
            [OperationalError]*3 + [True]

        call_command('wait_for_db')

        # make the value match to the num of errors above, including True
        self.assertEqual(patched_check.call_count, 6)

        patched_check.assert_called_with(databases=['default'])
