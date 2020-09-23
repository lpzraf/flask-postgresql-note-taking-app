from flask import (Flask, render_template, request, abort, 
                    redirect, url_for, jsonify,session,g, session)
from flask_modus import Modus
from model import User, Note
from forms import UserForm, NoteForm
# from model import db, save_db, user_db, save_user_db
from flask_sqlalchemy import SQLAlchemy
import datetime
import random
from credentials import *

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CREDENTIALS
db = SQLAlchemy(app)
db.init_app(app)
with app.app_context():
    db.create_all()


app.secret_key = SECRET_KEY
modus = Modus(app) # for overwriting http methods

date = datetime.datetime.now().strftime('%A, %b %d, %Y')


# root
@app.route('/')
def root():
    return redirect(url_for('index.html'))

# users home
@app.route('/users', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        new_user = User(request.form['username'], request.form['password'])
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('users/index.html', users=User.query.all())

# users new
@app.route('/users/new')
def new():
    user_form = UserForm()
    return render_template('users/new.html', form=user_form)

# users edit
@app.route('/users/<int:id>/edit')
def edit(id):
    return render_template('users/edit.html', user=User.query.get(id))

# users show
@app.route('/users/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def show(id):
    found_user = User.query.get(id)
    if request.method == b'PATCH':
        found_user.username = request.form['username']
        found_user.password = request.form['password']
        db.session.add(found_user)
        db.session.commit()
        return redirect(url_for('index'))
    if request.method == b'DELETE':
        db.session.delete(found_user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('users/show.html', user=found_user)

# notes index
@app.route('/users/<int:user_id>/notes', methods=['GET', 'POST'])
def notes_index(user_id):
    if request.method == 'POST':
        new_notes = Note(request.form['title'], datetime.datetime.now(), request.form['note_body'],user_id)
        db.session.add(new_notes)
        db.session.commit()
        return redirect(url_for('notes_index', user_id=user_id)) 
    return render_template('notes/index.html', user=User.query.get(user_id))

# notes new
@app.route('/users/<int:user_id>/notes/new', methods=['GET', 'POST'])
def notes_new(user_id):
    return render_template('notes/new.html', user=User.query.get(user_id))

# notes edit
@app.route('/users/<int:user_id>/notes/<int:id>/edit')
def notes_edit(user_id,id):
    found_note = Note.query.get(id)
    return render_template('notes/edit.html', note=found_note)

# notes delete
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
        db.session.delete(found_note)
        db.session.commit()
        return redirect(url_for('notes_index', user_id=user_id))
    return render_template('notes/show.html', note=found_note)


###### old code #####
# about
@app.route('/about')
def about():
    return render_template('about.html')

# notes homepage
@app.route('/notes')
def notes():
    global date
    if not g.user:
        return redirect(url_for('login'))
    
    return render_template('notes.html', 
                            date=date,
                            notes=db)

# adding a note
@app.route('/notes/new', methods=["GET", "POST"])
def add_note():
    global date
    if not g.user:
        return redirect(url_for('login'))

    if request.method == "POST":
        note = {"title": request.form['title'],
                "date": request.form['date'],  
                "note_body": request.form['note_body']}
        db.append(note)
        save_db()
        return redirect(url_for('view_note', index=len(db) - 1))
    else:
        return render_template("add_note.html", date=date)

# viewing a note
@app.route('/notes/<int:index>', methods=['GET', 'PATCH', 'DELETE'])
def view_note(index):
    if not g.user:
        return redirect(url_for('login'))

    try:
        note = db[index]
        # if updating a note
        if request.method == b"PATCH":
            note = {"title": request.form['title'],
                "date": request.form['date'],  
                "note_body": request.form['note_body']}
            db[index] = note
            save_db()
            return redirect(url_for('notes'))
        
        # if deleting a note
        if request.method == b"DELETE":
            del note
            save_db()
            return redirect(url_for('notes'))
        
        # if showing a note
        return render_template("note.html", 
                                note=note,
                                index=index,
                                max_index= len(db)-1)
    except IndexError:
        abort(404)

# edit a note
@app.route('/notes/<int:index>/edit')
def edit_note(index):
    if not g.user:
        return redirect(url_for('login'))

    try:
        global date
        note = db[index]
        return render_template("edit.html", 
                                note=note,
                                index=index,
                                max_index= len(db)-1,
                                date=date)
    except IndexError:
        abort(404)

# removing a note 
@app.route('/remove_note/<int:index>', methods=["GET", "POST"])
def remove_note(index):
    if not g.user:
        return redirect(url_for('login'))

    try:
        if request.method == "POST":
            del db[index]
            save_db()
            return redirect(url_for('notes'))
        else:
            return render_template('remove_note.html', note=db[index])
    except IndexError:
        abort(404)


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
