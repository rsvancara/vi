#!/usr/bin/env python3

from visualintrigue import app
from werkzeug.contrib.fixers import ProxyFix

if __name__ == "__main__":

    app.debug = True

    app.wsgi_app = ProxyFix(app.wsgi_app)

    app.run(host="0.0.0.0")

