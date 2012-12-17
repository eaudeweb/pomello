from decimal import Decimal as D
from collections import defaultdict


QUANT = D('.01')


class Account(object):

    def __init__(self):
        self.history = []

    def add(self, date, value, description, order_date=None):
        self.history.append({
            'date': date,
            'order_date': order_date,
            'value': value,
            'description': description,
        })

    @property
    def balance(self):
        return sum(i['value'] for i in self.history)


def compute(history):
    accounts = defaultdict(Account)
    remaining = []
    contributions = history.get('contributions', {})
    orders = history.get('orders', {})

    for label, day_values in contributions.items():
        for name, raw_value in day_values.items():
            value = D(raw_value).quantize(QUANT)
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
            accounts[name].add(**history_item)

    for day_of_order, day_orders in orders.items():
        consumption = defaultdict(list)
        for order in day_orders:
            order_type = order.get('type', 'food')
            if order_type == 'tip':
                value = -D(order['value']).quantize(QUANT)
                accounts['rulment'].add(**{
                    'date': day_of_order,
                    'order_date': day_of_order,
                    'value': value,
                    'description': u"tip",
                })
                continue
            per_eat = (D(order['price']) / D(order['qty'])).quantize(QUANT)
            order['remaining'] = order['qty']
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
                    accounts['rulment'].add(**{
                        'date': day_of_order,
                        'order_date': day_of_order,
                        'value': value,
                        'description': u"trashed",
                    })
                    order_remaining['closed'] = day_eats
                    continue
                for name, pieces in day_eats.items():
                    value = - pieces * (per_eat + fee)
                    if fee:
                        fee_value = pieces * fee
                        accounts['rulment'].add(**{
                            'date': eat_date,
                            'order_date': day_of_order,
                            'value': fee_value,
                            'description': u"contribution " + name,
                        })
                    description = order['name']
                    if pieces != 1:
                        description += u" (x%s)" % pieces
                    consumption[eat_date, name].append((description, value))
                    order_remaining['qty'] -= pieces
                    order['remaining'] -= pieces
        for ((eat_date, name), entries) in sorted(consumption.items()):
            accounts[name].add(**{
                'date': eat_date,
                'order_date': day_of_order,
                'value': sum(v for d, v in entries).quantize(QUANT),
                'description': u" + ".join(d for d, v in entries),
            })

    rulment_history = (accounts['rulment'].history
                       if 'rulment' in accounts else [])
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

    accounts['uneaten'] = Account()
    accounts['uneaten'].add(None, uneaten, "uneaten")

    for day in orders:
        orders[day] = [i for i in orders[day] if i.get('type') != 'tip']

    return {
        'accounts': dict(accounts),
        'orders': orders,
    }
