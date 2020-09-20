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

Another relationship I had was comments, which you'll 
see below within the models. Comments have a one-to-many 
relationship, with clubs and users. Every comment can be 
connected to one club or one user (the author), but users 
and clubs can have many comments.

#### Models
```
class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    tags = db.relationship('Tag', secondary=tag_relations)
    favorites = db.relationship('User', secondary=favorites)
    comments = db.relationship('Comment', backref='comments')
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
    password = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(80), nullable=False)
    year = db.Column(db.Integer)
    major = db.Column(db.String(80))
    favorites = db.relationship('Club', secondary=favorites)
    comments = db.relationship('Comment', backref='club_comments')
```
The User model is pretty simple. It would maintain the user's 
information like username, password, name, email, year, major. Note, 
that even though password is stored, it is a secure hashed 
password using bcrypt. Also, I wanted to be able to access 
favorites and comments through relationships. The primary key 
is id, because name and username could potentially change.

```
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
```
Here is the model for comments, which was a bonus feature 
that I pursued. Here we see the user_id and club_id 
columns, which link the comment to the author and the 
club it is talking about.

### API
Here are the REST API routes I implemented. I tried to do as much 
error checking with requests as possible. For example, checking 
if the club or user in the request exists and 
explaining the error in the response.

**IMPORTANT:** I implemented login/logout/signup so to use `POST` 
requests, you have to be logged in. You can use Josh's account which 
is:  
username: **josh**  
password: **Password1!**  
Additonally, the username for any 
`POST` requests that need it will be 
gotten through the session. For example, before, 
favoriting would need a username in the request body, 
but now we can just look at the session.

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
**Requires Login**

This request can be used to create a new club. You 
just need to club name in the request body. If no 
club code is specified (like in the request from 
the frontend), then a code will try to be 
generated by the first letters in the club name. I 
wasn't too sure what the club code was exactly used 
for; I just assumed it was related to the club and 
not something that was random. Tags and description 
are optional. It's good to note that any tags used that 
didn't exist before, will be created in the database
as well.

I also noticed that the frontend was still sending 
form data instead of JSON, so I had to add a check 
for that and a function to convert the form data 
into JSON.

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
**Requires Login**

This request is used to allow a user to favorite a specific club, 
which is defined by name in the route parameter. The user is 
defined from the session. If the club is already favorited, 
then this will unfavorite the club for the user.

The request body originally included a user key-value pair, but now 
since sessions are used, we can just use the username from the 
session.

#### GET `/api/:club/favorite`
This request returns the number of favorites for the club 
specified by name in the route parameter.

#### PATCH `/api/clubs/:code`
**Requires Login**

This request will modify the club specified by club code in the 
route parameter. You can modify anything about the club, except 
for the primary key, the id. What's convenient about this request 
is that you only need to specify the fields that are changing in 
the request body. It's also good to note that if you add tags 
that don't already exist, those will be entered into the database 
too.

Sample request body for changing name and tag fields:
```
{
    "name": "Penn Lorem Ipsum Club",
    "tags": ["Undergraduate", "Literary", "Graduate"]
}
```

#### GET `/api/tag_count`
This request shows a list of tags with the number of clubs 
associated with that club.

#### GET `/api/:club/comment`
The request will respond with a list of all the comments 
for the club specified by name in route parameter.

#### POST `/api/:club/comment`
**Requires Login**

This request is used to create a comment for the club 
with the name specified by the route parameter. The 
request would have the comment text.

Sample request body (the author is the username stored in the 
session):
```
{
    "text": "I love this club!!!!"
}
```

#### POST `/api/signup`
This post request is used for creating a new User. 
It is required to have username, password, email, and name 
in the request body. Year and major are optional 
fields. It is important to note that the passwords 
are stored securely witha hash. Another important 
thing is that usernames can't be repeated and the 
API will respond with "Username already exists" if 
that's the case. Addtionally, the user will be automatically 
signed in after creating their account.

Sample request body:
```
{
    "username": "kevin",
    "name": "Kevin Chen",
    "password": "Password1!",
    "email": "kevin@gmail.com",
    "year": 2023,
    "major": "Computer Science"
}
```

#### POST `/api/login`
This is the request used for logging in by authenticating a 
user's credentials, username and password. If successful, 
a session will be created for that user. Note that when using 
Postman, the session only works for the desktop app.

Sample request body:
```
{
    "username": "josh",
    "password": "Password1!"
}
```

#### GET `/api/logout`
This is the endpoint used to logout of a user that is signed in. 
This will remove the username from the session.

#### GET `/api/emails/:code`
**Requires Login**

This will get a mailing list for the club with the matching club code. 
The mailing list is the emails of all the users that liked the club. 
Note that for this request, there needs to be a signed in user. I didn't 
want to make it so users that weren't signed in could see people's 
emails.

#### PATCH `/api/user`
**Requires Login**

This will update the user profile of the user that is currently signed 
in. That means to use this request route, you will need to be signed 
in. You can modify username, password, name, email, year, and major. 
If the username is updated, the username stored by the session is also 
updated to maintain consistency. Like account creation, if username is 
already taken, and error message describing this will be returned.

Sample request body:
```
{
    "name": "New User Changed",
    "username": "newuserchanged",
    "password": "Password2!",
    "email": "newuserchanged@gmail.com",
    "year": 2022,
    "major": "Economics"
}
```

#### GET `/api/clubs/:tag`
This `GET` request will fetch all of the clubs that have the tag 
specified in the route.

### Bonus Features
#### Scraping
The first bonus feature I decided to tackle was the web scraper. 
I wrote web scraping code in `webscraper.py`. And then I wrote 
a method in `bootstrap.py` that would include all the scraped 
clubs in the database.

For this section, I used Beautiful Soup.

#### Club Comments
The second bonus feature I did was implementing club 
comments. To do this, I had to create a new Comment model 
and create some new relationships with the Club and User 
models.

I also added a new route (`GET` and `POST`) to access 
comments on a specified club, and create new comments.

Implementation details can be found in the documentation 
above.

#### Login/Logout/Signup
The third bonus feature I did was implementing login/logout/signup 
and also implementing session state. This bonus required me to use 
bcrypt and flask sessions.

Bcrypt was used to safely store hashed passwords in the database. 
And flask sessions was used to maintain information about the 
signed in user across multiple requests. 

Now that I had user sessions I changed the `POST` requests to 
require a user to be logged in. Otherwise, the response would 
be "access denied". Additionally, with session state, I could 
get rid of the username field in request bodies, and instead 
use the username stored by the session.

#### New API Routes
The fourth bonus feature was one that I made up. I decided to add 
a few additonal routes that made sense. A route I added allowed 
clubs to `GET` a mailing list of user's who've favorited the club. 
Another route I added allowed a `PATCH` that could update User 
information. I also added a `GET` route that returns all the clubs 
containing a specified tag.

More detail on these routes are above in the API section.

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
