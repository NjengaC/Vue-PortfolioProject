from flask import render_template, flash, request, redirect, url_for, jsonify
from flask_login import login_user, login_required, logout_user, current_user
import json
import stripe
from entry.forms import LoginRiderForm, RegistrationForm, LoginForm, UpdateAccountForm, RiderRegistrationForm, ParcelForm, UpdateRiderForm, ForgotPasswordForm, ResetPasswordForm
from entry.models import User, Rider, Parcel, FAQ
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
import secrets
import psycopg2
from sqlalchemy import or_

@app.route('/')
@app.route('/home')
def home():
    if current_user.is_authenticated and current_user.role == 'user':
        return redirect(url_for('home_authenticated'))
    elif current_user.is_authenticated and current_user.role == 'rider':
        return redirect(url_for('rider_authenticated'))

    return render_template('home.html', title='Home')

@app.route('/home_authenticated')
def home_authenticated():
    return render_template('home_authenticated.html', title='Vue-User\'s HomePage', user=current_user)

@app.route('/rider_authenticated')
def rider_authenticated():
    return render_template('rider_authenticated.html', title='Vue-Rider\'s HomePage', user=current_user)


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
            welcome_msg = render_template('welcome_user_mail.html', user=user, login_url=url_for('login', _external=True))
            msg= Message('Welcome to Vue!', recipients=[user.email])
            msg.html = welcome_msg
            mail.send(msg)

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
    if current_user.is_authenticated:
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


@app.route('/edit__rider_profile', methods=['GET', 'POST'])
def edit_rider_profile():
    if current_user.is_authenticated:
        form = UpdateRiderForm()
        if request.method == 'GET':
            form.email.data = current_user.email
        form.name.data = current_user.name
        form.current_location.data = current_user.current_location
        form.area_of_operation.data = current_user.area_of_operation
        form.vehicle_registration.data = current_user.vehicle_registration
        form.vehicle_type.data = current_user.vehicle_type
        form.contact_number.data = current_user.contact_number
    elif request.method == 'POST':
        if form.validate_on_submit():
            current_user.email = form.email.data
            current_user.username = form.name.data
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            current_user.password = hashed_password
            current_user.contact_number = form.contact_number.data
            current_user.vehicle_type = form.vehicle_type.data
            current_user.vehicle_registration = form.vehicle_registration.data
            current_user.area_of_operation = form.area_of_operation.data
            current_user.current_location = form.current_location.data

            db.session.commit()
            flash('Your account has been updated successfully!', 'success')
            return redirect(url_for('login_rider'))
        return render_template('edit_rider_profile.html', title='Edit Profile', form=form, user=current_user)
    else:
        flash('please login to view this page!', 'danger')
        return redirect(url_for('login'))

@app.route('/track_parcel')
def track_parcel():
    # Implement the functionality for sending parcels here
    return render_template('track_parcel.html')

@app.route('/get_parcel_status')
def get_parcel_status():
    tracking_number = request.args.get('tracking_number')
    if tracking_number:
        parcel = Parcel.query.filter_by(tracking_number=tracking_number).first()
        if parcel:
            return jsonify({
                'status': parcel.status,
                'expected_arrival': parcel.expected_arrival
            }), 200
        else:
            return jsonify({'error': 'Parcel not found'}), 404
    else:
        return jsonify({'error': 'Tracking number not provided'}), 400

@app.route('/view_shipping_providers')
def view_shipping_providers():
    return render_template('view_shipping_providers.html')


@app.route('/about')
def about():
    # Implement the functionality for sending parcels here
    return render_template('about.html')

@app.route('/contacts')
def contacts():
    return render_template('contact.html')


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
            welcome_msg = render_template('welcome_rider_mail.html', rider=new_rider, login_url=url_for('login_rider', _external=True))
            msg= Message('Welcome to Vue!', recipients=[new_rider.email])
            msg.html = welcome_msg
            mail.send(msg)

            flash('Rider registration successful!', 'success')
            return redirect(url_for('login_rider'))
        except IntegrityError:
            db.session.rollback()
            flash('User with details provided already exists. Please check Name, contact or Vehicle Registration', 'danger')
            return render_template('register_rider.html', title='Register Rider', form=form)
    return render_template('register_rider.html', title='Register Rider', form=form)

