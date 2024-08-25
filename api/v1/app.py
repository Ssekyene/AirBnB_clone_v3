#!/usr/bin/python3
"""The app module: for registering the blueprint and starting flask"""

import os
from models import storage
from api.v1.views import app_views
from flask import Flask, jsonify, make_response
from flask_cors import CORS


app = Flask(__name__)
app.register_blueprint(app_views)
CORS(app, resources={r"/*": {"origins": "0.0.0.0"}})


@app.teardown_appcontext
def tear_down(error=None):
    """calls storage.close()"""
    storage.close()


@app.errorhandler(404)
def page_not_found(error):
    """page not found error handler"""
    return make_response(jsonify({"error": "Not found"}), 404)


if __name__ == "__main__":
    # Set up environment
    host = os.getenv('HBNB_API_HOST', "0.0.0.0")
    port = int(os.getenv('HBNB_API_PORT', 5000))
    app.run(host=host, port=port, threaded=True)
