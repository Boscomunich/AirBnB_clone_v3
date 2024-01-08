#!/usr/bin/python3
""" Methods that handle the places's request """
from models.state import State
from models.city import City
from models.place import Place
from models.user import User
from models.amenity import Amenity
from models import storage
from api.v1.views import app_views
from flask import abort, jsonify, request, make_response


@app_views.route('/cities/<city_id>/places', methods=['GET'],
                 strict_slashes=False)
def get_places(city_id):
    """
    Gets the list of all places
    """
    city = storage.get(City, city_id)

    if not city:
        abort(404)
    places = [place.to_dict() for place in city.places]
    return jsonify(places)


@app_views.route('/places/<place_id>', methods=['GET'], strict_slashes=False)
def get_place(place_id):
    """
    Gets the place with the id
    """
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_place(place_id):
    """
    Deletes a place Object with the id
    """

    place = storage.get(Place, place_id)

    if not place:
        abort(404)
    storage.delete(place)
    storage.save()

    return make_response(jsonify({}), 200)


@app_views.route('/cities/<city_id>/places', methods=['POST'],
                 strict_slashes=False)
def post_place(city_id):
    """
    Creates a place with post req
    """
    city = storage.get(City, city_id)
    data = request.get_json()

    if not city:
        abort(404)
    if not data:
        abort(400, description="Not a JSON")
    if 'user_id' not in data:
        abort(400, description="Missing user_id")

    user = storage.get(User, data['user_id'])

    if not user:
        abort(404)

    if 'name' not in request.get_json():
        abort(400, description="Missing name")

    data["city_id"] = city_id
    instance = Place(**data)
    instance.save()
    return make_response(jsonify(instance.to_dict()), 201)


@app_views.route('/places/<place_id>', methods=['PUT'], strict_slashes=False)
def put_place(place_id):
    """
    Updates a place with put req
    """
    place = storage.get(Place, place_id)
    data = request.get_json()

    if not place:
        abort(404)
    if not data:
        abort(400, description="Not a JSON")

    ignored_keys = ['id', 'user_id', 'city_id', 'created_at', 'updated_at']

    for key, value in data.items():
        if key not in ignored_keys:
            setattr(place, key, value)
    storage.save()
    return make_response(jsonify(place.to_dict()), 200)


@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def places_search():
    """
    Task 15 Search
    Searches for a place and returns a list of places
    """
    if request.get_json() is None:
        abort(400, description="Not a JSON")

    data = request.get_json()

    if data and len(data):
        states = data.get('states', None)
        cities = data.get('cities', None)
        amenities = data.get('amenities', None)

    if not data or not len(data) or (
            not states and
            not cities and
            not amenities):
        places = storage.all(Place).values()
        places_list = []
        for place in places:
            places_list.append(place.to_dict())
        return jsonify(places_list)

    places_list = []
    if states:
        states_obj = [storage.get(State, s_id) for s_id in states]
        for state in states_obj:
            if state:
                for city in state.cities:
                    if city:
                        for place in city.places:
                            places_list.append(place)

    if cities:
        city_obj = [storage.get(City, c_id) for c_id in cities]
        for city in city_obj:
            if city:
                for place in city.places:
                    if place not in places_list:
                        places_list.append(place)

    if amenities:
        if not places_list:
            places_list = storage.all(Place).values()
        amenities_obj = [storage.get(Amenity, amenity_id)
                         for amenity_id in amenities]
        places_list = [place for place in places_list
                       if all([amen in place.amenities
                               for amen in amenities_obj])]

    places = []
    for pl in places_list:
        dict = pl.to_dict()
        dict.pop('amenities', None)
        places.append(dict)
    return jsonify(places)
