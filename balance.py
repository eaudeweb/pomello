from decimal import Decimal as D
from collections import defaultdict


QUANT = D('.01')


def compute(history):
    results = defaultdict(lambda: {'balance': D(0), 'history': []})
    remaining = []

    for label, day_values in history.get('contributions', {}).items():
        for name, raw_value in day_values.items():
            entry = results[name]
            value = D(raw_value).quantize(QUANT)
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
            history_item['value'] = value.quantize(QUANT)
            entry['history'].append(history_item)

    for day_of_order, day_orders in history.get('orders', {}).items():
        consumption = defaultdict(list)
        for order in day_orders:
            order_type = order.get('type', 'food')
            if order_type == 'tip':
                value = -D(order['value']).quantize(QUANT)
                results['rulment']['balance'] += value
                results['rulment']['history'].append({
                    'date': day_of_order,
                    'value': value,
                    'description': u"tip",
                })
                continue
            per_eat = (D(order['price']) / D(order['qty'])).quantize(QUANT)
            order_remaining = {
                'date': day_of_order,
                'name': order['name'],
                'qty': order['qty'],
                'per_eat': per_eat,
            }
            remaining.append(order_remaining)
            fee = (D(order.get('fee', 0)) * per_eat).quantize(QUANT)
            for eat_date, day_eats in order.get('eat', {}).items():
                if eat_date == 'trashed':
                    value = -day_eats * per_eat
                    results['rulment']['balance'] += value
                    results['rulment']['history'].append({
                        'date': day_of_order,
                        'value': value,
                        'description': u"trashed",
                    })
                    order_remaining['closed'] = day_eats
                    continue
                for name, pieces in day_eats.items():
                    value = - pieces * (per_eat + fee)
                    if fee:
                        fee_value = pieces * fee
                        results['rulment']['balance'] += fee_value
                        results['rulment']['history'].append({
                            'date': eat_date,
                            'value': fee_value,
                            'description': u"contribution " + name,
                        })
                    entry = results[name]
                    entry['balance'] += value
                    description = order['name']
                    if pieces != 1:
                        description += u" (x%s)" % pieces
                    consumption[eat_date, name].append((description, value))
                    order_remaining['qty'] -= pieces
        for ((eat_date, name), entries) in sorted(consumption.items()):
            results[name]['history'].append({
                'date': eat_date,
                'value': sum(v for d, v in entries).quantize(QUANT),
                'description': u" + ".join(d for d, v in entries),
            })

    for name in results:
        results[name]['balance'] = results[name]['balance'].quantize(QUANT)
    rulment_history = results.get('rulment', {}).get('history', [])
    rulment_history.sort(key=lambda e: (e['date'], e['description']))

    uneaten = D('0')
    for item in remaining:
        if 'closed' in item:
            delta = item['qty'] - item['closed']
            if delta != 0:
                raise ValueError("%r does not add up: delta=%r"
                                 % (item['name'], delta))
        else:
            uneaten -= item['qty'] * item['per_eat']

    results['uneaten'] = {'balance': uneaten}

    return {
        'results': dict(results),
    }
