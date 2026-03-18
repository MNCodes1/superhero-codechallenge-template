from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


# ---------------- HERO ----------------
class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    super_name = db.Column(db.String, nullable=False)

    # Relationships
    hero_powers = db.relationship(
        "HeroPower",
        back_populates="hero",
        cascade="all, delete-orphan"
    )

    powers = db.relationship(
        "Power",
        secondary="hero_powers",
        back_populates="heroes"
    )

    # Prevent infinite recursion
    serialize_rules = ("-hero_powers.hero",)

    def __repr__(self):
        return f"<Hero {self.id}>"


# ---------------- POWER ----------------
class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    # Relationships
    hero_powers = db.relationship(
        "HeroPower",
        back_populates="power",
        cascade="all, delete-orphan"
    )

    heroes = db.relationship(
        "Hero",
        secondary="hero_powers",
        back_populates="powers"
    )

    # Prevent recursion but allow nested power display
    serialize_rules = ("-hero_powers.power",)

    # Validation
    @validates("description")
    def validate_description(self, key, value):
        if not value or len(value) < 20:
            raise ValueError("description must be at least 20 characters long")
        return value

    def __repr__(self):
        return f"<Power {self.id}>"


# ---------------- HERO POWER ----------------
class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    hero_id = db.Column(db.Integer, db.ForeignKey("heroes.id"))
    power_id = db.Column(db.Integer, db.ForeignKey("powers.id"))

    # Relationships
    hero = db.relationship("Hero", back_populates="hero_powers")
    power = db.relationship("Power", back_populates="hero_powers")

    # Prevent deep nesting loops
    serialize_rules = (
        "-hero.hero_powers",
        "-power.hero_powers",
    )

    # Validation
    @validates("strength")
    def validate_strength(self, key, value):
        if value not in ["Strong", "Weak", "Average"]:
            raise ValueError("strength must be Strong, Weak, or Average")
        return value

    def __repr__(self):
        return f"<HeroPower {self.id}>"