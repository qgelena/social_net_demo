#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime

from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp

import sqlalchemy as sa
import sqlalchemy.exc as sqlexc

from models import db
import models

# Init app 
app = Flask(__name__)

# Init the database
basedir = Path(__file__).absolute().parent
sqlitepath = basedir/'db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + sqlitepath.as_posix()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Init JWT
def authenticate(username, password):
    user = models.User.query.filter_by(username=username).first()
    if user and safe_str_cmp(user.password.encode('utf8'), password.encode('utf8')):
        return user

def identity(payload):
    user_id = payload['identity']
    return models.User.query.get(user_id)

app.config['SECRET_KEY'] = 'we-dont-care-but-this-is-supposed-to-be-strong-salt'
app.config['JWT_AUTH_URL_RULE'] = '/login'
jwt = JWT(app, authenticate, identity)


@app.route('/signup', methods=['POST'])
def signup():
    try:
        username = request.json['username']
        password = request.json['password']
    except KeyError as e:
        return jsonify({
            'status': 'KeyError',
            'args': e.args
        }), 400
    
    # TODO: check password, it should be strong enough

    # otherwise: create a new user in the DB
    user = models.User(username, password)
    db.session.add(user)
    try:
        db.session.commit()
    except sqlexc.IntegrityError as e:
        # most likely, the username already exists,
        return jsonify({"status": "error", "message": str(e)}), 400
    return jsonify({"status": "ok", "id": user.id})

@app.route('/newpost', methods=['POST'])
@jwt_required()
def newpost():
    if 'content' not in request.json:
        return jsonify({"status": "error", "error": "no content"}), 400

    timestamp = datetime.now()
    content = request.json['content']
    user_id = current_identity.id

    post = models.Post(timestamp, content, user_id)
    db.session.add(post)
    db.session.commit()

    return jsonify({"status": "ok", "post_id": post.id})

@app.route('/post/<post_id>', methods=['GET'])
def getpost(post_id):
    post = models.Post.query.get(post_id)
    if post is None:
        return jsonify({'post': post_id, 'error': 'not found'}), 404

    print(post)
    return jsonify({
        'timestamp': post.timestamp,
        'content': post.content
    })

@app.route('/like/<post_id>', methods=['POST'])
@jwt_required()
def like_post(post_id):
    user_id = current_identity.id
    timestamp = datetime.now()

    if models.Post.query.get(post_id) is None:
        return jsonify({"status": "error", "error": "post not found"}), 404

    like = models.Like(user_id, post_id, timestamp)
    db.session.add(like)
    db.session.commit()
    
    return jsonify({"status": "ok"})

@app.route('/unlike/<post_id>', methods=['POST'])
@jwt_required()
def unlike_post(post_id):
    user_id = current_identity.id

    like = models.Like.query.filter_by(user_id=user_id, post_id=post_id).first()
    if like is None:
        return jsonify({"status": "error", "error": "not found"}), 404

    db.session.delete(like)
    db.session.commit()

    return jsonify({"status": "ok"})

@app.route('/analytics', methods=['GET'])
def analytics():
    try:
        date_from = request.args['date_from']
        date_to = request.args['date_to']

        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    except (KeyError, ValueError) as e:
        return jsonify({
            "status": "error",
            "error": str(e),
        }), 400

    Like = models.Like
    q = db.session \
        .query(sa.func.date(Like.timestamp), sa.func.count()) \
        .filter(Like.timestamp.between(date_from, date_to)) \
        .group_by(sa.func.date(Like.timestamp))
    # print('SQL: \n%s\n' % q)
    data = q.all()

    stats = {
        "status": "ok",
        "date_from": date_from,
        "date_to": date_to,
        "likes count per day": data
    }
    return jsonify(stats)

'''
@app.route('/activity', methods=['GET'])
''' 

if __name__ == '__main__':
    app.debug = True
    app.run()