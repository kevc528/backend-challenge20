from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from sqlalchemy import exc

DB_FILE = "clubreview.db"

app = Flask(__name__)
# needed CORS for requests to work
cors = CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_FILE}"
app.config['CORS_HEADERS'] = 'Content-Type'
db = SQLAlchemy(app)

from models import *


@app.route('/')
@cross_origin()
def main():
    return "Welcome to Penn Club Review!"

@app.route('/api')
@cross_origin()
def api():
    return jsonify({"message": "Welcome to the Penn Club Review API!."})

@app.route('/api/user/<username>', methods=['GET'])
@cross_origin()
def get_user_profile(username):
    user = User.query.filter_by(username=username).first()
    if user == None:
        return jsonify({'status':'No such user'}), 400
    return jsonify({
        'name': user.name,
        'username': user.username
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
        return jsonify({'status':'Bad request'}), 400
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
                req_json['description'] if 'description' in req_json else '', tag_objs)
            db.session.add(new_club)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            return jsonify({'status':'Duplicate fields'}), 400
        except Exception as e:
            print(e)
            jsonify({'status':'Write error'}), 400
    return jsonify({'status':'success'}), 200

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
@cross_origin()
def get_club_list():
    if request.method == 'GET':
        keyword = request.args.get('search')
        return get_clubs_keyword(keyword)
    else:
        req_json = request.get_json()
        if req_json == None:
            req_json = club_form_to_json(request.form)
        return create_new_club(req_json)

def favorite_club_post(req_json, club):
    """
    Function taking in a json request with username and 
    favoriting/unfavoriting the club for that user
    """
    if req_json == None or 'user' not in req_json:
        return jsonify({'status':'Bad request'}), 400
    username = req_json['user']
    user = User.query.filter_by(username=username).first()
    if user == None:
        return jsonify({'status':'No such user'}), 400
    club_obj = Club.query.filter_by(name=club).first()
    if club_obj == None:
        return jsonify({'status':'No such club'}), 400
    if club_obj in user.favorites:
        user.favorites.remove(club_obj)
    else:
        user.favorites.append(club_obj)
    db.session.commit()
    return jsonify({'status':'success'}), 200

def club_favorite_count(club):
    """
    Returns favorite count for specified club name
    """
    club_obj = Club.query.filter_by(name=club).first()
    if club_obj == None:
        return jsonify({'status':'No such club'}), 400
    return jsonify({'favorite count': len(club_obj.favorites)}), 200

@app.route('/api/<club>/favorite', methods=['GET', 'POST'])
@cross_origin()
def favorite_club(club):
    if request.method == 'POST':
        return favorite_club_post(request.get_json(), club)
    else:
        return club_favorite_count(club)

@app.route('/api/clubs/<code>', methods=['PATCH'])
@cross_origin()
def modify_club(code):
    club_obj = Club.query.filter_by(code=code).first()
    if club_obj == None:
        return jsonify({'status':'No such club'}), 400 
    req_json = request.get_json()
    # check which fields need to be updated
    if 'tags' in req_json:
        if not isinstance(req_json['tags'], list):
            return jsonify({'status':'Bad request'}), 400 
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
    return jsonify({'status':'success'}), 200 

@app.route('/api/tag_count', methods=['GET'])
@cross_origin()
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
    Adds comment (in json) for the club specified into the database
    """
    if req_json == None or 'user' not in req_json or 'text' not in req_json:
        return jsonify({'status':'Bad request'}), 400
    username = req_json['user']
    user = User.query.filter_by(username=username).first()
    if user == None:
        return jsonify({'status':'No such user'}), 400
    club_obj = Club.query.filter_by(name=club).first()
    if club_obj == None:
        return jsonify({'status':'No such club'}), 400
    comment_obj = Comment(user.id, club_obj.id, req_json['text'])
    club_obj.comments.append(comment_obj)
    db.session.commit()
    return jsonify({'status':'success'}), 200

def get_club_comments(club):
    """
    Gets all comments for a specified club. 
    Comment information includes author and text.
    """
    club_obj = Club.query.filter_by(name=club).first()
    if club_obj == None:
        return jsonify({'status':'No such club'}), 400
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
        req_json = request.get_json()
        return add_comment(club, req_json)
    else:
        return get_club_comments(club)

if __name__ == '__main__':
    app.run()