@app.route('/login_rider', methods=['GET', 'POST'])
def login_rider():
    if current_user.is_authenticated and current_user.role == 'rider':
        rider = Rider.query.filter_by(contact_number=current_user.contact_number).first()
        pending_assignments=Parcel.query.filter_by(rider_id=current_user.id).filter(Parcel.status.in_(['allocated', 'shipped', 'in_progress'])).first()
        return render_template('rider_authenticated.html', title='Rider\'s dashboard', user=current_user, assignment=pending_assignments)
    form = LoginRiderForm()
    if form.validate_on_submit():
        rider = Rider.query.filter_by(contact_number=form.contact_number.data).first()
        if rider:
            if bcrypt.check_password_hash(rider.password, form.password.data):
                login_user(rider)
                pending_assignments=Parcel.query.filter_by(rider_id=rider.id).filter(Parcel.status.in_(['allocated', 'shipped', 'in_progress'])).first()
                flash('Rider login successful!', 'success')
                return render_template('rider_authenticated.html', title='Rider\'s dashboard', user=rider, assignment=pending_assignments)
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
        allocation_result = allocate_parcel()
        if allocation_result['success']:
            send_rider_details_email(parcel.sender_email, allocation_result, parcel.tracking_number)
            flash(f'Rider Allocated. Check your email for more details')
#            return render_template('payment.html', results=allocation_result                    )
            return redirect(url_for('verify_payment'))
        else:
            flash('Allocation in progress. Please wait for a rider to be assigned', 'success')
            return redirect(url_for('verify_payment'))
#            return render_template('payment.html', result = allocation_result)
    return render_template('request_pickup.html', form=form)


def allocate_parcel():
    """
    Allocates pending parcel deliveries to available riders
    """
    pending_parcels = Parcel.query.filter_by(status='pending').all()
    available_riders = Rider.query.filter_by(status='available').all()
    allocated_parcels = []

    for parcel in pending_parcels:
        if not available_riders:
            break  # Break if no available riders left

        pickup_location = parcel.pickup_location
        closest_rider = None
        min_distance = float('inf')

        available_riders_excluding_denied = [rider for rider in available_riders if rider.id != parcel.rider_id]

        for rider in available_riders_excluding_denied:
            distance = calculate_distance(pickup_location, rider.current_location)
            if distance < min_distance:
                closest_rider = rider
                min_distance = distance

        if closest_rider:
            parcel.status = 'allocated'
            parcel.rider_id = closest_rider.id
            closest_rider.status = 'unavailable'
            db.session.commit()
            notify_rider_new_assignment(closest_rider.email, parcel, closest_rider)
            allocated_parcels.append(parcel)
            closest_rider_details = {
                    'id': closest_rider.id,
                    'name': closest_rider.name,
                    'contact': closest_rider.contact_number,
                    'vehicle_type': closest_rider.vehicle_type,
                    'vehicle_registration': closest_rider.vehicle_registration
                    }

            if allocated_parcels:
                result = {
                        'success': True,
                        'allocated_parcels': allocated_parcels,
                        'closest_rider': closest_rider_details
                        }
    else:
        result = {
                'success': False,
                'message': 'No available riders, parcel allocation pending'
                }

        return result


@app.route('/toggle_rider_status/<int:rider_id>', methods=['POST'])
def toggle_rider_status(rider_id):
    """
    Toggles the status of the rider between available and unavailable
    """
    rider = Rider.query.filter_by(id=rider_id).first()
    if rider:
        rider.status = 'unavailable' if rider.status == 'available' else 'available'
        db.session.commit()
        return jsonify({'status': rider.status})
    return jsonify({'error': 'Rider not found'}), 404


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
    user_agent = 'MyGeocodingApp/1.0 (victorcyrus01@gmail.com)'
    geolocator = Nominatim(user_agent=user_agent)
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

    assignment = Parcel.query.filter_by(id=parcel_id).filter(or_(Parcel.status == 'allocated', Parcel.status == 'shipped', Parcel.status == 'in_progress')).first()
    if assignment:
        if action == 'accept':
            assignment.status = 'in_progress'
            db.session.commit()
            flash("You have accepted parcel pick-up! We are waiting", 'success')
            return jsonify({'success': True})
        elif action == 'reject':
            rider = Rider.query.filter_by(id=assignment.rider_id).first()
            if rider:
                rider.status = 'available'
            assignment.status = 'pending'
            assignment.rider_id = None
            db.session.commit()
            flash("You have Rejected parcel pickup!, contact admin if that was unintentional", 'danger')
            allocate_parcel()
        elif action == 'shipped':
            assignment.status = 'shipped'
            db.session.commit()
            return jsonify({'success': True})
        elif action == 'arrived':
            assignment.status = 'arrived'
            rider = Rider.query.filter_by(id=assignment.rider_id).first()
            if rider:
                rider.status = 'available'
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Invalid action'}), 400
    else:
        return jsonify({'error': 'Assignment not found or already accepted/denied'}), 404
    return redirect(url_for('home'))


