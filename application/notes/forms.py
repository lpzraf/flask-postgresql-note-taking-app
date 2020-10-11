from flask_wtf import FlaskForm
from wtforms import StringField, validators


class NoteForm(FlaskForm):
    title = StringField('Title', [validators.DataRequired()])
    note_body = StringField('Note Body', [validators.DataRequired()])


class DeleteForm(FlaskForm):
    pass
