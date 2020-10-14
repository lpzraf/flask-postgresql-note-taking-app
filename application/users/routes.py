from flask import (render_template, request,
                   redirect, url_for, session,
                   flash, Blueprint, g)
from application.users.forms import UserForm, DeleteForm, EmptyForm
from application.models import User
from application import db, bcrypt
import datetime
from sqlalchemy.exc import IntegrityError
from decorators import (ensure_authenticated,
                        prevent_login_signup,
                        ensure_correct_user)

users_bp = Blueprint(
    'users',
    __name__,
    template_folder='templates'
)


# users
@users_bp.route('/')
@ensure_authenticated
def index():
    date = datetime.datetime.now().strftime('%A, %b %d, %Y')
    delete_form = DeleteForm()
    return render_template('users/index.html',
                           users=User.query.all(),
                           delete_form=delete_form,
                           date=date)


# user signup
@users_bp.route('/', methods=['POST'])
@prevent_login_signup
def signup():
    form = UserForm(request.form)
    if form.validate():
        try:
            new_user = User(form.username.data,
                            form.password.data,
                            datetime.datetime.now())
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            flash('User Created!', 'positive')
            return redirect(url_for('users.index'))
        except IntegrityError:
            return render_template('users/new.html', form=form)
        return render_template('users/new.html', form=form)


# users new
@users_bp.route('/new')
@prevent_login_signup
def new():
    user_form = UserForm()
    return render_template('users/new.html', form=user_form)


# users edit
@users_bp.route('/<int:user_id>/edit')
@ensure_authenticated
@ensure_correct_user
def edit(user_id):
    found_user = User.query.get(user_id)
    user_form = UserForm(obj=found_user)
    return render_template('users/edit.html', user=found_user, form=user_form)


# users show
@users_bp.route('/<int:user_id>', methods=['GET', 'PATCH', 'DELETE'])
@ensure_authenticated
def show(user_id):
    empty_form = EmptyForm()
    found_user = User.query.get(user_id)
    delete_form = DeleteForm()
    if request.method == b'PATCH':
        form = UserForm(request.form)
        if form.validate():
            found_user.username = form.username.data
            found_user.password = bcrypt.generate_password_hash(form.password.data).decode('UTF-8')
            db.session.add(found_user)
            db.session.commit()
            flash('User Updated!', 'positive')
            return redirect(url_for('users.index'))
        return render_template('users/edit.html', user=found_user, form=form)
    if request.method == b'DELETE':
        delete_form = DeleteForm(request.form)
        if delete_form.validate():
            db.session.delete(found_user)
            db.session.commit()
            session.pop('user_id')
            flash('User Deleted!', 'positive')
        return redirect(url_for('login'))
    return render_template('users/show.html',
                           user=found_user,
                           empty_form=empty_form,
                           delete_form=delete_form)


# follow and unfollow routes
@users_bp.route('/follow/<int:user_id>', methods=['POST'])
@ensure_authenticated
def follow(user_id):
    form = EmptyForm()
    curr_user_obj = g.user
    found_user = User.query.get(user_id)
    if form.validate_on_submit():
        if found_user is None:
            flash('User not found!', 'negative')
            return redirect(url_for('users.index'))
        if found_user == curr_user_obj:
            flash('You cannot follow yourself!')
            return redirect(url_for('users.show', user_id=found_user.id))
        curr_user_obj.follow(found_user)
        db.session.commit()
        flash(f'You are following {found_user.username}!', 'positive')
        return redirect(url_for('users.show', user_id=found_user.id))
    else:
        return redirect(url_for('users.index'))


@users_bp.route('/unfollow/<int:user_id>', methods=['POST'])
@ensure_authenticated
def unfollow(user_id):
    form = EmptyForm()
    found_user = User.query.get(user_id)
    curr_user_obj = g.user
    if form.validate_on_submit():
        if found_user is None:
            flash('User not found!', 'negative')
            return redirect(url_for('users.index'))
        if found_user == curr_user_obj:
            flash('You cannot unfollow yourself!', 'negative')
            return redirect(url_for('users.show', user_id=found_user.id))
        curr_user_obj.unfollow(found_user)
        db.session.commit()
        flash(f'You are not following {found_user.username}!', 'negative')
        return redirect(url_for('users.show', user_id=found_user.id))
    else:
        return redirect(url_for('users.index'))
