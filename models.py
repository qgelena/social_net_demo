from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    # TODO: change to salt+password hash
    password = db.Column(db.String(100))

    def __init__(self, username, password):
        self.username = username
        self.password = password

# Post Model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime())
    content = db.Column(db.String())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, timestamp, content, user_id):
        self.timestamp = timestamp
        self.content = content
        self.user_id = user_id

# Relationship Model
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    timestamp = db.Column(db.DateTime())
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id'),)
    
    def __init__(self, user_id, post_id, timestamp):
        self.user_id = user_id
        self.post_id = post_id
        self.timestamp = timestamp

if __name__ == '__main__':
    from app import app
    db.create_all(app=app)