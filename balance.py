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
            if label == 'initial':
                history_item = {
                    'description': u"initial",
                    'date': None,
                }
            else:
                history_item = {
                    'description': u"input",
                    'date': label,
                }
            history_item['value'] = value.quantize(CENT)
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
                        'date': eat_date,
                        'description': order['name'],
                    }
                    entry['history'].append(history_item)

    for name in results:
        results[name]['balance'] = results[name]['balance'].quantize(CENT)
    return dict(results)
