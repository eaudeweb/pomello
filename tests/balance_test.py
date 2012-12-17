import unittest
from datetime import date
from decimal import Decimal as D


def compute(history):
    from balance import compute
    return compute(history)


class BalanceTest(unittest.TestCase):

    def test_empty_history_returns_empty_result(self):
        accounts = compute({})['accounts']
        self.assertEqual(accounts.keys(), ['uneaten'])

    def test_order_with_no_consumption_returns_empty_result(self):
        history = {
            'orders': {
                date(2012, 11, 23): [
                    {'price': 55,
                     'qty': 10,
                     'name': ''},
                ],
            },
        }
        accounts = compute(history)['accounts']
        self.assertEqual(accounts.keys(), ['uneaten'])

    def test_compute_sum_of_contributions(self):
        history = {
            'contributions': {
                'initial': {'anton': 13},
                date(2012, 11, 23): {'anton': 9.15},
            }
        }
        accounts = compute(history)['accounts']
        self.assertEqual(accounts['anton'].balance, D('22.15'))

    def test_compute_sum_of_consumptions(self):
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
        accounts = compute(history)['accounts']
        self.assertEqual(accounts['anton'].balance, D('-26.92'))

    def test_compute_saves_personal_history_entries(self):
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
        accounts = compute(history)['accounts']
        self.assertEqual(accounts['anton'].history, [
            {'description': 'initial',
             'date': None,
             'order_date': None,
             'value': D('13.00')},
            {'description': 'input',
             'date': date(2012, 11, 23),
             'order_date': None,
             'value': D('9.15')},
            {'description': 'shrimps (x2)',
             'date': date(2012, 11, 25),
             'order_date': date(2012, 11, 23),
             'value': D('-21.42')},
        ])

    def test_compute_joins_history_items_from_same_order(self):
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
        accounts = compute(history)['accounts']
        self.assertEqual(accounts['anton'].history, [
            {'description': 'soup + shrimps (x2)',
             'date': date(2012, 11, 25),
             'order_date': date(2012, 11, 23),
             'value': D('-31.42')},
            {'description': 'soup',
             'date': date(2012, 11, 26),
             'order_date': date(2012, 11, 23),
             'value': D('-10.00')},
        ])

    def test_fee_is_added_to_spending(self):
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
        accounts = compute(history)['accounts']
        self.assertEqual(accounts['anton'].balance, D('-8.40'))

    def test_fee_total_is_increased_with_contribution(self):
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
        accounts = compute(history)['accounts']
        self.assertEqual(accounts['rulment'].balance, D('0.80'))

    def test_tip_is_deduced_from_rulment(self):
        history = {
            'orders': {
                date(2012, 11, 23): [
                    {'type': 'tip',
                     'value': 2},
                ],
            },
        }
        accounts = compute(history)['accounts']
        self.assertEqual(accounts['rulment'].balance, D('-2.00'))

    def test_losses_are_deduced_from_regie(self):
        history = {
            'orders': {
                date(2012, 11, 23): [
                    {'price': 11,
                     'qty': 2,
                     'name': '',
                     'eat': {'trashed': 2}},
                ],
            },
        }
        accounts = compute(history)['accounts']
        self.assertEqual(accounts['rulment'].balance, D('-11.00'))

    def test_regie_history_contains_additions_and_subtractions(self):
        history = {
            'orders': {
                date(2012, 11, 23): [
                    {'price': 32,
                     'qty': 4,
                     'fee': 0.05,
                     'name': '',
                     'eat': {date(2012, 11, 25): {'anton': 2},
                             'trashed': 2}},
                    {'type': 'tip',
                     'value': 2},
                ],
            },
        }
        accounts = compute(history)['accounts']
        self.assertEqual(accounts['rulment'].history, [
            {'description': u"tip",
             'date': date(2012, 11, 23),
             'order_date': date(2012, 11, 23),
             'value': D('-2.00')},
            {'description': u"trashed",
             'date': date(2012, 11, 23),
             'order_date': date(2012, 11, 23),
             'value': D('-16.00')},
            {'description': u"contribution anton",
             'date': date(2012, 11, 25),
             'order_date': date(2012, 11, 23),
             'value': D('0.80')},
        ])

    def test_complain_if_comsumption_does_not_add_up(self):
        history = {
            'orders': {
                date(2012, 11, 23): [
                    {'price': 80,
                     'qty': 10,
                     'fee': 0.05,
                     'name': 'shrimps',
                     'eat': {date(2012, 11, 25): {'anton': 2},
                             'trashed': 3}},
                ],
            },
        }
        with self.assertRaises(ValueError) as e:
            compute(history)
        self.assertEqual("'shrimps' does not add up: delta=5",
                         e.exception.message)

    def test_computes_sum_of_uneaten_food(self):
        history = {
            'orders': {
                date(2012, 11, 23): [
                    {'price': 80,
                     'qty': 10,
                     'fee': 0.05,
                     'name': 'shrimps',
                     'eat': {date(2012, 11, 25): {'anton': 2}}},
                ],
            },
        }
        accounts = compute(history)['accounts']
        self.assertEqual(accounts['uneaten'].balance, D('-64.00'))

    def test_preserve_list_of_ordered_food(self):
        NOV23 = date(2012, 11, 23)
        NOV25 = date(2012, 11, 25)
        history = {
            'orders': {
                NOV23: [
                    {'name': 'shrimps', 'price': 50, 'qty': 10},
                    {'name': 'fries', 'price': 20, 'qty': 10},
                ],
                NOV25: [
                    {'name': 'carrots', 'price': 30, 'qty': 10},
                ],
            }
        }
        orders = compute(history)['orders']
        self.assertDictContainsSubset(
            {'name': 'shrimps', 'price': 50, 'qty': 10},
            orders[NOV23][0])

    def test_tip_is_removed_from_order(self):
        NOV23 = date(2012, 11, 23)
        history = {
            'orders': {
                NOV23: [{'type': 'tip', 'value': 5},
                        {'name': 'shrimps', 'price': 50, 'qty': 10}]}}
        orders = compute(history)['orders']
        self.assertEqual(len(orders[NOV23]), 1)

    def test_order_items_have_remaining_quantity(self):
        NOV23 = date(2012, 11, 23)
        history = {
            'orders': {
                NOV23: [{
                    'name': 'shrimps',
                    'price': 50,
                    'qty': 10,
                    'eat': {NOV23: {'anton': 2}},
                }]}}
        orders = compute(history)['orders']
        self.assertEqual(orders[NOV23][0]['remaining'], 8)
