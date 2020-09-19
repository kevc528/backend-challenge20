# Penn Labs Backend Challenge

## Documentation

### Models
#### Relationships
Relationships were useful to have because many tables can be 
related. For example, clubs and tags are related because clubs 
can have tags describing them. And users and clubs are related 
because users can favorite clubs.

```
tag_relations = db.Table('tag_relations',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key=True)
)
```
The first relation that I defined was the club and tag relation. 
This is a many to many relationship as clubs can have many tags 
and a tag can be part of many clubs.

```
favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key=True)
)
```
The second relation I defined was favorites, which links users to 
their favorited clubs. This is similar to the club and tag 
relationship above.

#### Models
```
class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    tags = db.relationship('Tag', secondary=tag_relations)
    favorites = db.relationship('User', secondary=favorites)
```
For the Club model, I made the primary key the id. I wasn't sure 
if the club's code could change or not - maybe a user changes the 
club name and wants to then change the club code as well, or if 
the code gets leaked. But, if the club code is guaranteed to 
never change, then it could be the primary key too.

```
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(80), unique=True, nullable=False)
    clubs = db.relationship('Club', secondary=tag_relations)
```
Same concept here... if the tag name never changes then I 
could've made that the primary key. But to be safe, I made the 
id a primary key in case a Locust Labs member wanted to change 
the capitalization or something about a tag name.

Clubs and tags both store information about their relationship 
defined above. This makes it easy to find tags for a club, and 
clubs for a tag.

```
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), unique=True, nullable=False)
    favorites = db.relationship('Club', secondary=favorites)
```
The User model is pretty simple. It would maintain the user's 
information like username, name, and favorites (through 
relationship previously defined). The primary key is id, because 
name and username could potentially change.

### API
Here are the REST API routes I implemented. I tried to do as much 
error checking with requests as possible. For example, checking 
if the club or user in the request exists.

#### GET `/api/user/:username`
This request will return user information for the specific 
username specified in the route paramter. Here we would only 
expose the name and the username of the user for sake of privacy.

#### GET `/api/clubs`
This request returns a list of all clubs in JSON format.

#### GET `/api/clubs?search=<QUERY>`
This request will return clubs where the club name contains the 
query string (case insensitive). Behind the scenes, a SQL `LIKE` 
operator is used with `%<Query>%` on club names, which does a 
case insensitive search to see if the query is a substring of 
a club's name.

#### POST `/api/clubs`
This request can be used to create a new club. You just need to 
specify club code and a club name in the request body. Tags and 
description are optional.

Sample Request Body:
```
{
   "code":"abcd",
   "name":"Water Club",
   "description":"We love water",
   "tags":["Undergraduate","Health","Graduate"]
}
```

#### POST `/api/:club/favorite`
This request is used to allow a user to favorite a specific club, 
which is defined by name in the route parameter. The user is 
defined in the request body. If the club is already favorited, 
then this will unfavorite the club for the user.

Sample Request Body:
```
{
    "user": "josh"
}
```

#### GET `/api/:club/favorite`
This request returns the number of favorites for the club 
specified by name in the route parameter.

#### PATCH `/api/clubs/:code`
This request will modify the club specified by club code in the 
route parameter. You can modify anything about the club, except 
for the primary key, the id. What's convenient about this request 
is that you only need to specify the fields that are changing in 
the request body.

Sample request body for changing name and tag fields:
```
{
    "name": "Water Lover Club",
    "tags": ["Undergraduate", "Health", "Meme", "Graduate"]
}
```

#### GET `/api/tag_count`
This request shows a list of tags with the number of clubs 
associated with that club.

### Bonus Features
#### Scraping
The first bonus feature I decided to tackle was the web scraper. 
I wrote web scraping code in `webscraper.py`. And then I wrote 
a method in `bootstrap.py` that would include all the scraped 
clubs in the database.

For this section, I used Beautiful Soup.

## Installation

1. Click the green "use this template" button to make your own copy of this repository, and clone it. Make sure to create a **private repository**.
2. Change directory into the cloned repository.
3. Install `pipenv`
   - `pip install --user --upgrade pipenv`
4. Install packages using `pipenv install`.

## File Structure

- `app.py`: Main file. Has configuration and setup at the top. Add your [URL routes](https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing) to this file!
- `models.py`: Model definitions for SQLAlchemy database models. Check out documentation on [declaring models](https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/) as well as the [SQLAlchemy quickstart](https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/#quickstart) for guidance
- `bootstrap.py`: Code for creating and populating your local database. You will be adding code in this file to load the provided `clubs.json` file into a database.

## Developing

0. Determine how to model the data contained within `clubs.json` and then complete `bootstrap.py`
1. Run `pipenv run python bootstrap.py` to create the database and populate it.
2. Use `pipenv run flask run` to run the project.
3. Follow the instructions [here](https://www.notion.so/pennlabs/Backend-Challenge-Fall-20-31461f3d91ad4f46adb844b1e112b100).
4. Document your work in this `README.md` file.

## Reference frontend

If you want to use the reference frontend to see if your implementation of the
backend is working correctly, follow the below steps

1. `cd reference-frontend` to enter the directory.
2. `yarn install` to download all the dependencies.
3. `yarn start` to start the server.
4. Navigate to `localhost:3000` to see if the website is working correctly.

Feel free to make changes to the reference frontend as necessary. If you want
to work on the reference frontend as a supplementary challenge, the current
implementation doesn't implement _tags_. Modifying the reference frontend to
list club tags while browsing clubs or allow users to include tags while
creating a new club could be a good place to start with improving the frontend.

## Submitting

Follow the instructions on the Technical Challenge page for submission.

## Installing Additional Packages

Use any tools you think are relevant to the challenge! To install additional packages
run `pipenv install <package_name>` within the directory. Make sure to document your additions.
