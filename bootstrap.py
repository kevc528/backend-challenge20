import os
import json
from app import db, DB_FILE
from models import *

def user_signup(username, name):
    new_user = User(username, name)
    db.session.add(new_user)
    db.session.commit()


def create_user():
    user_signup('josh', 'Josh')


def load_data():
    print('hello')

# No need to modify the below code.
if __name__ == '__main__':
    load_data()
