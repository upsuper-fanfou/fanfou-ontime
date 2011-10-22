# - * - coding: UTF-8 - * -

import json
import urllib
import urlparse

import oauth2 as oauth

from flask import session, g, request, \
        url_for, redirect, render_template

from ontime import app

consumer_key = app.config['CONSUMER_KEY']
consumer_secret = app.config['CONSUMER_SECRET']
consumer = oauth.Consumer(consumer_key, consumer_secret)

request_token_url = 'http://fanfou.com/oauth/request_token'
access_token_url = 'http://fanfou.com/oauth/access_token'
authorize_url = 'http://fanfou.com/oauth/authorize'
authenticate_url = 'http://fanfou.com/oauth/authenticate'

@app.before_request
def before_request():
    if 'user_id' not in session:
        if not request.path.startswith(url_for('auth')):
            return redirect(url_for('auth'))
    else:
        user_id = session['user_id']
        cur = g.db.cursor()
        cur.execute("""
            SELECT `token`, `secret` FROM `users`
            WHERE `user_id`=%s
            """, (user_id, ))
        access_token = cur.fetchone()
        token = oauth.Token(access_token['token'], access_token['secret'])
        g.client = oauth.Client(consumer, token)

@app.route('/auth')
def auth():
    client = oauth.Client(consumer)
    resp, content = client.request(request_token_url, 'GET')
    request_token = dict(urlparse.parse_qsl(content))
    url = authenticate_url + '?' + urllib.urlencode({
        'oauth_token': request_token['oauth_token'],
        'oauth_callback': url_for('callback_page', _external=True)
        })
    if 'user_id' in session:
        del session['user_id']
    session['token'] = request_token
    return redirect(url)

@app.route('/auth/callback')
def callback_page():
    return render_template('callback.html')

@app.route('/auth/callback.js')
def callback():
    request_token = session.pop('token', None)
    if request_token is None:
        return redirect(url_for('auth'))
    token = oauth.Token(request_token['oauth_token'],
            request_token['oauth_token_secret'])
    client = oauth.Client(consumer, token)
    resp, content = client.request(access_token_url, 'GET')
    access_token = dict(urlparse.parse_qsl(content))
    token = oauth.Token(access_token['oauth_token'],
            access_token['oauth_token_secret'])
    client = oauth.Client(consumer, token)
    resp, content = client.request('http://api.fanfou.com/users/show.json', 'GET')
    content = json.loads(content)
    user_id = content['id']
    user_name = content['name']
    user_image = content['profile_image_url']
    
    cur = g.db.cursor()
    cur.execute("""
        REPLACE INTO `users`
        (`user_id`, `token`, `secret`)
        VALUES (%s, %s, %s)
        """, (
            user_id,
            access_token['oauth_token'],
            access_token['oauth_token_secret']
            ))
    g.db.commit()

    session['user_id'] = user_id
    session['user_name'] = user_name
    session['user_image'] = user_image
    return render_template('callback.js')
