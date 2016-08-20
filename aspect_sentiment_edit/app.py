"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
import argparse

# only need to change sys.path only once
# since sys.path is shared global variable
import os,sys
parentpath = os.path.abspath("..")
if parentpath not in sys.path:
    sys.path.append(parentpath)

from reviews_proxy import ReviewsMongoProxy

from flask import Flask
app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

from routes import * # it must after 'app' is defined, because routes needs 'app'
if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug",action="store_true")
    parser.add_argument("-n","--dbname",required=True)
    args = parser.parse_args()

    # for test purpose, we just hardcode 'tripadvisor' as databasename
    # laster, we should read dbname from configuration
    app.mongoproxy = ReviewsMongoProxy(args.dbname)
    app.debug= args.debug
    app.run(HOST, PORT)
