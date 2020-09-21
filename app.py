from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from sqlalchemy import exc
import bcrypt

DB_FILE = "clubreview.db"

app = Flask(__name__)
# needed CORS for requests to work w/ postman
cors = CORS(app, supports_credentials=True)
app.secret_key = b'\x9f1\xa1Z\\\xbe3U\x85N\xce\xcf\xa9\x864,KR\xd3a[XJU'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_FILE}"
db = SQLAlchemy(app)

from models import *
from bootstrap import user_signup


@app.route('/')
def main():
    return "Welcome to Penn Club Review!"

@app.route('/api')
def api():
    return jsonify({"message": "Welcome to the Penn Club Review API!."})

@app.route('/api/user/<username>', methods=['GET'])
def get_user_profile(username):
    user = User.query.filter_by(username=username).first()
    if user == None:
        return jsonify({'message':'No such user'}), 400
    return jsonify({
        'name': user.name,
        'username': user.username,
        'year': user.year,
        'major': user.major
    })

def get_clubs_keyword(keyword):
    """
    Function to get json club list by keyword.
    In case of no keyword, or empty keyword, all clubs are returned. 
    When keyword is specified, SQL 'LIKE' is used to find substring 
    matches in the title.
    """
    club_list = []
    if keyword == None or keyword == '':
        clubs = Club.query.all()
    else:
        clubs = Club.query.filter(Club.name.like("%"+keyword+"%")).all()
    for club in clubs:
            club_list.append({
                'name': club.name,
                'description': club.description,
                'tags': list(map(lambda x: x.tag_name, club.tags))
            })
    return jsonify({'clubs': club_list}), 200

def create_new_club(req_json):
    """
    Function used to create a new club passed in json format
    """
    if req_json == None or 'name' not in req_json:
        return jsonify({'message':'Bad request'}), 400
    else:
        # try to generate acronym code in the case where no code is provided
        if 'code' not in req_json:
           req_json['code'] = "".join(word[0] for word in req_json['name'].split()) 
        try:
            tag_objs = []
            if 'tags' in req_json:
                tag_strings = req_json['tags']
                # need to create any non-existing tags
                for tag in tag_strings:
                    tag_obj = Tag.query.filter_by(tag_name=tag).first()
                    if tag_obj == None:
                        tag_obj = Tag(tag)
                        db.session.add(tag_obj)
                        db.session.commit()
                    tag_objs.append(tag_obj)
            new_club = Club(req_json['code'], req_json['name'], 
                req_json['description'] if 'description' in req_json else None, tag_objs)
            db.session.add(new_club)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            return jsonify({'message':'Duplicate fields'}), 400
        except Exception as e:
            print(e)
            jsonify({'message':'Write error'}), 400
    return jsonify({'message':'success'}), 200

def club_form_to_json(form):
    """
    Helper function used to convert form data into JSON
    """
    json = {}
    if 'name' in form:
        json['name'] = form['name']
    if 'description' in form:
        json['description'] = form['description']
    if 'code' in form:
        json['code'] = form['code']
    if 'tags' in form:
        json['tags'] = form.getlist('tags')
    return json

@app.route('/api/clubs', methods=['POST', 'GET'])
def get_club_list():
    if request.method == 'GET':
        keyword = request.args.get('search')
        return get_clubs_keyword(keyword)
    else:
        if 'username' not in session:
            return jsonify({'message':'Access denied, please log in'}), 401
        req_json = request.get_json()
        if req_json == None:
            req_json = club_form_to_json(request.form)
        return create_new_club(req_json)

