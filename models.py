from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    app.app_context().push()
    db.app = app
    db.init_app(app)


class User(db.Model):
    """User database model."""

    __tablename__ = "users"

    notes = db.relationship('Note', backref='user')

    username = db.Column(
        db.String(20),
        primary_key=True)

    password = db.Column(
        db.String(100),
        nullable=False)

    email = db.Column(
        db.String(50),
        nullable=False,
        unique=True)

    first_name = db.Column(
        db.String(30),
        nullable=False)

    last_name = db.Column(
        db.String(30),
        nullable=False)

    # start_register
    @classmethod
    def register(cls, username, pwd, email, first_name, last_name):
        """Register user w/hashed password & return user. Copied from Demo."""

        hashed = bcrypt.generate_password_hash(pwd).decode('utf8')

        # return instance of user w/username and hashed pwd
        return cls(username=username,
                   password=hashed,
                   email=email,
                   first_name=first_name,
                   last_name=last_name)

    # end_register

    # start_authenticate
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct. Copied from Demo.

        Return user if valid; else return False.
        """

        user = cls.query.filter_by(username=username).one_or_none()

        if user and bcrypt.check_password_hash(user.password, pwd):
            # return user instance
            return user
        else:
            return False
    # end_authenticate


class Note(db.Model):
    """Note database model."""

    __tablename__ = "notes"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True)

    title = db.Column(
        db.String(100),
        nullable=False)

    content = db.Column(
        db.Text,
        nullable=False)

    owner_username = db.Column(
        db.String(20),
        db.ForeignKey('users.username'),
        nullable=False)
