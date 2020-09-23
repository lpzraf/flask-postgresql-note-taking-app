from flask_wtf import FlaskForm
from wtforms import StringField, validators

class UserForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    password = StringField('Password', [validators.DataRequired()])

class NoteForm(FlaskForm):
    title = StringField('Title', [validators.DataRequired()])
    note_body = StringField('Note Body', [validators.DataRequired()])