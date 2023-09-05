import os

from flask import Flask, redirect, session, render_template, flash
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, User
from forms import RegisterForm, LoginForm, CSRFProtectForm
from werkzeug.exceptions import Unauthorized

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", 'postgresql:///notes_app')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

app.config['SECRET_KEY'] = "I'LL NEVER TELL!!"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)


@app.get("/")
def show_root():
    """Root route to redirect to /register"""

    return redirect("/register")

@app.route("/register", methods=["GET","POST"])
def register():
    """Register user: produce form & handle form submission."""

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        is_valid = True

        if User.query.filter(User.username == username).first():
            form.username.errors = ["Username already exists!"]
            is_valid = False

        if User.query.filter(User.email == email).first():
            form.email.errors = ["Email is already associated with a user!"]
            is_valid = False

        if is_valid:
            user = User.register(username, pwd, email, first_name, last_name)
            db.session.add(user)
            db.session.commit()

            session['username'] = username

            return redirect(f"/users/{username}")

    return render_template("register.html", form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    """Show and handle login form."""

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data

        user = User.authenticate(username, pwd)

        if user:
            session["username"] = username
            return redirect(f"/users/{username}")

        else:
            form.username.errors = ["Bad name/password"]

    return render_template("login.html", form=form)

@app.get('/users/<username>')
def show_user(username):
    """Show information about user."""

    form = CSRFProtectForm()

    if "username" not in session:
        flash("You must be logged in to view!")
        return redirect("/")

    else:
        if session["username"] == username:
            user = User.query.get_or_404(username)
            return render_template("user.html",
                                   user=user,
                                   session=session,
                                   form=form)

        else:
            raise Unauthorized()

@app.post("/logout")
def logout():
    """Logs user out and redirects to homepage. Copied from Demo."""

    form = CSRFProtectForm()

    if form.validate_on_submit():
        # Remove "user_id" if present, but no errors if it wasn't
        session.pop("username", None)

    return redirect("/")