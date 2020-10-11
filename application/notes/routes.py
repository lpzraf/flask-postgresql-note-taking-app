
from flask import (render_template, request,
                   redirect, url_for, Blueprint)
from application.notes.forms import NoteForm, DeleteForm
from application.models import User, Note
from application import db
import datetime
from decorators import ensure_authenticated, ensure_correct_user

notes_bp = Blueprint(
    'notes',
    __name__,
    template_folder='templates'
)


# notes index
@notes_bp.route('/', methods=['GET', 'POST'])
@ensure_authenticated
def index(user_id):
    date = datetime.datetime.now().strftime('%A, %b %d, %Y')
    delete_form = DeleteForm()
    found_user = User.query.get(user_id)
    if request.method == 'POST':
        form = NoteForm(request.form)
        if form.validate():
            new_notes = Note(request.form['title'], datetime.datetime.now(),
                             request.form['note_body'], user_id)
            db.session.add(new_notes)
            db.session.commit()
            return redirect(url_for('notes.index', user_id=user_id))
        else:
            return render_template('notes/new.html', form=form)
    return render_template('notes/index.html', user=found_user,
                           delete_form=delete_form, date=date)


# notes new
@notes_bp.route('/new', methods=['GET', 'POST'])
@ensure_authenticated
@ensure_correct_user
def new(user_id):
    found_user = User.query.get(user_id)
    note_form = NoteForm()
    return render_template('notes/new.html', user=found_user, form=note_form)


# notes edit
@notes_bp.route('/<int:id>/edit')
@ensure_authenticated
@ensure_correct_user
def edit(user_id, id):
    found_note = Note.query.get(id)
    note_form = NoteForm(obj=found_note)
    return render_template('notes/edit.html', note=found_note, form=note_form)


# notes show
@notes_bp.route('/<int:id>',  methods=['GET', 'PATCH', 'DELETE'])
@ensure_authenticated
@ensure_correct_user
def show(user_id, id):
    found_note = Note.query.get(id)
    found_user = User.query.get(user_id)
    if request.method == b"PATCH":
        found_note.title = request.form["title"]
        found_note.note_body = request.form["note_body"]
        db.session.add(found_note)
        db.session.commit()
        return redirect(url_for('notes.index', user_id=user_id))
    if request.method == b"DELETE":
        delete_form = DeleteForm(request.form)
        if delete_form.validate():
            db.session.delete(found_note)
            db.session.commit()
        return redirect(url_for('notes.index', user_id=user_id))
    return render_template('notes/show.html', note=found_note, user=found_user)
