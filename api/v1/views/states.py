#!/usr/bin/python3
"""Views for State obj that handles default RESTFUL API
   functions: get_state
               get_state_id
               delete_state
               create_state
               update_state
"""

from flask import Flask, jsonify, abort, request, make_response
from models import storage
from api.v1.views import app_views
from models.state import State


@app_views.route('/states', methods=['GET'], strict_slashes=False)
def get_state():
    """Retrieves list of all State object: GET /api/v1/states"""
    state_list = [state.to_dict() for state in storage.all('State').values()]
    return jsonify(state_list)


@app_views.route('states/<state_id>', methods=['GET'], strict_slashes=False)
def get_state_id(state_id):
    """Retrieves a State object: GET /api/v1/states/<state_id>"""
    state = storage.get("State", state_id)
    if state is None:
        abort(404)
    return jsonify(state.to_dict())


@app_views.route('states/<state_id>', methods=['DELETE'], strict_slashes=False)
def delete_state(state_id):
    """Deletes a State object:: DELETE /api/v1/states/<state_id>"""
    state = storage.get("State", state_id)
    if state is None:
        abort(404)
    state.delete()
    storage.save()
    return make_response(jsonify({}), 200)


@app_views.route('/states', methods=['POST'], strict_slashes=False)
def create_state():
    """Creates a new State obj in the db"""
    if not request.get_json():
        return jsonify({"error": "Not a JSON"}), 400
    elif "name" not in request.get_json():
        return jsonify({"error": "Missing name"}), 400
    else:
        data = request.get_json()
        obj = State(**data)
        obj.save()
        return jsonify(obj.to_dict()), 201


@app_views.route('states/<state_id>', methods=['PUT'], strict_slashes=False)
def update_state(state_id):
    """Updates a state obj in the db"""
    if not request.get_json():
        return jsonify({"error": "Not a JSON"}), 400

    obj = storage.get("State", state_id)
    if obj is None:
        abort(404)
    data = request.get_json()
    obj.name = data['name']
    obj.save()
    return jsonify(obj.to_dict()), 200