# Before implementing sessions, I would also need to pass 
# in json request with the username and check to make sure 
# that username exists
def favorite_club_post(club):
    """
    Function taking in a club and using the session 
    user to favorite/unfavorite
    """
    username = session['username']
    user = User.query.filter_by(username=username).first()
    # NOT NEEDED ANYMORE SINCE WE HAVE SESSION
    # if user == None:
    #     return jsonify({'message':'No such user'}), 400
    club_obj = Club.query.filter_by(name=club).first()
    if club_obj == None:
        return jsonify({'message':'No such club'}), 400
    if club_obj in user.favorites:
        user.favorites.remove(club_obj)
    else:
        user.favorites.append(club_obj)
    db.session.commit()
    return jsonify({'message':'success'}), 200

def club_favorite_count(club):
    """
    Returns favorite count for specified club name
    """
    club_obj = Club.query.filter_by(name=club).first()
    if club_obj == None:
        return jsonify({'message':'No such club'}), 400
    return jsonify({'favorite count': len(club_obj.favorites)}), 200

@app.route('/api/<club>/favorite', methods=['GET', 'POST'])
def favorite_club(club):
    if request.method == 'POST':
        if 'username' not in session:
            return jsonify({'message':'Access denied, please log in'}), 401
        return favorite_club_post(club)
    else:
        return club_favorite_count(club)

@app.route('/api/clubs/<code>', methods=['PATCH'])
def modify_club(code):
    if 'username' not in session:
        return jsonify({'message':'Access denied, please log in'}), 401
    club_obj = Club.query.filter_by(code=code).first()
    if club_obj == None:
        return jsonify({'message':'No such club'}), 400 
    req_json = request.get_json()
    # check which fields need to be updated
    if 'tags' in req_json:
        if not isinstance(req_json['tags'], list):
            return jsonify({'message':'Bad request'}), 400 
        tag_objs = []
        for tag in req_json['tags']:
            tag_obj = Tag.query.filter_by(tag_name=tag).first()
            # creating any new tags
            if tag_obj == None:
                tag_obj = Tag(tag)
                db.session.add(tag_obj)
                db.session.commit()
            tag_objs.append(tag_obj)
        club_obj.tags = tag_objs
    if 'name' in req_json:
        club_obj.name = req_json['name']
    if 'code' in req_json:
        club_obj.code = req_json['code']
    if 'description' in req_json:
        club_obj.description = req_json['description']
    db.session.commit()
    return jsonify({'message':'success'}), 200 

@app.route('/api/tag_count', methods=['GET'])
def tag_count():
    counts = []
    all_tags = Tag.query.all()
    for tag in all_tags:
        obj = {
            'tag': tag.tag_name,
            'count': len(tag.clubs)
        }
        counts.append(obj)
    return jsonify(counts), 200

def add_comment(club, req_json):
    """
    Adds comment (text in json) for the club specified into the database. 
    The author will be the current signed in user
    """
    if req_json == None or 'text' not in req_json:
        return jsonify({'message':'Bad request'}), 400
    username = session['username']
    user = User.query.filter_by(username=username).first()
    # NOT NEEDED ANYMORE SINCE WE HAVE SESSION
    # if user == None:
    #     return jsonify({'message':'No such user'}), 400
    club_obj = Club.query.filter_by(name=club).first()
    if club_obj == None:
        return jsonify({'message':'No such club'}), 400
    comment_obj = Comment(user.id, club_obj.id, req_json['text'])
    club_obj.comments.append(comment_obj)
    db.session.commit()
    return jsonify({'message':'success'}), 200

def get_club_comments(club):
    """
    Gets all comments for a specified club. 
    Comment information includes author and text.
    """
    club_obj = Club.query.filter_by(name=club).first()
    if club_obj == None:
        return jsonify({'message':'No such club'}), 400
    comments = club_obj.comments
    comment_json_list = []
    for comment in comments:
        author_obj = User.query.filter_by(id=comment.user_id).first()
        comment_json_list.append({
            'author': author_obj.username,
            'text': comment.text
        })
    return jsonify(comment_json_list), 200

@app.route('/api/<club>/comment', methods=['GET', 'POST'])
def club_comments(club):
    if request.method == 'POST':
        if 'username' not in session:
            return jsonify({'message':'Access denied, please log in'}), 401
        req_json = request.get_json()
        return add_comment(club, req_json)
    else:
        return get_club_comments(club)

