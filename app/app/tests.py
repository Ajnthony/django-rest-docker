"""
test test
"""

from django.test import SimpleTestCase
from app import calc


class CalcTests(SimpleTestCase):
    def test_add_numbers(self):
        res = calc.add(6, 4)
        self.assertEqual(res, 10)

    def test_subtract_numbers(self):
        res = calc.subtract(6, 4)
        self.assertEqual(res, 2)
