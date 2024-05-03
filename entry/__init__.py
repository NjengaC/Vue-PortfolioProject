from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
""" My changes start here"""
from flask_mail import Mail
from flask_wtf import CSRFProtect

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:new_password@localhost/vue'
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'yvonnegichovi@gmail.com'
app.config['MAIL_PASSWORD'] = 'qflepxivndrhyaxh'
app.config['MAIL_DEFAULT_SENDER'] = 'yvonnegichovi@gmail.com'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost/vue'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

mail = Mail(app)
csrf = CSRFProtect(app)

from entry import routes
