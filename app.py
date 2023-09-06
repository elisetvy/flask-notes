import os

from flask import Flask, redirect, session, render_template, flash
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, User, Note
from forms import RegisterForm, LoginForm, CSRFProtectForm, AddNoteForm, EditNoteForm
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


AUTH_KEY = "username"


@app.get("/")
def show_root():
    """Root route to redirect to /register"""

    return redirect("/register")


@app.route("/register", methods=["GET", "POST"])
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

            session[AUTH_KEY] = username

            flash("User created.")
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
            session[AUTH_KEY] = username
            return redirect(f"/users/{username}")

        else:
            form.username.errors = ["Bad name/password"]

    return render_template("login.html", form=form)


@app.get('/users/<username>')
def show_user(username):
    """Show information about user."""

    if AUTH_KEY not in session:
        flash("You must be logged in to view!")
        return redirect("/")

    if session[AUTH_KEY] != username:
        raise Unauthorized()

    form = CSRFProtectForm()
    user = User.query.get_or_404(username)

    return render_template("user.html",
                           user=user,
                           session=session,
                           form=form,
                           notes=user.notes)


@app.post("/logout")
def logout():
    """Logs user out and redirects to homepage. Copied from Demo."""

    form = CSRFProtectForm()

    if form.validate_on_submit():
        # Remove "username" if present, but no errors if it wasn't
        session.pop(AUTH_KEY, None)

        flash("Logged out.")
        return redirect("/")

    raise Unauthorized()


@app.post("/users/<username>/delete")
def delete_user_and_notes(username):
    """Deletes user and user's notes from database."""

    if session[AUTH_KEY] == username:
        user = User.query.get_or_404(username)
        notes = user.notes

        for note in notes:
            db.session.delete(note)

        db.session.delete(user)
        db.session.commit()

        session.pop(AUTH_KEY, None)

        flash("User deleted.")
        return redirect("/")

    raise Unauthorized()


@app.route("/users/<username>/notes/add", methods=["GET", "POST"])
def add_note(username):
    """Display and handle note form; add note to database."""

    if AUTH_KEY not in session or session[AUTH_KEY] != username:
        raise Unauthorized()

    form = AddNoteForm()
    user = User.query.get_or_404(username)

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        note = Note(title=title, content=content, owner_username=username)
        db.session.add(note)
        db.session.commit()

        flash("Note added!")
        return redirect(f"/users/{username}")

    return render_template("add_note.html", form=form, user=user)


@app.route("/notes/<int:note_id>/update", methods=["GET", "POST"])
def update_note(note_id):
    """Display and handle note form."""

    note = Note.query.get_or_404(note_id)

    if AUTH_KEY not in session or session[AUTH_KEY] != note.owner_username:
        raise Unauthorized()

    form = EditNoteForm(obj=note)

    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data

        db.session.commit()

        flash("Note updated!")
        return redirect(f"/users/{note.owner_username}")

    return render_template("edit_note.html", form=form, note=note)


@app.post("/notes/<int:note_id>/delete")
def delete_note(note_id):
    """Deletes note and redirects to /users/<username>."""

    note = Note.query.get_or_404(note_id)

    if AUTH_KEY not in session or session[AUTH_KEY] != note.owner_username:
        raise Unauthorized()

    form = CSRFProtectForm()

    if form.validate_on_submit():
        db.session.delete(note)
        db.session.commit()

        flash("Note deleted!")
        return redirect(f"/users/{note.owner_username}")
    else:
        raise Unauthorized()