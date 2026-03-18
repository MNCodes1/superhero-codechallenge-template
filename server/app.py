#!/usr/bin/env python3

from flask import Flask, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)

api = Api(app)

# ---------------- ROOT ----------------
@app.route('/')
def index():
    return '<h1>Code challenge</h1>'


# ---------------- HERO RESOURCES ----------------
class Heroes(Resource):
    def get(self):
        heroes = Hero.query.all()
        return [
            hero.to_dict(only=("id", "name", "super_name"))
            for hero in heroes
        ]


class HeroByID(Resource):
    def get(self, id):
        hero = Hero.query.get(id)
        if not hero:
            return {"error": "Hero not found"}, 404
        return hero.to_dict()


# ---------------- POWER RESOURCES ----------------
class Powers(Resource):
    def get(self):
        powers = Power.query.all()
        return [
            power.to_dict(only=("id", "name", "description"))
            for power in powers
        ]


class PowerByID(Resource):
    def get(self, id):
        power = Power.query.get(id)
        if not power:
            return {"error": "Power not found"}, 404
        return power.to_dict(only=("id", "name", "description"))

    def patch(self, id):
        power = Power.query.get(id)
        if not power:
            return {"error": "Power not found"}, 404

        data = request.get_json() or {}
        description = data.get("description")

        try:
            if description is not None:
                power.description = description  # triggers model validation

            db.session.commit()
            return power.to_dict(only=("id", "name", "description")), 200

        except ValueError:
            return {"errors": ["validation errors"]}, 400


# ---------------- HEROPOWER RESOURCE ----------------
class HeroPowers(Resource):
    def post(self):
        data = request.get_json() or {}

        strength = data.get("strength")
        hero_id = data.get("hero_id")
        power_id = data.get("power_id")

        # Validate required fields
        if not all([strength, hero_id, power_id]):
            return {"errors": ["validation errors"]}, 400

        # Validate foreign keys
        hero = Hero.query.get(hero_id)
        power = Power.query.get(power_id)
        if not hero or not power:
            return {"errors": ["validation errors"]}, 400

        try:
            # Create HeroPower (triggers strength validation)
            hero_power = HeroPower(
                strength=strength,
                hero_id=hero_id,
                power_id=power_id
            )

            db.session.add(hero_power)
            db.session.commit()

            # Explicit serialization to prevent recursion errors
            return hero_power.to_dict(only=(
                "id",
                "strength",
                "hero_id",
                "power_id",
                "hero.id",
                "hero.name",
                "hero.super_name",
                "power.id",
                "power.name",
                "power.description"
            )), 200

        except ValueError:
            return {"errors": ["validation errors"]}, 400


# ---------------- ROUTE REGISTRATION ----------------
api.add_resource(Heroes, "/heroes")
api.add_resource(HeroByID, "/heroes/<int:id>")
api.add_resource(Powers, "/powers")
api.add_resource(PowerByID, "/powers/<int:id>")
api.add_resource(HeroPowers, "/hero_powers")


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(port=5555, debug=True)
