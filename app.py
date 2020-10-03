from flask import (Flask, render_template, request, abort, 
                    redirect, url_for, jsonify, session, g, flash)
from flask_modus import Modus
from forms import UserForm, NoteForm, DeleteForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_bcrypt import Bcrypt
from credentials import *
from sqlalchemy.exc import IntegrityError
from decorators import ensure_authenticated, prevent_login_signup, ensure_correct_user

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CREDENTIALS
app.secret_key = SECRET_KEY
db = SQLAlchemy(app) # comment this if using model.py
db.init_app(app)
with app.app_context():
    db.create_all()


modus = Modus(app) # for overwriting http methods

date = datetime.datetime.now().strftime('%A, %b %d, %Y')

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(120), unique=True)
    notes = db.relationship('Note', backref='user', lazy='dynamic', cascade="all,delete")

    def __init__(self,username,password):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode('UTF-8')
    
    def __repr__(self):
        return '<User %r>' % self.username
    
    @classmethod
    def authenticate(cls,username,password):
        found_user = cls.query.filter_by(username = username).first()
        if found_user:
            authenticated_user = bcrypt.check_password_hash(found_user.password, password)
            if authenticated_user:
                return found_user
        return False

class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    date = db.Column(db.DateTime)
    note_body = db.Column(db.String(280), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self,title,date,note_body, user_id):
        self.title = title
        self.date = date
        self.note_body = note_body
        self.user_id = user_id


# home
@app.route('/users')
@ensure_authenticated
def index():
    global date
    delete_form = DeleteForm()
    return render_template('users/index.html', users=User.query.all(), delete_form=delete_form, date=date)

# user signup
@app.route('/users', methods=['POST'])
@prevent_login_signup
def signup():
    form = UserForm(request.form)
    if form.validate():
        try:
            new_user = User(form.username.data, form.password.data)
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            flash('User Created!')
            return redirect(url_for('index'))
        except IntegrityError:
            return render_template('users/new.html', form=form)
        return render_template('users/new.html', form=form)

# users new
@app.route('/users/new')
@prevent_login_signup
def new():
    user_form = UserForm()
    return render_template('users/new.html', form=user_form)

# users edit
@app.route('/users/<int:id>/edit')
@ensure_authenticated
@ensure_correct_user
def edit(id):
    found_user = User.query.get(id)
    user_form = UserForm(obj=found_user)
    return render_template('users/edit.html', user=found_user, form=user_form)

# users show
@app.route('/users/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
@ensure_authenticated
@ensure_correct_user
def show(id):
    found_user = User.query.get(id)
    if request.method == b'PATCH':
        form = UserForm(request.form)
        if form.validate():
            found_user.username = request.form['username']
            found_user.password = request.form['password']
            db.session.add(found_user)
            db.session.commit()
            flash('User Updated!')
            return redirect(url_for('index'))
        return render_template('users/edit.html', user=found_user, form=form)
    if request.method == b'DELETE':
        delete_form = DeleteForm(request.form)
        if delete_form.validate():
            db.session.delete(found_user)
            db.session.commit()
            flash('User Deleted!')
        return redirect(url_for('index'))
    return render_template('users/show.html', user=found_user)

# notes index
@app.route('/users/<int:user_id>/notes', methods=['GET', 'POST'])
@ensure_correct_user
def notes_index(user_id):
    delete_form = DeleteForm()
    found_user = User.query.get(user_id)
    if request.method == 'POST':
        form = NoteForm(request.form)
        if form.validate():
            new_notes = Note(request.form['title'], datetime.datetime.now(), request.form['note_body'],user_id)
            db.session.add(new_notes)
            db.session.commit()
            return redirect(url_for('notes_index', user_id=user_id))
        else:
            return render_template('notes/new.html', form=form) 
    return render_template('notes/index.html', user=found_user, delete_form=delete_form)

# notes new
@app.route('/users/<int:user_id>/notes/new', methods=['GET', 'POST'])
def notes_new(user_id):
    note_form = NoteForm()
    return render_template('notes/new.html', user=User.query.get(user_id), form=note_form)

# notes edit
@app.route('/users/<int:user_id>/notes/<int:id>/edit')
@ensure_authenticated
def notes_edit(user_id,id):
    found_note = Note.query.get(id)
    note_form = NoteForm(obj=found_note)
    return render_template('notes/edit.html', note=found_note, form=note_form)

# notes show
@app.route('/users/<int:user_id>/notes/<int:id>',  methods=['GET', 'PATCH' ,'DELETE'])
def notes_show(user_id,id):
    found_note = Note.query.get(id)
    found_user = User.query.get(user_id)
    if request.method == b"PATCH":
        found_note.title = request.form["title"]
        found_note.note_body = request.form["note_body"]
        db.session.add(found_note)
        db.session.commit()
        return redirect(url_for('notes_index', user_id=user_id))
    if request.method == b"DELETE":
        delete_form = DeleteForm(request.form)
        if delete_form.validate():
            db.session.delete(found_note)
            db.session.commit()
        return redirect(url_for('notes_index', user_id=user_id))
    return render_template('notes/show.html', note=found_note,user=found_user)


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
                flash('You are logged in.')
                return redirect(url_for('profile'))
            else:
                flash('Invalid credentials!')
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


if __name__ == '__main__':
    app.run(debug=True)
