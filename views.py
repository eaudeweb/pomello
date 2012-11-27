import flask
from datetime import date
from path import path
import yaml
import balance

HISTORY_DIR = path(__file__).abspath().parent / 'history'

views = flask.Blueprint(__name__, 'views')


def _get_balance():
    with (HISTORY_DIR / '2012-11.yaml').open('rb') as f:
        history = yaml.load(f)
    return balance.compute(history)


@views.route('/')
def home():
    results = _get_balance()
    return flask.render_template('overview.html', results=results)


@views.route('/person/<string:name>')
def person(name):
    results = _get_balance()
    return flask.render_template('person.html', **{
        'name': name,
        'history': sorted(results[name]['history'],
                          key=lambda h: h['date'] or date(2000, 1, 1)),
    })
