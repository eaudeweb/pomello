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
            {'description': 'shrimps (x2)',
             'date': date(2012, 11, 25),
             'value': D('-21.42')},
        ])

    def test_compute_joins_history_items_from_same_order(self):
        from balance import compute
        history = {
            'orders': {
                date(2012, 11, 23): [
                  {'price': 30,
                   'qty': 3,
                   'name': 'soup',
                   'eat': {date(2012, 11, 25): {'anton': 1},
                           date(2012, 11, 26): {'anton': 1}}},
                  {'price': 75,
                   'qty': 7,
                   'name': 'shrimps',
                    'eat': {date(2012, 11, 25): {'anton': 2}}},
                ],
            }
        }
        results = compute(history)
        self.assertEqual(results['anton']['history'], [
            {'description': 'soup + shrimps (x2)',
             'date': date(2012, 11, 25),
             'value': D('-31.42')},
            {'description': 'soup',
             'date': date(2012, 11, 26),
             'value': D('-10.00')},
        ])

    def test_fee_is_added_to_spending(self):
        from balance import compute
        history = {
            'orders': {
                date(2012, 11, 23): [
                    {'price': 80,
                     'qty': 10,
                     'fee': 0.05,
                     'name': '',
                     'eat': {date(2012, 11, 25): {'anton': 1}}},
                ],
            },
        }
        results = compute(history)
        self.assertEqual(results['anton']['balance'], D('-8.40'))

    def test_fee_total_is_increased_with_contribution(self):
        from balance import compute
        history = {
            'orders': {
                date(2012, 11, 23): [
                    {'price': 80,
                     'qty': 10,
                     'fee': 0.05,
                     'name': '',
                     'eat': {date(2012, 11, 25): {'anton': 2}}},
                ],
            },
        }
        results = compute(history)
        self.assertEqual(results['rulment']['balance'], D('0.80'))

    def test_tip_is_deduced_from_rulment(self):
        from balance import compute
        history = {
            'orders': {
                date(2012, 11, 23): [
                    {'type': 'tip',
                     'value': 2},
                ],
            },
        }
        results = compute(history)
        self.assertEqual(results['rulment']['balance'], D('-2.00'))
