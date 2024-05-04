from flask import render_template, flash, request, redirect, url_for, jsonify
from flask_login import login_user, login_required, logout_user, current_user
import json
import stripe
from entry.forms import LoginRiderForm, RegistrationForm, LoginForm, UpdateAccountForm, RiderRegistrationForm, ParcelForm
from entry.models import User, Rider, Parcel
import secrets
from entry import app, db, bcrypt
from sqlalchemy.exc import IntegrityError
import requests
from flask import render_template
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import random
import string
from datetime import datetime, timedelta



@app.route('/')
@app.route('/home')
def home():
    if current_user.is_authenticated:
        return render_template('home_authenticated.html', title='Home', user=current_user)
    return render_template('home.html', title='Home')

@app.route('/companies')
def view_companies():
    # Render the companies template with the list of available companies
    return jsonify(companies)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return render_template('home_authenticated.html')
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role='user')
        db.session.add(user)
        try:
            db.session.commit()
            flash('Account created', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect(url_for('register'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return render_template('home_authenticated.html', user=current_user)
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return render_template('home_authenticated.html', user=user)
        else:
            flash('Login Unsuccessful, please check you email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UpdateAccountForm()
    if request.method == 'GET':
        form.email.data = current_user.email
        form.username.data = current_user.username
    elif request.method == 'POST':
        if form.validate_on_submit():
            current_user.email = form.email.data
            current_user.username = form.username.data
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            current_user.password = hashed_password
            db.session.commit()
            flash('Your account has been updated successfully!', 'success')
            return render_template('home.html', title='Home', user=current_user)
    return render_template('edit_profile.html', title='Edit Profile', form=form, user=current_user)

@app.route('/send_parcel')
def send_parcel():
    # Implement the functionality for sending parcels here
    return render_template('track_parcel.html')

@app.route('/sendparcel')
def sendparcel():
            return render_template('sendparcel.html')

@app.route('/view_shipping_providers')
def view_shipping_providers():
    return render_template('view_shipping_providers.html')

@app.route('/update_profile')
def update():
    return render_template('home_authenticated.html')

@app.route('/about')
def about():
    # Implement the functionality for sending parcels here
    return render_template('about.html')
@app.route('/viewavailableriders')
def viewavailableriders():
        return render_template('viewavailableriders.html')

#@app.route('/requestpickup')
#def requestpickup():
   # return render_template('requestpickup.html')

@app.route('/vieworderhistory')
def vieworderhistory():
    return render_template('vieworderhistory.html')


@app.route('/register_rider', methods=['GET', 'POST'])
def register_rider():
    form = RiderRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_rider = Rider(
            name=form.name.data,
            contact_number=form.contact_number.data, 
            email=form.email.data,
            vehicle_type=form.vehicle_type.data,
            vehicle_registration=form.vehicle_registration.data,
            area_of_operation=form.area_of_operation.data,
            password=hashed_password,
            role='rider'
        )
        db.session.add(new_rider)
        try:
            db.session.commit()
            flash('Rider registration successful!', 'success')
            return redirect(url_for('login_rider'))
        except IntegrityError:
            db.session.rollback()
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect(url_for('register_rider'))
    return render_template('register_rider.html', title='Register Rider', form=form)

@app.route('/login_rider', methods=['GET', 'POST'])
def login_rider():
    form = LoginRiderForm()
    if form.validate_on_submit():
        rider = Rider.query.filter_by(contact_number=form.contact_number.data).first()
        if rider:
            if bcrypt.check_password_hash(rider.password, form.password.data):
                login_user(rider)
                flash('Rider login successful!', 'success')
                return render_template('rider_dashboard.html', title='Rider\'s dashboard', user=rider)
            else:
                flash('Invalid password. Please try again.', 'danger')
        else:
            flash('Rider not found. Please check your contact number.', 'danger')

    return render_template('login_rider.html', title='Rider Login', form=form)


@app.route('/request_pickup', methods=['GET', 'POST'])
def request_pickup():
    form = ParcelForm()
    if form.validate_on_submit():
        parcel = Parcel(
            sender_name=form.sender_name.data,
            sender_email=form.sender_email.data,
            sender_contact=form.sender_contact.data,
            receiver_name=form.receiver_name.data,
            receiver_contact=form.receiver_contact.data,
            pickup_location=form.pickup_location.data,
            delivery_location=form.delivery_location.data,
            description=form.description.data
        )
        db.session.add(parcel)
        db.session.commit()

        pickup_location = geocode_location(parcel.pickup_location)
        if pickup_location:
            available_riders = Rider.query.all()
            closest_rider = None
            min_distance = float('inf')
            for rider in available_riders:
                distance = calculate_distance(pickup_location, rider.current_location)
                if distance < min_distance:
                    closest_rider = rider
                    min_distance = distance
            if closest_rider:
                allocate_parcel_to_rider(closest_rider, parcel)
                return jsonify({'message': 'Parcel allocated to the closest rider'})
            else:
                return jsonify({'message': 'No rider found'})
        else:
            return jsonify({'message': 'Error geocoding pickup location'})

    return render_template('request_pickup.html', form=form)

def geocode_location(location):
    """
    Geocode the location string to latitude and longitude using Nominatim API
    """
    url = 'https://nominatim.openstreetmap.org/search'
    params = {
        'q': location,
        'format': 'json',
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data:
        latitude = float(data[0]['lat'])
        longitude = float(data[0]['lon'])
        return (latitude, longitude)
    else:
        return None

def calculate_distance(location1, location2):
    """
    Implements distance calculation logic
    It uses the location format: (latitude, longitude)
    """
    distance = geodesic(location1, location2).kilometers
    return distance


def allocate_parcel_to_rider(rider, parcel):
    """
    Implements parcel allocation logic
    """
    parcel.status = 'allocated'
    parcel.rider_id = rider.id
    db.session.commit()
@app.route('/track_parcel.html')
def track_parcel():
        return render_template('track_parcel.html')
from flask import render_template

@app.route('/get_quote')
def get_quote():
      # Your logic to handle getting a quote
        return render_template('quote.html')
from flask import render_template

@app.route('/box_information')
def box_information():
      # Your logic to display information about boxes
        return render_template('box_information.html')

