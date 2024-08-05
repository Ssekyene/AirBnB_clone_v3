#!/usr/bin/python3
"""The index module creates routes on the obj app_views"""

from api.v1.views import app_views
from flask import Flask, jsonify
from models import storage


@app_views.route('/status', methods=['GET'], strict_slashes=False)
def status():
    """route /status on the object app_views"""
    return jsonify({"status": "OK"})


@app_views.route('/stats', methods=['GET'], strict_slashes=False)
def get_stats():
    """endpoint that retrieves the no of each obj by type"""
    classes = {
        "amenities": "Amenity",
        "cities": "City",
        "places": "Place",
        "reviews": "Review",
        "states": "State",
        "users": "User"
    }

    stats = {}
    for key, value in classes.items():
        count = storage.count(value)
        stats[key] = count
    return jsonify(stats)
