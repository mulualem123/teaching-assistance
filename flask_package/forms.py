from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, InputRequired
from flask_security.forms import RegisterForm as BaseRegisterForm

class ExtendedRegisterForm(BaseRegisterForm):
    """
    Extends the default Flask-Security RegisterForm to include a username field.
    """
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField ('Login')
    
class PlaylistForm(FlaskForm):
    name = StringField('Playlist Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Create Playlist')