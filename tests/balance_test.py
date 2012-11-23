import unittest
from decimal import Decimal as D
from collections import defaultdict


CENT = D('.01')


def compute(history):
    results = defaultdict(lambda: {'balance': D(0), 'history': []})

    for label, day_values in history.get('contributions', {}).items():
        for name, raw_value in day_values.items():
            entry = results[name]
            value = D(raw_value).quantize(CENT)
            entry['balance'] += value
            history_item = {
                'description': label,
                'value': value.quantize(CENT),
            }
            entry['history'].append(history_item)

    for day_orsers in history.get('orders', {}).values():
        for order in day_orsers:
            per_eat = (D(order['price']) / D(order['qty'])).quantize(CENT)
            for eat_date, day_eats in order['eat'].items():
                for name, raw_value in day_eats.items():
                    value = - D(raw_value).quantize(CENT) * per_eat
                    entry = results[name]
                    entry['balance'] += value
                    history_item = {
                        'value': value.quantize(CENT),
                        'description': ('{order[name]} {eat_date}'
                                        .format(**locals())),
                    }
                    entry['history'].append(history_item)

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
                   'name': '',
                    'eat': {'2012-11-20': {'anton': 1}}},
                ],
                '2012-11-23': [
                  {'price': 75,
                   'qty': 7,
                   'name': '',
                    'eat': {'2012-11-20': {'anton': 2}}},
                ],
            }
        }
        results = compute(history)
        self.assertEqual(results['anton']['balance'], D('-26.92'))

    def test_compute_saves_personal_history_entries(self):
        history = {
            'contributions': {
                'initial': {'anton': 13},
                '2012-11-23': {'anton': 9.15},
            },
            'orders': {
                '2012-11-23': [
                  {'price': 75,
                   'qty': 7,
                   'name': 'shrimps',
                    'eat': {'2012-11-25': {'anton': 2}}},
                ],
            }
        }
        results = compute(history)
        self.assertEqual(results['anton']['history'], [
            {'description': 'initial',
             'value': D('13.00')},
            {'description': '2012-11-23',
             'value': D('9.15')},
            {'description': 'shrimps 2012-11-25',
             'value': D('-21.42')},
        ])