@app.route('/api/signup', methods=['POST'])
def create_user():
    req_json = request.get_json()
    if (req_json == None or 'username' not in req_json or 
            'password' not in req_json or 'name' not in req_json or
            'email' not in req_json):
        return jsonify({'message':'Bad request'}), 400
    username = req_json['username']
    password = req_json['password']
    name = req_json['name']
    email = req_json['email']
    year = req_json['year'] if 'year' in req_json else None
    major = req_json['major'] if 'major' in req_json else None
    try:
        user_signup(username, password, name, email, year, major)
    except exc.IntegrityError:
        return jsonify({'message':'Username already exists'}), 400
    session['username'] = username
    return jsonify({'message':'success'}), 200

@app.route('/api/login', methods=['POST'])
def login():
    req_json = request.get_json()
    print(req_json)
    if req_json == None or 'username' not in req_json or 'password' not in req_json:
        return jsonify({'message':'Bad request'}), 400
    username = req_json['username']
    password = req_json['password']
    user = User.query.filter_by(username=username).first()
    if user == None:
        return jsonify({'message':"Username doesn't exist"}), 401
    password_b = password.encode('utf-8')
    hashed = user.password
    if bcrypt.checkpw(password_b, hashed):
        session['username'] = username
        return jsonify({'message':'success'}), 200
    else:
        return jsonify({'message':'Login failed'}), 401

@app.route('/api/logout', methods=['GET'])
def logout():
    username = session.pop('username', None)
    if username != None:
        return jsonify({'message':'Logged out of ' + username}), 200
    return jsonify({'message':'success'}), 200

@app.route('/api/emails/<code>', methods=['GET'])
def mailing_list(code):
    # here we only want signed in users to access
    # don't want anyone to see student emails
    if 'username' not in session:
        return jsonify({'message':'Access denied, please log in'}), 401
    club_obj = Club.query.filter_by(code=code).first()
    if club_obj == None:
        return jsonify({'message':'No such club'}), 400
    emails = []
    for user in club_obj.favorites:
        emails.append(user.email)
    return jsonify(emails), 200

@app.route('/api/user', methods=['PATCH'])
def update_user():
    if 'username' not in session:
        return jsonify({'message':'Access denied, please log in'}), 401
    username = session['username']
    user_obj = User.query.filter_by(username=username).first()
    req_json = request.get_json()
    # check which fields need to be updated
    if 'username' in req_json:
        user_obj.username = req_json['username']
    if 'password' in req_json:
        b_password = req_json['password'].encode("utf-8")
        hashed = bcrypt.hashpw(b_password, bcrypt.gensalt())
        user_obj.password = hashed
    if 'name' in req_json:
        user_obj.name = req_json['name']
    if 'email' in req_json:
        user_obj.email = req_json['email']
    if 'year' in req_json:
        user_obj.year = req_json['year']
    if 'major' in req_json:
        user_obj.major = req_json['major']
    try:
        db.session.commit()
        # need to change the session username if it's updated
        if 'username' in req_json:
            session['username'] = req_json['username']
        return jsonify({'message':'success'}), 200
    except exc.IntegrityError:
        return jsonify({'message':'Username already exists'}), 400

@app.route('/api/clubs/<tag>', methods=['GET'])
def get_clubs_by_tag(tag):
    tag_obj = Tag.query.filter_by(tag_name=tag).first()
    if tag_obj == None:
        return jsonify({'message':'No such tag'}), 400
    club_list = []
    tagged_clubs = tag_obj.clubs
    for club in tagged_clubs:
        club_list.append({
            'name': club.name,
            'description': club.description,
            'tags': list(map(lambda x: x.tag_name, club.tags))
        })
    return jsonify({'clubs': club_list}), 200

if __name__ == '__main__':
    app.run()
