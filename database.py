from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# =========================
# USER MODEL
# =========================
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
        index=True
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

    role = db.Column(
        db.String(50),
        default="user",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # Relationship (IMPORTANT)
    analyses = db.relationship(
        "Analysis",
        backref="user",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"<User {self.username}>"



# =========================
# PROPERTY MODEL (NEW - IMPORTANT)
# =========================
class Property(db.Model):
    __tablename__ = "properties"

    id = db.Column(db.Integer, primary_key=True)

    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Float, nullable=False)
    sqft_living = db.Column(db.Integer, nullable=False)

    grade = db.Column(db.Integer)
    condition = db.Column(db.Integer)
    yr_built = db.Column(db.Integer)

    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    year_sold = db.Column(db.Integer)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # Relationship
    analyses = db.relationship(
        "Analysis",
        backref="property",
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f"<Property {self.id}>"



# =========================
# ANALYSIS MODEL
# =========================
class Analysis(db.Model):
    __tablename__ = "analyses"

    id = db.Column(db.Integer, primary_key=True)

    # ---------- INPUTS (VERY IMPORTANT) ----------
    annual_rent = db.Column(db.Float, nullable=False)
    annual_expenses = db.Column(db.Float, nullable=False)
    annual_loan_payment = db.Column(db.Float)
    investment_years = db.Column(db.Integer, nullable=False)

    # ---------- OUTPUTS ----------
    predicted_price = db.Column(db.Float)
    roi = db.Column(db.Float)
    irr = db.Column(db.Float)

    risk_level = db.Column(db.String(50))
    recommendation = db.Column(db.String(50))

    investment_score = db.Column(db.Float)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        index=True
    )

    # ---------- FOREIGN KEYS ----------
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    property_id = db.Column(
        db.Integer,
        db.ForeignKey("properties.id"),
        nullable=False
    )

    def __repr__(self):
        return f"<Analysis {self.id} - ROI {self.roi}>"