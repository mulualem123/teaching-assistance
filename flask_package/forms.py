from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, InputRequired

class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[InputRequired(),Length(min=4, max=25)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField ('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField ('Login')
    
class PlaylistForm(FlaskForm):
    name = StringField('Playlist Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Create Playlist')