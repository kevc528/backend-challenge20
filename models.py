from app import db

# Your database models should go here.
# Check out the Flask-SQLAlchemy quickstart for some good docs!
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/

"""
Table for Tag and Club Relationships through id
"""
tag_relations = db.Table('tag_relations',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key=True)
)

"""
Table for the User and Club relationship for favoriting clubs
"""
favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key=True)
)

class Club(db.Model):
    """
    Model for a club

    Columns: id (auto-incremented), code, name, description, tags
    Relationships: favorites (w/ Club), comments (w/ Comment)
    """
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    tags = db.relationship('Tag', secondary=tag_relations)
    favorites = db.relationship('User', secondary=favorites)
    comments = db.relationship('Comment', backref='comments')

    def __init__(self, code, name, description, tags):
        self.code = code
        self.name = name
        self.description = description
        self.tags = tags

class Tag(db.Model):
    """
    Model for a tag

    Columns: id (auto-incremented), tag_name
    Relationships: clubs (Club w/ the tag)
    """
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(80), unique=True, nullable=False)
    clubs = db.relationship('Club', secondary=tag_relations)

    def __init__(self, tag_name):
        self.tag_name = tag_name


class User(db.Model):
    """
    Model for a user

    Columns: id (auto-incremented), username, name
    Relationships: favorites (Club that user likes), comments (Comment by user)
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), unique=True, nullable=False)
    favorites = db.relationship('Club', secondary=favorites)
    comments = db.relationship('Comment', backref='club_comments')

    def __init__(self, username, name, favorites):
        self.username = username
        self.name = name
        self.favorites = favorites

class Comment(db.Model):
    """
    Model for a comment

    Columns: id (auto-incremented), user_id (of author), club_id, text
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)

    def __init__(self, user_id, club_id, text):
        self.user_id = user_id
        self.club_id = club_id
        self.text = text
