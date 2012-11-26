#!/usr/bin/env python

import os
import flask
from flask.ext.script import Manager


views = flask.Blueprint(__name__, 'views')


@views.route('/')
def home():
    return flask.render_template('overview.html')


def create_app():
    app = flask.Flask(__name__)
    app.debug = bool(os.environ.get('DEBUG'))
    app.register_blueprint(views)

    @app.route('/crashme')
    def crashme():
        raise RuntimeError("Here's your exception")

    return app


manager = Manager(create_app, with_default_commands=False)


@manager.option('port', type=int)
def runserver(port):
    app = flask.current_app
    app.run(port=port, use_reloader=app.debug)


if __name__ == '__main__':
    manager.run()
