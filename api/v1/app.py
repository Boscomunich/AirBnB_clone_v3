#!/usr/bin/python3
'''A flask web api for Airbnb
'''
from api.v1.views import app_views
from flask import Flask, jsonify
from models import storage
import os
from flask_cors import CORS



app = Flask(__name__)
'''The flask web app instance named app'''
app.url_map.strict_slashes = False
app.register_blueprint(app_views)

cors = CORS(app, resources={r"/api/v1/*": {"origins": "*"}})

@app.teardown_appcontext
def teardown_flask(exception):
    '''The Flask app/request context end event listener.'''
    # print(exception)
    storage.close()

@app.errorhandler(404)
def error_404(error):
    '''Handles the 404 HTTP error code.'''
    return jsonify(error='Not found'), 404

if __name__ == '__main__':
    app_host = os.getenv('HBNB_API_HOST', '0.0.0.0')
    app_port = int(os.getenv('HBNB_API_PORT', '5000'))
    app.run(
        host=app_host,
        port=app_port,
        threaded=True)    
