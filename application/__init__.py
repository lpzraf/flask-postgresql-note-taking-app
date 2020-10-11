from flask import (Flask, render_template, request,
                   redirect, url_for, session, g, flash)
from flask_modus import Modus
from application.users.forms import LoginForm
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from decorators import ensure_authenticated, prevent_login_signup, ensure_correct_user

from application.models import db, User, Note

app = Flask(__name__)

# Using a production configuration
# app.config.from_object('config.ProdConfig')

# Using a development configuration
app.config.from_object('config.DevConfig')


bcrypt = Bcrypt(app)

db.init_app(app)
with app.app_context():
    db.create_all()

modus = Modus(app)  # for overwriting http methods

from application.users.routes import users_bp
from application.notes.routes import notes_bp


app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(notes_bp, url_prefix='/users/<int:user_id>/notes')


# about
@app.route('/about')
def about():
    return render_template('about.html')


# session
@app.before_request
def before_request():
    if session.get('user_id'):
        g.user = User.query.get(session['user_id'])
    else:
        g.user = None


# login
@app.route('/login', methods=['GET', 'POST'])
@prevent_login_signup
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate():
            authenticated_user = User.authenticate(form.username.data, form.password.data)
            if authenticated_user:
                session['user_id'] = authenticated_user.id
                flash('You are logged in.', 'positive')
                return redirect(url_for('profile'))
            else:
                flash('Invalid credentials!', 'negative')
                return redirect(url_for('login'))
    return render_template('login.html', form=form)


# logout
@app.route('/logout')
@ensure_authenticated
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))


# profile
@app.route('/profile')
@ensure_authenticated
def profile():
    return render_template('profile.html')