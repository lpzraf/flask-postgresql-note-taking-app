from flask import (Flask, render_template, request, abort, 
                    redirect, url_for, jsonify,session,g, session)
from flask_modus import Modus
# from model import User, Note, db
from forms import UserForm, NoteForm, DeleteForm
# from model import db, save_db, user_db, save_user_db
from flask_sqlalchemy import SQLAlchemy
import datetime
import random
from credentials import *

app = Flask(__name__)
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
    password = db.Column(db.String(20), unique=True)
    notes = db.relationship('Note', backref='user', lazy='dynamic', cascade="all,delete")

    def __init__(self,username,password):
        self.username = username
        self.password = password
    
    def __repr__(self):
        return '<User %r>' % self.username

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



# root
@app.route('/')
def root():
    return redirect(url_for('index.html'))

# users home
@app.route('/users', methods=['GET', 'POST'])
def index():
    delete_form = DeleteForm()
    if request.method == 'POST':
        form = UserForm(request.form)
        if form.validate():
            new_user = User(request.form['username'], request.form['password'])
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('index'))
        else:
            return render_template('users/new.html', form=form)
    return render_template('users/index.html', users=User.query.all(), delete_form=delete_form)

# users new
@app.route('/users/new')
def new():
    user_form = UserForm()
    return render_template('users/new.html', form=user_form)

# users edit
@app.route('/users/<int:id>/edit')
def edit(id):
    found_user = User.query.get(id)
    user_form = UserForm(obj=found_user)
    return render_template('users/edit.html', user=found_user, form=user_form)

# users show
@app.route('/users/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def show(id):
    found_user = User.query.get(id)
    if request.method == b'PATCH':
        form = UserForm(request.form)
        if form.validate():
            found_user.username = request.form['username']
            found_user.password = request.form['password']
            db.session.add(found_user)
            db.session.commit()
            return redirect(url_for('index'))
        return render_template('users/edit.html', user=found_user, form=form)
    if request.method == b'DELETE':
        delete_form = DeleteForm(request.form)
        if delete_form.validate():
            db.session.delete(found_user)
            db.session.commit()
        return redirect(url_for('index'))
    return render_template('users/show.html', user=found_user)

# notes index
@app.route('/users/<int:user_id>/notes', methods=['GET', 'POST'])
def notes_index(user_id):
    delete_form = DeleteForm()
    if request.method == 'POST':
        form = NoteForm(request.form)
        if form.validate():
            new_notes = Note(request.form['title'], datetime.datetime.now(), request.form['note_body'],user_id)
            db.session.add(new_notes)
            db.session.commit()
            return redirect(url_for('notes_index', user_id=user_id))
        else:
            return render_template('notes/new.html', form=form) 
    return render_template('notes/index.html', user=User.query.get(user_id), delete_form=delete_form)

# notes new
@app.route('/users/<int:user_id>/notes/new', methods=['GET', 'POST'])
def notes_new(user_id):
    note_form = NoteForm()
    return render_template('notes/new.html', user=User.query.get(user_id), form=note_form)

# notes edit
@app.route('/users/<int:user_id>/notes/<int:id>/edit')
def notes_edit(user_id,id):
    found_note = Note.query.get(id)
    note_form = NoteForm(obj=found_note)
    return render_template('notes/edit.html', note=found_note, form=note_form)

# notes show
@app.route('/users/<int:user_id>/notes/<int:id>',  methods=['GET', 'PATCH' ,'DELETE'])
def notes_show(user_id,id):
    found_note = Note.query.get(id)
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
    return render_template('notes/show.html', note=found_note,user=User.query.get(user_id))


###### old code #####
# about
@app.route('/about')
def about():
    return render_template('about.html')



# session
@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        global user_db
        user = [x for x in user_db if x['id'] == session['user_id']][0]
        g.user = user


# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']

        user = [x for x in user_db if x['username'] == username][0]
        if user and user['password'] == password:
            session['user_id'] = user['id']
            return redirect(url_for('profile'))

        return redirect(url_for('login'))

    return render_template('login.html')


# logout
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    global date
    if request.method == 'POST':
        session.pop('user_id', None)
        return redirect(url_for('login'))
    else:
        return render_template('logout.html', date=date)


# profile
@app.route('/profile')
def profile():
    if not g.user:
        return redirect(url_for('login'))

    return render_template('profile.html')


# creating a user
@app.route('/users/new', methods=["GET", "POST"])
def add_user():
    global date
    if request.method == "POST":
        user = {"id": random.randint(0,10000),
                "username": request.form['username'],  
                "password": request.form['password']}
        session['user_id'] = user['id']
        user_db.append(user)
        save_user_db()
        return redirect(url_for("profile"))
    
    return render_template("add_user.html", date=date)


#protected
@app.route('/protected')
def protected():
    if g.user:
        return render_template('protected.html')
    return redirect(url_for('login'))


# drop session
@app.route('/dropsession')
def dropsession():
    session.pop('user_id', None)
    return 'Dropped!'

if __name__ == '__main__':
    app.run(debug=True)
