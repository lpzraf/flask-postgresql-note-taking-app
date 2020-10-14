
from flask import (render_template, request,
                   redirect, url_for, session, g, flash, Blueprint)
# from flask_modus import Modus
from application.users.forms import LoginForm
# from flask_bcrypt import Bcrypt
from decorators import ensure_authenticated, prevent_login_signup
# from application.models import db, User
from application.models import User
from app import app


auth_bp = Blueprint(
    'auth',
    __name__,
    template_folder='templates'
)


# about
@auth_bp.route('/about')
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
@auth_bp.route('/login', methods=['GET', 'POST'])
@prevent_login_signup
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate():
            authenticated_user = User.authenticate(
                form.username.data,
                form.password.data)
            if authenticated_user:
                session['user_id'] = authenticated_user.id
                flash('You are logged in.', 'positive')
                return redirect(url_for('users.show', user_id=authenticated_user.id))
            else:
                flash('Invalid credentials!', 'negative')
                return redirect(url_for('auth.login'))
    return render_template('login.html', form=form)


# logout
@auth_bp.route('/logout')
@ensure_authenticated
def logout():
    session.pop('user_id')
    return redirect(url_for('auth.login'))