@app.route('/track_assignment/<int:id>')
def track_assignment(id):
    assignment = Parcel.query.get(id)
    if assignment and assignment.rider_id == current_user.id:
        lifecycle_entries = ParcelLifecycle.query.filter_by(parcel_id=id).order_by(ParcelLifecycle.timestamp.desc()).all()
        return render_template('track_assignment.html', assignment=assignment, lifecycle_entries=lifecycle_entries)
    else:
        flash('Assignment not found or not assigned to you.', 'error')
        return redirect(url_for('home'))

def notify_rider_new_assignment(rider_email, parcel, rider):
    """
    Trigger notification when assigning a parcel to a rider
    """
    msg = Message('New Delivery Assignment', recipients=[rider_email])
    html_content = render_template('new_assignment_email.html', parcel=parcel, rider=rider)
    msg.html = html_content
    mail.send(msg)

def send_rider_details_email(recipient_email, allocation_result, tracking_number):
    msg = Message('Parcel Allocation Details', recipients=[recipient_email])
    html_content = render_template('rider_details_email.html', **allocation_result, tracking_number=tracking_number)
    msg.html = html_content
    mail.send(msg)



from flask import redirect, url_for

@app.route('/support', methods=['GET', 'POST'])
def support():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        comment = request.form.get('comment')

        if not name or not email or not comment:
            flash('Please fill out all fields.', 'error')
        else:
            # Create a Message object for sending email to admin
            msg = Message(subject='User Comment', recipients=['victorcyrus01@gmail.com'])
            msg.body = f"Name: {name}\nEmail: {email}\nComment: {comment}"

            try:
                # Send the email to admin
                mail.send(msg)
                flash('Email sent successfully! Our support team will get back to you shortly', 'success')
            except Exception as e:
                flash('Something unexpected happened! Please try again', 'error')

        # Redirect to the support page after processing the form data
        return redirect(url_for('support'))

    if request.method == 'GET':
        search_query = request.args.get('search_query', '').strip()

        if search_query:
            search_words = search_query.split()

            filter_conditions = []

            for word in search_words:
                question_condition = FAQ.question.ilike(f'%{word}%')
                answer_condition = FAQ.answer.ilike(f'%{word}%')

                filter_conditions.append(question_condition)
                filter_conditions.append(answer_condition)

            combined_condition = or_(*filter_conditions)

            existing_faqs = FAQ.query.filter(combined_condition).all()

            faqs_dict = [{'question': faq.question, 'answer': faq.answer} for faq in existing_faqs]
            existing_faqs = jsonify(faqs_dict)
            return existing_faqs  # Return JSON response for search query

    return render_template('support.html')


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        rider = Rider.query.filter_by(email=email).first()
        if user:
            # Generate a unique token for the user
            token = secrets.token_urlsafe(32)
            user.reset_password_token = token
            db.session.commit()

            # Send password reset email
            reset_url = url_for('reset_password', token=token, _external=True)
            message = f"Click the link to reset your password: {reset_url}"
            send_email(user.email, "Password Reset Request", message)

            flash("Instructions to reset your password have been sent to your email.", 'success')
            return redirect(url_for('login'))
        elif rider:
            # Generate a unique token for the rider
            token = secrets.token_urlsafe(32)
            rider.reset_password_token = token
            db.session.commit()

            # Send password reset email
            reset_url = url_for('reset_password', token=token, _external=True)
            message = f"Click the link to reset your password: {reset_url}"
            send_email(rider.email, "Password Reset Request", message)

            flash("Instructions to reset your password have been sent to your email.")
            return redirect(url_for('login'))
        else:
            flash("Email address not found.", 'danger')
    return render_template('forgot_password.html', form=form)



