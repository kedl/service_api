#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# @Author: Danny
# @Date: 2017-09-22 14:33:03
# @Last Modified by:   Danny
# @Last Modified time: 2017-09-22 14:33:03

from flask import Flask, jsonify, abort, make_response, request, url_for, g
import base64, time, json
from db_model import session, User, hash_password, Posts

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


def generate_token(username):
    _time = int(time.time())
    str_time = str(int(time.time()))
    s = '.' + username + ':' + str_time + '.'
    token = str(base64.b64encode(bytes(s, encoding='utf-8')))
    return token


def judge_token(token):

    if session.query(User).filter(User.token == token).first() is None:
        return False
    else:
        end_time = session.query(User).filter(
            User.token == token).first().end_time
        now = int(time.time())
        if (now - int(end_time)) >= 600:
            return False
        else:
            return True


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    user = session.query(User).filter(User.username == username).first()
    if username is None or password is None:
        return jsonify({'error': 'please input username or password!'})
    elif len(username.strip()) == 0 or len(password.strip()) == 0:
        return jsonify({'error': 'username or password cannot be empty!'})
    elif session.query(User).filter(User.username == username).first() is None:
        return jsonify({'error': 'user does not exist!'})
    elif not User.verify_password(user, password=password):
        return jsonify({'error': 'login fail!'})
    token = generate_token(username).split("'", 2)[1]
    end_time = int(time.time()) + (10 * 60)
    session.query(User).filter(User.username == username).update({
        User.token:
        token,
        User.end_time:
        end_time
    })
    try:
        session.commit()
    except:
        session.rollback()
    finally:
        session.close()
    return jsonify({
        'code': str(201),
        'content': {
            'token': token,
            'message': 'success'
        }
    })


@app.route('/api/users/add', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        return jsonify({'error': 'please input username or password!'})
    elif len(username.strip()) == 0 or len(password.strip()) == 0:
        return jsonify({'error': 'username or password cannot be empty!'})
    elif len(username) >= 10:
        return jsonify({'error': 'username length must be less than 10'})
    elif len(password) >= 20:
        return jsonify({'error': 'password length must be less than 20'})
    elif session.query(User).filter(
            User.username == username).first() is not None:
        return jsonify({'error': 'user already exists'})
    session.add(User(username=username, password_hash=hash_password(password)))
    try:
        session.commit()
    except:
        session.rollback()
    finally:
        session.close()
    return jsonify({
        'code': str(201),
        'content': {
            'u_id': str(get_user(username).id),
            'username': get_user(username).username
        }
    })


def get_user(username):
    user = session.query(User).filter(User.username == username).first()
    if not user:
        return None
    else:
        return user


@app.route('/api/posts/add', methods=['POST'])
def Commit_post():
    token = request.json.get('token')
    title = request.json.get('title')
    text = request.json.get('text')
    _now = str(int(time.time()))
    if judge_token(token):
        session.add(Posts(title=title, text=text, creat_time=_now))
        try:
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()
        return jsonify({'code': '200', 'Message': 'success'})
    else:
        abort(404)


@app.route('/api/posts/get', methods=['GET'])
def Get_post():
    token = request.json.get('token')
    _id = request.json.get('id')
    if judge_token(token):
        if _id is None:
            abort(404)
        else:
            post = session.query(Posts).filter(Posts.id == _id).first()
            if post is not None:
                return jsonify({
                    'code': str(200),
                    'Content': {
                        'id': post.id,
                        'title': post.title,
                        'text': post.text,
                        'creat_time': post.creat_time
                    }
                })
            else:
                abort(404)
    else:
        abort(404)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(debug=True)
