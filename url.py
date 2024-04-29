from flask import url_for
from entry import app
from entry.routes import login_required, rider_required

# URLs that require login
login_required_urls = [
    'edit_profile',
    'request_pickup',
    'my_parcels',
]

# URLs that require rider role
rider_required_urls = [
    'view_assignments',
    'edit_profile_rider',
    'track_assignment',
]

@app.route('/')
def home():
    return url_for('home')

@app.route('/login')
def login():
    return url_for('login')

# Define other routes...

def add_login_required_urls():
    for url in login_required_urls:
        app.view_functions[url].decorators = [login_required]

def add_rider_required_urls():
    for url in rider_required_urls:
        app.view_functions[url].decorators.append(rider_required)

add_login_required_urls()
add_rider_required_urls()

