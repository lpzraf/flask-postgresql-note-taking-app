from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators


class UserForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])


class NoteForm(FlaskForm):
    title = StringField('Title', [validators.DataRequired()])
    note_body = StringField('Note Body', [validators.DataRequired()])


class DeleteForm(FlaskForm):
    pass


class LoginForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
