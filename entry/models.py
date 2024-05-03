from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
from datetime import datetime
from entry import db, login_manager
from geoalchemy2 import Geometry
import random
import string
from datetime import datetime, timedelta

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
    current_location = db.Column(Geometry(geometry_type='POINT', srid=4326))
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
    description = db.Column(db.String(400), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    rider_id = db.Column(db.Integer, db.ForeignKey('rider.id'))
    tracking_number = db.Column(db.String(10), nullable=False,  unique=True)
    expected_arrival = db.Column(db.DateTime)
    def __init__(self, *args, **kwargs):
        super(Parcel, self).__init__(*args, **kwargs)
        self.tracking_number = self.generate_tracking_number()
        self.set_expected_arrival()

    def generate_tracking_number(self):
        # Generate a unique 7-character tracking number
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))

    def set_expected_arrival(self):
        # Set expected arrival as current time plus one day
        self.expected_arrival = datetime.now() + timedelta(days=1)

    def __repr__(self):
        return f"Parcel('{self.sender_name}', '{self.sender_email}', '{self.receiver_name}', '{self.status}')"


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Admin('{self.username}', '{self.email}')"
