from app import db

# Your database models should go here.
# Check out the Flask-SQLAlchemy quickstart for some good docs!
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/

tag_relations = db.Table('tag_relations',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key=True)
)

favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key=True)
)

class Club(db.Model):
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
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(80), unique=True, nullable=False)
    clubs = db.relationship('Club', secondary=tag_relations)

    def __init__(self, tag_name):
        self.tag_name = tag_name


class User(db.Model):
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
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)

    def __init__(self, user_id, club_id, text):
        self.user_id = user_id
        self.club_id = club_id
        self.text = text
