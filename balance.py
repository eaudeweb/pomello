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
                'description': str(label),
                'value': value.quantize(CENT),
            }
            entry['history'].append(history_item)

    for day_orsers in history.get('orders', {}).values():
        for order in day_orsers:
            per_eat = (D(order['price']) / D(order['qty'])).quantize(CENT)
            for eat_date, day_eats in order.get('eat', {}).items():
                if eat_date == 'trashed':
                    continue
                for name, raw_value in day_eats.items():
                    value = - D(raw_value).quantize(CENT) * per_eat
                    entry = results[name]
                    entry['balance'] += value
                    history_item = {
                        'value': value.quantize(CENT),
                        'description': (u"{order[name]} {eat_date}"
                                        .format(**locals())),
                    }
                    entry['history'].append(history_item)

    return dict(results)
