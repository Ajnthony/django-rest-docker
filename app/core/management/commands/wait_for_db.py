"""
Django command to wait for db to be ready to roll.
"""

import time
from psycopg2 import OperationalError as Psycopg2OpError
# Error thatn Django throws when db is not ready
from django.db.utils import OperationalError

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        # entrypoint for command
        self.stdout.write('Waiting for DB -')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('DB not available - waiting 1 second...')
                time.sleep(1)  # 1 second

        self.stdout.write(self.style.SUCCESS('DB is ready'))
