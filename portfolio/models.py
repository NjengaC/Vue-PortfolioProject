from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
from datetime import datetime
from portfolio import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def __str__(self):
        return f"User('{self.username}', '{self.email}', '{self.password}')"


class Rider(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)
    vehicle_registration = db.Column(db.String(50), unique=True, nullable=False)
    area_of_operation = db.Column(db.String(100), nullable=False)
    availability = db.Column(db.Boolean, default=True)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"Rider('{self.name}', '{self.contact_number}', '{self.vehicle_type}', '{self.area_of_operation}', '{self.availability}')"


class Parcel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_name = db.Column(db.String(100), nullable=False)
    sender_email = db.Column(db.String(100), nullable=False)
    sender_contact = db.Column(db.String(20), nullable=False)
    receiver_name = db.Column(db.String(100))
    receiver_contact = db.Column(db.String(20))
    pickup_location = db.Column(db.String(255), nullable=False)
    delivery_location = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(60))
    pickup_time = db.Column(db.TIMESTAMP)
    delivery_time = db.Column(db.TIMESTAMP)
    description = db.Column(db.String(400), nullable=False)
    parcel_weight = db.Column(db.String(60))
    status = db.Column(db.String(20), default='pending')
    def __repr__(self):
        return f"Parcel('{self.parcel_name}', '{self.sender_name}', '{self.receiver_name}', '{self.status}')"


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Admin('{self.username}', '{self.email}')"
