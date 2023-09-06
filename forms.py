from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, TextAreaField
from wtforms.validators import InputRequired, Email, Length


########## USER FORMS ##########

class RegisterForm(FlaskForm):
    """Form for registering a user."""

    username = StringField(
        "Username",
        validators=[InputRequired(), Length(max=20)]
    )

    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(max=100)]
    )

    email = EmailField(
        "Email",
        validators=[InputRequired(), Email(), Length(max=50)]
    )

    first_name = StringField(
        "First Name",
        validators=[InputRequired(), Length(max=30)]
    )

    last_name = StringField(
        "Last Name",
        validators=[InputRequired(), Length(max=30)]
    )


class LoginForm(FlaskForm):
    """Form for logging in a user."""

    username = StringField(
        "Username",
        validators=[InputRequired(), Length(max=20)]
    )

    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(max=100)]
    )


class CSRFProtectForm(FlaskForm):
    """Form for CSRF protection."""


########## NOTES FORMS ##########

class AddNoteForm(FlaskForm):
    """Form to add note."""

    title = StringField(
        "Title",
        validators=[InputRequired(), Length(max=100)]
    )

    content = TextAreaField(
        "Content",
        validators=[InputRequired()]
    )


class EditNoteForm(AddNoteForm):
    """Form to edit note."""
