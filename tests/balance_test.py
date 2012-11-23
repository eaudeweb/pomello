import unittest
from decimal import Decimal as D
from collections import defaultdict


def compute(history):
    balance = defaultdict(D)

    for day_values in history['contributions'].values():
        for name, value in day_values.items():
            balance[name] += D(value).quantize(D('.01'))

    return dict(balance)


class BalanceTest(unittest.TestCase):

    def test_compute_sum_of_contributions(self):
        history = {
            'contributions': {
                'initial': {'anton': 13},
                '2012-11-23': {'anton': 9.15},
            }
        }
        balance = compute(history)
        self.assertEqual(balance['anton'], D('22.15'))
