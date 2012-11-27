#!/usr/bin/env python

import os
import flask
from flask.ext.script import Manager


def create_app():
    from views import views

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