@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Check if the token exists for a user
    user = User.query.filter_by(reset_password_token=token).first()
    if user:
        form = ResetPasswordForm()
        if form.validate_on_submit():
            # Update the user's password
            new_password = form.password.data
            user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')

            # Clear the reset_password_token
            user.reset_password_token = None
            db.session.commit()

            flash("Your password has been successfully reset. You can now log in with your new password.", 'success')
            return redirect(url_for('login'))
        return render_template('reset_password.html', form=form)

    # If the token doesn't exist for a user, check if it exists for a rider
    rider = Rider.query.filter_by(reset_password_token=token).first()
    if rider:
        form = ResetPasswordForm()
        if form.validate_on_submit():
            # Update the rider's password
            new_password = form.password.data
            rider.password = bcrypt.generate_password_hash(new_password).decode('utf-8')

            # Clear the reset_password_token
            rider.reset_password_token = None
            db.session.commit()

            flash("Your password has been successfully reset. You can now log in with your new password.", 'success')
            return redirect(url_for('login_rider'))
        return render_template('reset_password.html', form=form)

    # If the token is invalid or expired for both user and rider
    flash("Invalid or expired token.", 'danger')
    return redirect(url_for('forgot_password'))


def send_email(recipient, subject, html_body):
    msg = Message(subject, recipients=[recipient])
    msg.html = html_body
    mail.send(msg)


@app.route('/payment_success', methods=['POST'])
def payment_success():
    return redirect(url_for('home'))


@app.route('/verify_payment', methods=['GET', 'POST'])
def verify_payment():
    # Extract the token from the request data
    # stripe_token = request.form.get('stripeToken')

    # Here you would perform the necessary steps to verify the payment using the token
    # For demonstration purposes, let's assume the payment is verified successfully
    payment_verified = True

    if payment_verified:
        send_payment_notification_email()
        return redirect(url_for('home'))

    else:
        return redirect(url_for('home'))

# Function to send email notification to admin
def send_payment_notification_email():
    msg = Message('New Payment Received', recipients=['victorcyrus01@gmai.com'])
    msg.body = 'A new payment has been received. Please check the dashboard for details.'
    mail.send(msg)

    # Optionally, you can also render a template for the email content
    # msg.html = render_template('payment_notification.html', amount=...)

@app.route('/view_parcel_history', methods=['GET', 'POST'])
def view_parcel_history():
    if current_user.is_authenticated:
        parcels = Parcel.query.filter_by(sender_email=current_user.email).all()

        # Separate parcels by status
        allocated_parcels = [parcel for parcel in parcels if parcel.status == 'allocated']
        in_progress_parcels = [parcel for parcel in parcels if parcel.status == 'in_progress']
        shipped_parcels = [parcel for parcel in parcels if parcel.status == 'shipped']
        arrived_parcels = [parcel for parcel in parcels if parcel.status == 'arrived']

        return render_template('view_parcel_history.html', 
                               allocated_parcels=allocated_parcels,
                               in_progress_parcels=in_progress_parcels,
                               shipped_parcels=shipped_parcels,
                               arrived_parcels=arrived_parcels)
        return render_template('view_parcel_history.html', parcels=parcels)
    else:
        return render_template('view_parcel_history.html')
        flash('Log in to view your parcels history!', 'danger')

@app.route('/view_rider_history', methods=['GET', 'POST'])
def view_rider_history():
    if current_user.is_authenticated:
        # Query parcels for the current rider
        parcels = Parcel.query.filter_by(rider_id=current_user.id).all()

        # Separate parcels by status
        open_orders = [parcel for parcel in parcels if parcel.status in ['in_progress', 'shipped']]
        closed_orders = [parcel for parcel in parcels if parcel.status == 'arrived']

        return render_template('view_rider_history.html',
                               open_orders=open_orders,
                               closed_orders=closed_orders)
    else:
        flash('Log in to view your parcels history!', 'danger')
        return render_template('login.html')


@app.route('/rider_dashboard', methods=['GET', 'POST'])
def rider_dashboard():
    pending_assignments = Parcel.query.filter(Parcel.status == 'allocated', Parcel.rider_id==rider.id).first()
    return render_template('rider_dashboard.html', rider=current_user)
