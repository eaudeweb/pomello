import unittest
from datetime import date
from decimal import Decimal as D


class BalanceTest(unittest.TestCase):

    def test_empty_history_returns_empty_result(self):
        from balance import compute
        results = compute({})
        self.assertEqual(results, {})

    def test_order_with_no_consumption_returns_empty_result(self):
        from balance import compute
        history = {
            'orders': {
                date(2012, 11, 23): [
                    {'price': 55,
                     'qty': 10,
                     'name': ''},
                ],
            },
        }
        results = compute(history)
        self.assertEqual(results, {})

    def test_trashed_key_is_skipped(self):
        from balance import compute
        history = {
            'orders': {
                date(2012, 11, 23): [
                    {'price': 55,
                     'qty': 10,
                     'name': '',
                     'eat': {'trashed': 1}},
                ],
            },
        }
        results = compute(history)
        self.assertEqual(results, {})

    def test_compute_sum_of_contributions(self):
        from balance import compute
        history = {
            'contributions': {
                'initial': {'anton': 13},
                date(2012, 11, 23): {'anton': 9.15},
            }
        }
        results = compute(history)
        self.assertEqual(results['anton']['balance'], D('22.15'))

    def test_compute_sum_of_consumptions(self):
        from balance import compute
        history = {
            'orders': {
                date(2012, 11, 20): [
                  {'price': 55,
                   'qty': 10,
                   'name': '',
                    'eat': {date(2012, 11, 20): {'anton': 1}}},
                ],
                date(2012, 11, 23): [
                  {'price': 75,
                   'qty': 7,
                   'name': '',
                    'eat': {date(2012, 11, 20): {'anton': 2}}},
                ],
            }
        }
        results = compute(history)
        self.assertEqual(results['anton']['balance'], D('-26.92'))

    def test_compute_saves_personal_history_entries(self):
        from balance import compute
        history = {
            'contributions': {
                'initial': {'anton': 13},
                date(2012, 11, 23): {'anton': 9.15},
            },
            'orders': {
                date(2012, 11, 23): [
                  {'price': 75,
                   'qty': 7,
                   'name': 'shrimps',
                    'eat': {date(2012, 11, 25): {'anton': 2}}},
                ],
            }
        }
        results = compute(history)
        self.assertEqual(results['anton']['history'], [
            {'description': 'initial',
             'date': None,
             'value': D('13.00')},
            {'description': 'input',
             'date': date(2012, 11, 23),
             'value': D('9.15')},
            {'description': 'shrimps',
             'date': date(2012, 11, 25),
             'value': D('-21.42')},
        ])
