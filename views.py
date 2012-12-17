import os
import flask
from datetime import date, datetime
import yaml
import jinja2
import balance

views = flask.Blueprint(__name__, 'views')


def _get_balance():
    with open(os.environ['HISTORY_FILE'], 'rb') as f:
        history = yaml.load(f)
    return balance.compute(history)


@views.route('/')
def home():
    accounts = _get_balance()['accounts']
    return flask.render_template('overview.html', accounts=accounts)


@views.route('/person/<string:name>')
def person(name):
    accounts = _get_balance()['accounts']
    return flask.render_template('person.html', **{
        'name': name,
        'history': sorted(accounts[name].history,
                          key=lambda h: h['date'] or date(2000, 1, 1)),
    })


@views.route('/order/<string:order_date_str>')
def order(order_date_str):
    data = _get_balance()
    order_date = datetime.strptime(order_date_str, '%Y-%m-%d').date()
    return flask.render_template('order.html', **{
        'date': order_date,
        'order': data['orders'][order_date],
    })


@views.app_template_filter('money')
def money(value):
    css_class = 'money-negative' if value < 0 else 'money-positive'
    value = abs(value)
    return jinja2.Markup('<span class="{css_class}">{value:.2f}</span>'
                         .format(**locals()))
