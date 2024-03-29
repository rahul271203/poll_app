from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import StringField, EmailField, PasswordField, SubmitField,URLField
from wtforms.validators import DataRequired, Email, Length, ValidationError

class LoginForm(FlaskForm):
    email = EmailField(validators=[DataRequired(), Email()], render_kw={"placeholder": "Enter your email"})
    password = PasswordField(validators=[DataRequired()], render_kw={"placeholder": "Enter your password"})
    submit = SubmitField('login',render_kw={"class": "btn btn-primary"})

class RegisterForm(FlaskForm):
    email = EmailField( validators=[DataRequired(), Email()], render_kw={"placeholder": "Enter your email"})
    username = StringField( validators=[DataRequired()], render_kw={"placeholder": "Choose a username"})
    password = PasswordField( validators=[DataRequired(),Length(min=8)], render_kw={"placeholder": "Choose a password"})
    submit = SubmitField('register',render_kw={"class": "btn btn-success"})

class CommentForm(FlaskForm):
    head = StringField( validators=[DataRequired()], render_kw={"placeholder": "Enter heading"})
    body = CKEditorField('Body', validators=[DataRequired()])
    bg_image = URLField('Enter backgroud image URL',render_kw={"placeholder": "Enter backgroud image URL"})
    submit = SubmitField('Post poll',render_kw={"class": "btn btn-success"})
    
class DatabaseForm(FlaskForm):
    icon_link = URLField(validators=[DataRequired()], render_kw={"placeholder": "Enter valid icon link"})
    submit = SubmitField('Submit',render_kw={"class": "btn btn-primary"})