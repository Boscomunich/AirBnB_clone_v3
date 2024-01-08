#!/usr/bin/python3
""" Methods that handle the reviews's of places request"""
from models.review import Review
from models.place import Place
from models.user import User
from models import storage
from api.v1.views import app_views
from flask import abort, jsonify, make_response, request


@app_views.route('/places/<place_id>/reviews', methods=['GET'],
                 strict_slashes=False)
def get_reviews(place_id):
    """
    Gets the list of all reviews of a place
    """
    place = storage.get(Place, place_id)

    if not place:
        abort(404)
    all_reviews = [review.to_dict() for review in place.reviews]
    return jsonify(all_reviews)


@app_views.route('/reviews/<review_id>', methods=['GET'], strict_slashes=False)
def get_review(review_id):
    """
    Gets the review with the id
    """
    review = storage.get(Review, review_id)

    if not review:
        abort(404)
    return jsonify(review.to_dict())


@app_views.route('/reviews/<review_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_review(review_id):
    """
    Deletes a review obj with the id
    """

    review = storage.get(Review, review_id)

    if not review:
        abort(404)
    storage.delete(review)
    storage.save()
    return make_response(jsonify({}), 200)


@app_views.route('/places/<place_id>/reviews', methods=['POST'],
                 strict_slashes=False)
def post_review(place_id):
    """
    Creates a review with post req
    """
    place = storage.get(Place, place_id)
    data = request.get_json()

    if not place:
        abort(404)
    if not data:
        abort(400, description="Not a JSON")
    if 'user_id' not in data:
        abort(400, description="Missing user_id")

    user = storage.get(User, data['user_id'])

    if not user:
        abort(404)
    if 'text' not in request.get_json():
        abort(400, description="Missing text")

    data['place_id'] = place_id
    review_obj = Review(**data)
    review_obj.save()
    return make_response(jsonify(review_obj.to_dict()), 201)


@app_views.route('/reviews/<review_id>', methods=['PUT'], strict_slashes=False)
def put_review(review_id):
    """
    Updates a review with put req
    """
    review = storage.get(Review, review_id)
    data = request.get_json()

    if not review:
        abort(404)
    if not data:
        abort(400, description="Not a JSON")

    ignored_keys = ['id', 'user_id', 'place_id', 'created_at', 'updated_at']

    for key, value in data.items():
        if key not in ignored_keys:
            setattr(review, key, value)
    storage.save()
    return make_response(jsonify(review.to_dict()), 200)
