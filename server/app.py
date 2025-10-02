#!/usr/bin/env python3

from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User, Review, Game

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)


# -------------------------------
# Helper functions
# -------------------------------
def get_json_or_400():
    if not request.is_json:
        return None, make_response({"error": "Request must be JSON"}, 400)
    return request.get_json(), None


def serialize_list(items):
    return [item.to_dict() for item in items]


# -------------------------------
# Routes
# -------------------------------
@app.route('/')
def index():
    return jsonify({"message": "Index for Game/Review/User API"}), 200


# ---------- GAMES ----------
@app.route('/games', methods=['GET'])
def get_games():
    games = serialize_list(Game.query.all())
    return jsonify(games), 200


@app.route('/games/<int:id>', methods=['GET'])
def get_game(id):
    game = Game.query.get(id)
    if not game:
        return jsonify({"error": "Game not found"}), 404
    return jsonify(game.to_dict()), 200


# ---------- USERS ----------
@app.route('/users', methods=['GET'])
def get_users():
    users = serialize_list(User.query.all())
    return jsonify(users), 200


# ---------- REVIEWS ----------
@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    if request.method == 'GET':
        all_reviews = serialize_list(Review.query.all())
        return jsonify(all_reviews), 200

    elif request.method == 'POST':
        data, error = get_json_or_400()
        if error:
            return error

        # Validate required fields
        required_fields = ["score", "comment", "user_id", "game_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field '{field}'"}), 400

        # Validate foreign keys exist
        if not User.query.get(data["user_id"]):
            return jsonify({"error": "User does not exist"}), 400
        if not Game.query.get(data["game_id"]):
            return jsonify({"error": "Game does not exist"}), 400

        new_review = Review(
            score=data["score"],
            comment=data["comment"],
            user_id=data["user_id"],
            game_id=data["game_id"]
        )

        db.session.add(new_review)
        db.session.commit()

        return jsonify(new_review.to_dict()), 201


@app.route('/reviews/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def review_by_id(id):
    review = Review.query.get(id)
    if not review:
        return jsonify({"error": "Review not found"}), 404

    if request.method == 'GET':
        return jsonify(review.to_dict()), 200

    elif request.method == 'PATCH':
        data, error = get_json_or_400()
        if error:
            return error

        # Only allow certain fields to be updated
        allowed_fields = ["score", "comment"]
        for field in allowed_fields:
            if field in data:
                setattr(review, field, data[field])

        db.session.commit()
        return jsonify(review.to_dict()), 200

    elif request.method == 'DELETE':
        db.session.delete(review)
        db.session.commit()
        return jsonify({"delete_successful": True, "message": "Review deleted"}), 204


# -------------------------------
# Run app
# -------------------------------
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5555))
    app.run(port=port, debug=True)
