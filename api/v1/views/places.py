#!/usr/bin/python3
'''
    RESTful API for class Place
'''
from flask import Flask, jsonify, abort, request
from models import storage
from api.v1.views import app_views
from models.place import Place
from models.city import City
from models.user import User
from models.amenity import Amenity
from os import getenv


@app_views.route('/cities/<city_id>/places', methods=['GET'],
                 strict_slashes=False)
def get_place_by_city(city_id):
    '''
        return places in city using GET
    '''
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    places_list = [place.to_dict() for place in city.places]
    return jsonify(places_list), 200


@app_views.route('/places/<place_id>', methods=['GET'], strict_slashes=False)
def get_place_id(place_id):
    '''
        return place and its id using GET
    '''
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict()), 200


@app_views.route('/places/<place_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_place(place_id):
    '''
        DELETE place obj given place_id
    '''
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    place.delete()
    storage.save()
    return jsonify({}), 200


@app_views.route('/cities/<city_id>/places', methods=['POST'],
                 strict_slashes=False)
def create_place(city_id):
    '''
        create new place obj through city association using POST
    '''
    if not request.get_json():
        return jsonify({"error": "Not a JSON"}), 400
    elif "name" not in request.get_json():
        return jsonify({"error": "Missing name"}), 400
    elif "user_id" not in request.get_json():
        return jsonify({"error": "Missing user_id"}), 400
    else:
        obj_data = request.get_json()
        city = storage.get(City, city_id)
        user = storage.get(User, obj_data['user_id'])
        if city is None or user is None:
            abort(404)
        obj_data['city_id'] = city.id
        obj_data['user_id'] = user.id
        obj = Place(**obj_data)
        obj.save()
        return jsonify(obj.to_dict()), 201


@app_views.route('/places/<place_id>', methods=['PUT'], strict_slashes=False)
def update_place(place_id):
    '''
        update existing place object using PUT
    '''
    if not request.get_json():
        return jsonify({"error": "Not a JSON"}), 400

    obj = storage.get(Place, place_id)
    if obj is None:
        abort(404)
    obj_data = request.get_json()
    ignore = ("id", "user_id", "created_at", "updated_at")
    for k, v in obj_data.items():
        if k not in ignore:
            setattr(obj, k, v)
    obj.save()
    return jsonify(obj.to_dict()), 200


@app_views.route('/places_search', methods=['POST'])
def places_search():
    """
        places route to handle http method for request to search places
    """

    obj_data = request.get_json()
    if obj_data is None:
        abort(400, 'Not a JSON')

    states = obj_data.get('states')
    if states and len(states) > 0:
        cities_in_states_ids = set([city.id
                                    for city in storage.all(City).values()
                                    if city.state_id in states])
    else:
        cities_in_states_ids = set()

    cities = obj_data.get('cities')
    if cities and len(cities) > 0:
        cities_ids = set([c_id for c_id in cities if storage.get(City, c_id)])
    else:
        cities_ids = set()

    state_cities_ids = cities_in_states_ids.union(cities_ids)
    all_places = [p for p in storage.all(Place).values()]

    amenities = obj_data.get('amenities')
    if len(state_cities_ids) > 0:
        all_places = [p for p in all_places if p.city_id in state_cities_ids]
        if amenities is None or len(amenities) == 0:
            result = [place.to_dict() for place in all_places]
            return jsonify(result)
        else:
            places_with_amenities = []
            amenities_ids = set([a_id for a_id in amenities if
                                 storage.get(Amenity, a_id)])
            for place in all_places:
                place_amenities_ids = None
                if place.amenities:
                    if getenv("STORAGE_TYPE") == 'db':
                        place_amenities_ids = [a.id for a in place.amenities]
                    else:
                        place_amenities_ids = place.amenity_ids

                if place_amenities_ids and all([a_id in place_amenities_ids
                                                for a_id in amenities_ids]):
                    places_with_amenities.append(place)
            result = [place.to_dict() for place in places_with_amenities]
            return jsonify(result)
    else:
        result = [place.to_dict() for place in all_places]
        return jsonify(result)
