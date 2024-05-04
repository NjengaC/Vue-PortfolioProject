from flask import render_template, flash, request, redirect, url_for, jsonify
from flask_login import login_user, login_required, logout_user, current_user
import json
import stripe
from entry.forms import LoginRiderForm, RegistrationForm, LoginForm, UpdateAccountForm, RiderRegistrationForm, ParcelForm
from entry.models import User, Rider, Parcel
import secrets
from entry import app, db, bcrypt
from sqlalchemy.exc import IntegrityError
#from here is where i started modifing 
from flask import render_template, abort
from geopy.distance import geodesic
from flask_mail import Message, Mail
from geopy.geocoders import Nominatim
from flask_login import current_user
from functools import wraps
from flask_login import current_user
from entry import mail
import retrying
import geopy.exc


@app.route('/')
@app.route('/home')
def home():
    if current_user.is_authenticated:
        logout()
    return render_template('home.html', title='Home')


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

@app.route('/track_parcel')
def track_parcel():
    # Implement the functionality for sending parcels here
    return render_template('request_pickup.html')


@app.route('/view_shipping_providers')
def view_shipping_providers():
    return render_template('view_shipping_providers.html')

@app.route('/update_profile')
def update():
    return render_template('update_profile.html')

@app.route('/about')
def about():
    # Implement the functionality for sending parcels here
    return render_template('about.html')


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
            current_location=form.current_location.data,
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
                pending_assignments = Parcel.query.filter(Parcel.status == 'allocated', Parcel.rider_id==rider.id).first()
                return render_template('view_assignments.html', title='Rider\'s dashboard', user=rider, assignment=pending_assignments)
            else:
                flash('Invalid password. Please try again.', 'danger')
        else:
            flash('Rider not found. Please check your contact number.', 'danger')

    return render_template('login_rider.html', title='Rider Login', form=form)


def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('You need to log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_view


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
        #Allocate parcel to the nearest unoccupied rider
        allocation_result = allocate_parcel(parcel)
        if allocation_result['success']:
            flash('Parcel allocated to the nearest rider. Please wait for confirmation.')
            return render_template('payment.html')
        else:
            flash('Allocation in progress. Please wait for a rider to be assigned.')
            return render_template('home.html')
    return render_template('request_pickup.html', form=form)

def allocate_parcel(parcel):
    """
    Allocates a parcel delivery to a rider
    """
    pickup_location = parcel.pickup_location
    available_riders = Rider.query.filter_by(status='available').all()
    closest_rider = None
    min_distance = float('inf')

    for rider in available_riders:
        distance = calculate_distance(pickup_location, rider.current_location)
        if distance < min_distance:
            closest_rider = rider
            min_distance = distance
    if closest_rider:
        parcel.status = 'allocated'
        parcel.rider_id = closest_rider.id
        db.session.commit()
        notify_rider_new_assignment(closest_rider.email, parcel)
        return {
            'success': True,
            'rider_id': closest_rider.id,
            'rider_name': closest_rider.name,
            'vehicle_type': closest_rider.vehicle_type,
            'vehicle_registration': closest_rider.vehicle_registration,
        }
    else:
        return {'success': False, 'message': 'Allocation in progress. Please wait for a rider to be assigned.'}


@retrying.retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)
def geocode_with_retry(geolocator, location):
    """
    retrying decorator incase the nominatim encouters challenges while loading
    """
    return geolocator.geocode(location)


def calculate_distance(location1, location2):
    """
    Implements distance calculation logic
    It uses the location format: (latitude, longitude)
    """
    geolocator = Nominatim(user_agent='myapplication')
    location1 = geolocator.geocode(location1)
    location2 = geolocator.geocode(location2)
    current = location1.latitude, location1.longitude
    pickup_location = location2.latitude, location2.longitude

    distance = geodesic(pickup_location, current).kilometers
    return distance

@app.route('/update_assignment', methods=['POST'])
def update_assignment():
    data = request.json
    parcel_id = data.get('parcel_id')
    action = data.get('action')

    assignment = Parcel.query.filter_by(id=parcel_id, status='allocated').first()

    if assignment:
        if action == 'accept':
            assignment.status = 'in_progress'
            db.session.commit()
            return jsonify({'success': True})
        elif action == 'deny':
            assignment.status = 'pending'
            assignment.rider_id = None
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Invalid action'}), 400
    else:
        return jsonify({'error': 'Assignment not found or already accepted/denied'}), 404

@app.route('/track_assignment/<int:id>')
def track_assignment(id):
    assignment = Parcel.query.get(id)
    if assignment and assignment.rider_id == current_user.id:
        lifecycle_entries = ParcelLifecycle.query.filter_by(parcel_id=id).order_by(ParcelLifecycle.timestamp.desc()).all()
        return render_template('track_assignment.html', assignment=assignment, lifecycle_entries=lifecycle_entries)
    else:
        flash('Assignment not found or not assigned to you.', 'error')
        return redirect(url_for('home'))


def notify_rider_new_assignment(rider_email, parcel):
    """
    Trigger notification when assigning a parcel to a rider
    """
    msg = Message('New Delivery Assignment', recipients=[rider_email])
    msg.body = f'Hey, you have a new delivery assignment:\n\n{parcel}\n\nClick here to view and accept: http://127.0.0.1:5000/view_assignments'
    mail.send(msg)
