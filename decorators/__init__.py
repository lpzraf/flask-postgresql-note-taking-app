from functools import wraps
from flask import redirect, session, url_for, flash


def ensure_authenticated(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if session.get('user_id') is None:
            flash('Please log in first!', 'negative')
            return redirect(url_for('auth.login'))
        return fn(*args, **kwargs)
    return wrapper


def prevent_login_signup(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if session.get('user_id'):
            flash('You are logged in already!', 'negative')
            return redirect(url_for('users.index'))
        return fn(*args, **kwargs)
    return wrapper


def ensure_correct_user(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # import pdb; pdb.set_trace()
        correct_id = kwargs.get('user_id')
        if correct_id != session.get('user_id'):
            flash('Not authorized!', 'negative')
            return redirect(url_for('users.index'))
        return fn(*args, **kwargs)
    return wrapper
