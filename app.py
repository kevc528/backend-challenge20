from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from sqlalchemy import exc

DB_FILE = "clubreview.db"

app = Flask(__name__)
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
    if req_json == None or 'code' not in req_json or 'name' not in req_json:
        return jsonify({'status':'Bad request'}), 400
    else:
        try:
            tag_objs = []
            if 'tags' in req_json:
                tag_strings = req_json['tags']
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

@app.route('/api/clubs', methods=['POST', 'GET'])
@cross_origin()
def get_club_list():
    if request.method == 'GET':
        keyword = request.args.get('search')
        return get_clubs_keyword(keyword)
    else:
        req_json = request.get_json()
        return create_new_club(req_json)

def favorite_club_post(req_json, club):
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
    club_obj = Club.query.filter_by(name=club).first()
    if club_obj == None:
        return jsonify({'status':'No such club'}), 400
    return jsonify({'favorite count': len(club_obj.favorites)}), 200

@app.route('/api/<club>/favorite', methods=['GET', 'POST'])
@cross_origin()
def favorite_club(club):
    club = club.replace("%20", " ")
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
    if 'tags' in req_json:
        if not isinstance(req_json['tags'], list):
            return jsonify({'status':'Bad request'}), 400 
        tag_objs = []
        for tag in req_json['tags']:
            tag_obj = Tag.query.filter_by(tag_name=tag).first()
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

if __name__ == '__main__':
    app.run()
