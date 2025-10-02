from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, CheckConstraint
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

# Naming conventions for foreign keys
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

# ---------------------------
# Models
# ---------------------------
class Game(db.Model, SerializerMixin):
    __tablename__ = 'games'

    serialize_rules = ('-reviews.game',)

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    genre = db.Column(db.String(50))
    platform = db.Column(db.String(50))
    price = db.Column(db.Integer, CheckConstraint('price >= 0'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now(), nullable=False)

    reviews = db.relationship('Review', back_populates='game', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Game {self.id}: {self.title} ({self.platform})>"


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    serialize_rules = ('-reviews.user',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now(), nullable=False)

    reviews = db.relationship('Review', back_populates='user', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.id}: {self.name}>"


class Review(db.Model, SerializerMixin):
    __tablename__ = 'reviews'

    serialize_rules = ('-game.reviews', '-user.reviews',)

    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, CheckConstraint('score >= 0 AND score <= 10'), nullable=False)
    comment = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now(), nullable=False)

    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    game = db.relationship('Game', back_populates='reviews')
    user = db.relationship('User', back_populates='reviews')

    def __repr__(self):
        return f"<Review {self.id}: Game {self.game_id}, User {self.user_id}, Score {self.score}>"

    # ---------------------------
    # Validations
    # ---------------------------
    @validates('score')
    def validate_score(self, key, value):
        if value < 0 or value > 10:
            raise ValueError("Score must be between 0 and 10")
        return value
