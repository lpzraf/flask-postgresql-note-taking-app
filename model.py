class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20), unique=True)
    notes = db.relationship('Note', backref='user', lazy='dynamic', cascade="all,delete")

    def __init__(self,username,password):
        self.username = username
        self.password = password
    
    def __repr__(self):
        return '<User %r>' % self.username

class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    date = db.Column(db.DateTime)
    note_body = db.Column(db.String(280), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self,title,date,note_body, user_id):
        self.title = title
        self.date = date
        self.note_body = note_body
        self.user_id = user_id





# import json

# # notes db
# def load_db():
#     with open("notes_data_db.json") as f:
#         return json.load(f)

# def save_db():
#     with open("notes_data_db.json", 'w') as f:
#         return json.dump(db, f)

# # user db
# def load_user_db():
#     with open("users_data_db.json") as f:
#         return json.load(f)

# def save_user_db():
#     with open("users_data_db.json", 'w') as f:
#         return json.dump(user_db, f)


# db = load_db()
# user_db = load_user_db()

