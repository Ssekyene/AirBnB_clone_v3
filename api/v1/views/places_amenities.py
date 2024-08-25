#!/usr/bin/python3
"""
route for handling place and amenities linking
"""
from flask import jsonify, abort
from os import getenv
from api.v1.views import app_views
from models import storage
from models.place import Place
from models.amenity import Amenity


@app_views.route("/places/<place_id>/amenities",
                 methods=["GET"],
                 strict_slashes=False)
def amenity_by_place(place_id):
    """
    get all amenities of a place
    """
    obj = storage.get(Place, place_id)

    if obj is None:
        abort(404)

    amenities_list = [amenity.to_dict() for amenity in obj.amenities]
    return jsonify(amenities_list), 200


@app_views.route("/places/<place_id>/amenities/<amenity_id>",
                 methods=["DELETE"],
                 strict_slashes=False)
def delete_place_amenity(place_id, amenity_id):
    """
    for DBStorage: deletes Amenity object from amenities relationship
    with Place object
    for FileStorage: removes Amenity ID from the list amenity_ids
    of a Place object
    :param place_id: place id
    :param amenity_id: amenity id
    :return: returns empty json or error
    """
    if not storage.get(Place, place_id):
        abort(404)
    if not storage.get(Amenity, amenity_id):
        abort(404)

    place_obj = storage.get(Place, place_id)
    found = False

    if getenv("HBNB_TYPE_STORAGE") == "db":
        for amenity_obj in place_obj.amenities:
            if amenity_obj.id == amenity_id:
                place_obj.amenities.remove(amenity_obj)
                found = True
                break
    else:
        for a_id in place_obj.amenity_ids:
            if a_id == amenity_id:
                place_obj.amenity_ids.remove(a_id)
                found = True
                break

    if not found:
        abort(404)
    else:
        storage.save()
        resp = jsonify({})
        resp.status_code = 200
        return resp


@app_views.route("/places/<place_id>/amenities/<amenity_id>",
                 methods=["POST"],
                 strict_slashes=False)
def link_amenity_to_place(place_id, amenity_id):
    """
    for DBStorage: appends an amenity object to amenities
    relationship with Place object
    for FileStorage: appends an amenity id to the list
    amenity_ids of Place object
    :param place_id: place id
    :param amenity_id: amenity id
    :return: returns Amenity obj existing or added or error
    """

    place_obj = storage.get(Place, place_id)
    amenity_obj = storage.get(Amenity, amenity_id)
    found_amenity = None

    if not place_obj or not amenity_obj:
        abort(404)

    for a_obj in place_obj.amenities:
        if a_obj.id == amenity_id:
            found_amenity = a_obj
            break

    if found_amenity is not None:
        return jsonify(found_amenity.to_dict()), 200

    if getenv("HBNB_TYPE_STORAGE") == "db":
        place_obj.amenities.append(amenity_obj)
    else:
        place_obj.amenity_ids.append(amenity_obj.id)

    storage.save()

    resp = jsonify(amenity_obj.to_dict())
    resp.status_code = 201
    return resp
