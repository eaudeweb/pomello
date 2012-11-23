import unittest
from decimal import Decimal as D
from collections import defaultdict


CENT = D('.01')


def compute(history):
    results = defaultdict(lambda: {'balance': D(0), 'history': []})

    for day_values in history.get('contributions', {}).values():
        for name, value in day_values.items():
            results[name]['balance'] += D(value).quantize(CENT)

    for day_orsers in history.get('orders', {}).values():
        for order in day_orsers:
            per_eat = (D(order['price']) / D(order['qty'])).quantize(CENT)
            for day_eats in order['eat'].values():
                for name, value in day_eats.items():
                    results[name]['balance'] -= D(value) * per_eat

    return dict(results)


class BalanceTest(unittest.TestCase):

    def test_compute_sum_of_contributions(self):
        history = {
            'contributions': {
                'initial': {'anton': 13},
                '2012-11-23': {'anton': 9.15},
            }
        }
        results = compute(history)
        self.assertEqual(results['anton']['balance'], D('22.15'))

    def test_compute_sum_of_consumptions(self):
        history = {
            'orders': {
                '2012-11-20': [
                  {'price': 55,
                   'qty': 10,
                    'eat': {'2012-11-20': {'anton': 1}}},
                ],
                '2012-11-23': [
                  {'price': 75,
                   'qty': 7,
                    'eat': {'2012-11-20': {'anton': 2}}},
                ],
            }
        }
        results = compute(history)
        self.assertEqual(results['anton']['balance'], D('-26.92'))
