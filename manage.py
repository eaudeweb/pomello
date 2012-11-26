#!/usr/bin/env python

import os
import flask
from flask.ext.script import Manager
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


def create_app():
    app = flask.Flask(__name__)
    app.debug = bool(os.environ.get('DEBUG'))
    app.register_blueprint(views)

    @app.route('/crashme')
    def crashme():
        raise RuntimeError("Here's your exception")

    return app


manager = Manager(create_app, with_default_commands=False)


@manager.option('listen')
def runserver(listen):
    if ':' in listen:
        (host, port) = listen.split(':')
    else:
        (host, port) = ('127.0.0.1', listen)
    app = flask.current_app
    app.run(host=host, port=int(port), use_reloader=app.debug)


if __name__ == '__main__':
    manager.run()
