import flask
from path import path
import yaml
import balance

HISTORY_DIR = path(__file__).abspath().parent / 'history'

views = flask.Blueprint(__name__, 'views')


@views.route('/')
def home():
    with (HISTORY_DIR / '2012-11.yaml').open('rb') as f:
        history = yaml.load(f)
    results = balance.compute(history)
    return flask.render_template('overview.html', results=results)


@views.app_template_filter('py3format')
def py3format(spec, *args, **kwargs):
    return spec.format(*args, **kwargs)
