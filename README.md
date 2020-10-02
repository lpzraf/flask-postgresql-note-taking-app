## Note-Taking App built with Python Flask and PostgreSQL

### Built this app to practice:
1. Refactoring an older app from saving data locally in json to PostgreSQL
2. CRUD
3. RESTful practices
4. Routing with Flask
5. Persisting session data
6. Form submits with Flask
7. User login and logout
8. Creating tables and loading data to PostgreSQL

### Tech
1. Python Flask
2. PostgreSQL
3. Jinja2
4. Vanilla JavaScript
5. Segment.ui for CSS

### Modules
1. Forms
2. Cards
3. Lists
4. Buttons
5. Nav

### Run it! -----NEEDS UPDATE
1. Fork and git clone the repo
2. Cd to the main directory
3. Get into the venv running source venv/bin/activate
4. Run `FLASK_APP=app.py FLASK_ENV=development flask run`
5. Visit http://127.0.0.1:5000/login

### Whats next? -----NEEDS UPDATE
Debugging example: to add user from the terminal load the Python shell and follow the setps below:
1. >>> from app import db, User, Note, datetime
2. >>> db.create_all()
3. >>> raf = User(username='rafi',password='rafi')
4. >>> note1 = Note(title='notes of Rafi', date=datetime.datetime.now(), note_body='note copy', user=rafi)
5. >>> exit()



