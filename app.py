from flask import Flask, request, redirect, render_template, session, flash
from models import dbConnect
from util.user import User
from datetime import timedelta
import hashlib
import uuid
import re

app = Flask(__name__)
app.secret_key = uuid.uuid4().hex
app.permanent_session_lifetime = timedelta(days=30)

#サインイン
@app.route('/signin')
def signup():
    return render_template('registration/signin.html')

@app.route('/signin', methods=['POST'])
def signup(): #登録情報の取得
    user_name = request.form.get('user_name')
    email = request.form.get('email')
    user_id = request.form.get('name')
    password = request.form.get('password')
    password_chk = request.form.get('password_chk')

    def isMail(email):
        pattern = "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return re.match(pattern, email)


    if user_id == '' or email =='' or password == '' or password_chk == '':
        flash('空のフォームがあります')
    elif password != password_chk :
        flash('パスワードが一致していません。')
    elif isMail(email) is None:
        flash('正しいメールアドレスを記入してください。')
    else:
        user_id = uuid.uuid4
        password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        user = User(user_id, user_name, email, password)
        DBuser = dbConnect.getUser(email)

    if DBuser != None: #emailが登録済み
        flash('すでに登録済みのユーザーです。')
    else:
        dbConnect.createUser(user)
        UserId = str(user_id)
        session['user_id'] = UserId
        return redirect('/')
    return redirect('/signup')  #間違ってる所をクリア、色塗りの方がいいんじゃ

#メッセージ追加
app.route('/message',methods=['POST'])
def add_message():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect('/login')

    message = request.form.get('message')
    ch_id = request.form.get('channel_id')

    if message:
        dbConnect.createMessamge(user_id,ch_id,message) #reactionは別で更新

    channel = dbConnect.getChannelById(ch_id)
    messages = dbConnect.getMessageAll(ch_id)

    return render_template('detail.html',messages=messages,channel=channel,user_id=user_id)

#メッセージ削除
app.route('delete_message',methods=['POST'])
def delete_message():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect('/login')

    message_id = request.form.get('message_id')
    ch_id = request.form.get('channel_id')
    if message_id:
        dbConnect.deleteMessage(message_id)

    channel = dbConnect.getChannelById(ch_id)
    messages = dbConnect.getMessageAll(ch_id)

    return render_template('detail.html',messages=messages,channel=channel,user_id=user_id)

#リアクション追加
app.route('reaction_message',methods=['POST'])
def reaction_message():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect('/login')

    message_id = request.form.get('message_id')
    ch_id = request.form.get('channel_id')
    if message_id:
        dbConnect.addReaction(message_id)

    channnel = dbConnect.getChannelById(ch_id)
    messages = dbConnect.getMessageAll(ch_id)

    return render_template('detail.html',messages=messages,user_id=user_id)