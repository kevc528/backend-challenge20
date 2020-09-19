import os
import json
from app import db, DB_FILE
from models import *
from webscraper import scrape_clubs

def user_signup(username, name, favorites):
    """
    Used to create a new user - signup function
    """
    new_user = User(username, name, favorites)
    db.session.add(new_user)
    db.session.commit()

# creating josh's user
def create_user():
    user_signup('josh', 'Josh', [])

def create_clubs_from_json(clubs):
    """
    Used to create a club in the database from json layout 
    similar to clubs.json
    """
    tag_map = {}
    for club in clubs:
        tag_objs = []
        for tag in club['tags']:
            if tag not in tag_map:
                tag_obj = Tag(tag)
                tag_map[tag] = tag_obj
                db.session.add(tag_obj)
                db.session.commit()
            tag_objs.append(tag_map[tag])
        db.session.add(Club(club['code'], club['name'], club['description'], tag_objs))
    db.session.commit()


def load_data():
    """
    Load json data into the database
    """
    with open('clubs.json') as fObj:
        clubs = json.load(fObj)
    create_clubs_from_json(clubs)

def load_scraped_data():
    """
    Load scraped data into the database
    """
    clubs = scrape_clubs()
    create_clubs_from_json(clubs)

# No need to modify the below code.
if __name__ == '__main__':
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    
    db.create_all()
    create_user()
    load_data()
    load_scraped_data()
