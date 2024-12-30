#  _________________________Importing the necessry packages_________________________
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo  import MongoClient
import wolframalpha
from youtubesearchpython import VideosSearch
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import wikipedia
import openai
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from translate import Translator
import os
import heapq
from sudoku import Sudoku
import stripe
import random
import speech_recognition as sr
import moviepy.editor as mp

# _________________________Connecting flask_________________________
app= Flask(__name__)
app.secret_key= "password"
socketio = SocketIO(app)

# _________________________Connecting OpenAI_________________________
openai.api_key = "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"

# _________________________Connecting MongoDB_________________________
client= MongoClient("mongodb://localhost:27017/")
db= client["Arivagam-IIIT"]
users= db["users"]
chat= db["chat_messages"]
# leaderboard = db["leaderboard"]

# _________________________Connecting Wolframalpha_________________________
client= wolframalpha.Client('6WAEP9-R9GHYET35U')

#__________________________Cache Memory Managemnet - LRU____________________
cache_lru = []

# _________________________Connecting HTML_________________________
# Landing Page
@app.route("/")
def LandingPage():
    return render_template("LandingPage.html")

# Login Page
@app.route('/Login', methods=['GET','POST'])
def Login():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'yukthi@gmail.com':
            return redirect(url_for('admin'))

        user = db.users.find_one(
            {'username': username, 'password': password})

        if user:
            session['user'] = username
            return redirect(url_for('home'))
        else:
            correction = "Invalid username or password"
            return render_template('Login.html',correction=correction)

    return render_template('Login.html')

# Sign-Up Page
@app.route('/SignUp', methods=['GET','POST'])
def SignUp():

    if request.method=='POST':

        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['email']
        password = request.form['password']
        confpassword = request.form['confpassword']
        age = request.form['age']
        gender = request.form['gender']
        preflang1 = request.form['preflang1']
        preflang2 = request.form['preflang2']
        mentor = request.form['option']
        hist1=[]
        hist2=[]
        hist3=[]
        subtitle=""
        id=""

        if db.users.find_one({'username': username}):
            correction = "Mail-ID alraedy taken"
            return render_template('SignUp.html',correction=correction)
        elif password != confpassword:
            correction = "Passwords are not similar"
            return render_template('SignUp.html',correction=correction)

        user_data = {'username': username, 'password': password,
                     'firstname': firstname, 'lastname': lastname,
                     'history1':hist1,'history2':hist2, 'history3':hist3,
                     'age':age, 'subtitle':subtitle,
                     'id':id,'preflang1':preflang1, 'gender':gender,"mentor" :mentor,
                     'preflang2':preflang2,'confpassword':confpassword,'leaderboard':'50'}
        db.users.insert_one(user_data)

        session['user'] = username
  
        return redirect(url_for('home'))

    return render_template('SignUp.html')

# Home Page.
@app.route('/home', methods=['GET','POST'])
def home():
    text = request.data.decode('utf-8')
    if text:
        user = db.users.find_one({'username': 'yukthi@gmail.com'})
        if text == 'button1':
            lilink = user.get('li1')
        elif text == 'button2':
            lilink = user.get('li2')
        elif text == 'button3':
            lilink = user.get('li3')
        elif text == 'button4':
            lilink = user.get('li4')
        elif text == 'button5':
            lilink = user.get('li5')
        elif text == 'button6':
            lilink = user.get('li6')
        elif text == 'button7':
            lilink = user.get('li7')
        elif text == 'button8':
            lilink = user.get('li8')
        elif text == 'button9':
            lilink = user.get('li9')
        elif text == 'button10':
            lilink = user.get('li10')
        elif text == 'button11':
            lilink = user.get('li11')
        elif text == 'button12':
            lilink = user.get('li12')
        elif text == 'button13':
            lilink = user.get('li13')
        elif text == 'button14':
            lilink = user.get('li14')
        elif text == 'button15':
            lilink = user.get('li15')
        elif text == 'button16':
            lilink = user.get('li16')
        elif text == 'button17':
            lilink = user.get('li17')
        elif text == 'button18':
            lilink = user.get('li18')
        elif text == 'button19':
            lilink = user.get('li19')
        elif text == 'button20':
            lilink = user.get('li20')
        elif text == 'button21':
            lilink = user.get('li21')
        user = db.users.find_one({'username': session['user']})
        if user:
            db.users.update_one({'username':session['user']},{'$set':{'courslist':lilink}})
    user = db.users.find_one({'username': session['user']})
    if user:
        age=user.get('age') 
        # disability = user.get('disability')
    if request.method == 'POST':
        to_search = request.form['ytsearch']
        playsearch = request.form['ytplay']
        if playsearch:
            return redirect(url_for('Video'))
        videosSearch = VideosSearch(to_search, limit=7)
        results = videosSearch.result()
        video_links = []
        for result in results['result']:
            video_links.append(result['link'])
        link = video_links[0]
        sep_l = link.split('=')
        id = sep_l[-1]
        try:
            transcript = YouTubeTranscriptApi.get_transcript(id)
        except:
            try:
                link = video_links[1]
                sep_l = link.split('=')
                id = sep_l[-1]
                transcript = YouTubeTranscriptApi.get_transcript(id)
            except:
                link = video_links[2]
                sep_l = link.split('=')
                id = sep_l[-1]
                transcript = YouTubeTranscriptApi.get_transcript(id)
        script = ""
        for text in transcript:
            t = text["text"]
            if t != '[Music]':
                script += t + " "

        subtitle = script

        if subtitle:
            user = db.users.find_one({'username': session['user']})
            if user:
                db.users.update_one({'username':session['user']},{'$set':{'subtitle':subtitle}})
                db.users.update_one({'username':session['user']},{'$set':{'id':id}})
                db.users.update_one({'username':session['user']},{'$set':{'video_links':video_links}})
            return redirect(url_for('extract'))
    return render_template('Home.html',age=age)
#extract
@app.route('/extract', methods=['GET', 'POST'])
def extract():
    user = db.users.find_one({'username': session['user']})
    if user:
        subtitle=user.get('subtitle') 
        video_links = user.get('video_links')
        id=user.get('id')
        vll=[]
        for i in video_links:
            sep_l = i.split('=')
            idi = sep_l[-1]
            vll.append(idi)
        id1=vll[1]
        id2=vll[2]
        id3=vll[3]
        id4=vll[4]
        id5=vll[5]
        id6=vll[6]
        lii = []
        for i in subtitle:
            if i ==' ':
                lii.append('/static/img/space.jpg')
                continue
            if i.isupper():
                i = i.lower()
            if i.isdigit():
                continue
            if not i.isalnum():
                continue
            a='/static/img/'+i+'.jpg'
            lii.append(a)
        data = os.listdir('C:/Users/Sujay R/OneDrive/Desktop/Arivagam.-IIIT--main/static/vdo')
        s = subtitle.split()
        org_words = ['an','the','a','s','of','so']
        li =[]
        for i in s:
            if i ==" ":
                continue
            elif i.isupper():
                i = i.lower()
            elif i.isdigit():
                continue
            elif not i.isalnum():
                continue
            elif i in org_words:
                continue
            elif i+'.webm' in data:
                a='/static/vdo/'+i+'.webm'
                li.append(a)
            else :
                for j in i:
                   b='/static/vdo/'+j+'.webm' 
                   li.append(b)
    print(li)
    return render_template('extract.html', subtitle=subtitle,id=id,id1=id1,id2=id2,id3=id3,id4=id4,id5=id5,id6=id6,li=li,lii=lii)

@app.route('/signtrans',methods=['GET','POST'])
def signtrans():
    video_file = "C:/Users/Sujay R/OneDrive/Desktop/Arivagam.-IIIT--main/static/vdo/train.mp4"
    clip = mp.VideoFileClip(video_file)
    audio_file = f"{os.path.splitext(video_file)[0]}.wav"
    clip.audio.write_audiofile(audio_file)

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    transcript = recognizer.recognize_google(audio)

    print("Transcript:")
    print(transcript)

    lii = []
    for i in transcript:
        if i ==' ':
            lii.append('/static/img/space.jpg')
            continue
        if i.isupper():
            i = i.lower()
        if i.isdigit():
            continue
        if not i.isalnum():
            continue
        a='/static/img/'+i+'.jpg'
        lii.append(a)
    data = os.listdir('C:/Users/Sujay R/OneDrive/Desktop/Arivagam.-IIIT--main/static/vdo')
    s = transcript.split()
    org_words = ['an','the','a','s','of','so']
    li =[]
    for i in s:
        if i ==" ":
            continue
        elif i.isupper():
            i = i.lower()
        elif i.isdigit():
            continue
        elif not i.isalnum():
            continue
        elif i in org_words:
            continue
        elif i+'.webm' in data:
            a='/static/vdo/'+i+'.webm'
            li.append(a)
        else :
            continue
    if len(li) > 55:
        cache_lru = li[-1:-50]
    print(li)
    return render_template('signtrans.html',li=li,lii=lii,subtitle=transcript)

#ytlink page
@app.route('/linkyt',methods=['GET','POST'])
def linkyt():
    if request.method == 'POST':
        yout_li = request.form['yout_li']
        sep_l = yout_li.split('=')
        id = sep_l[-1]
        transcript = YouTubeTranscriptApi.get_transcript(id)
        script = ""
        for text in transcript:
            t = text["text"]
            if t != '[Music]':
                script += t + " "

        subtitle = script
        video_links = ['nfjnjf=ff','nfjnjf=ff','nfjnjf=ff','nfjnjf=ff','nfjnjf=ff','nfjnjf=ff','nfjnjf=ff']

        if subtitle:
            user = db.users.find_one({'username': session['user']})
            if user:
                db.users.update_one({'username':session['user']},{'$set':{'subtitle':subtitle}})
                db.users.update_one({'username':session['user']},{'$set':{'id':id}})
                db.users.update_one({'username':session['user']},{'$set':{'video_links':video_links}})
            return redirect(url_for('extract'))
    return render_template('linkyt.html')

# Video Page.
@app.route('/Video',methods=['GET','POST'])
def Video():
    return render_template('Video.html')

@app.route('/live',methods=['GET','POST'])
def live():
    if request.method == 'POST':
        file = request.files['vdoname']
        save_path = os.path.join('static', 'vdo', 'train.mp4')

        # if os.path.exists(save_path):
        #     os.remove(save_path)
        
        file.save(save_path)
    
        return redirect(url_for('signtrans'))
    return render_template('live.html')

# ProfileEdit Page.
@app.route('/ProfileEdit',methods=['GET', 'POST'])
def ProfileEdit():
    if request.method=='POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['email']
        password = request.form['password']
        confpassword = request.form['confpassword']
        age = request.form['age']
        gender = request.form['gender']
        preflang1 = request.form['preflang1']
        preflang2 = request.form['preflang2']
        user = db.users.find_one({'username': session['user']})
        if user:
            db.users.update_many({'username':session['user']},{'$set':{'username': username, 'password': password,
                     'firstname': firstname, 'lastname': lastname,
                     'age':age,
                     'preflang1':preflang1, 'gender':gender, 
                     'preflang2':preflang2,'confpassword':confpassword}})
  
        return redirect(url_for('home'))
    user = db.users.find_one({'username': session['user']})
    if user:
        username = user.get('username')
        password = user.get('password')
        firstname = user.get('firstname')
        lastname = user.get('lastname')
        age = user.get('age')
        gender = user.get('gender')
        preflang1 = user.get('preflang1')
        preflang2 = user.get('preflang2')
        confpassword = user.get('confpassword')
    return render_template('ProfileEdit.html',username = username,password=password,firstname=firstname,lastname=lastname,age=age,gender=gender,preflang1=preflang1,preflang2=preflang2,confpassword=confpassword)


#Transformers
def transfromers_vec(lines):
    from transformers import BertTokenizer, BertModel
    import torch

    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    model = BertModel.from_pretrained("bert-base-uncased")

    input_text = lines


    encoded_output = tokenizer.encode_plus(
        input_text,
        add_special_tokens=True, 
        return_tensors="pt"
    )

    input_ids = encoded_output["input_ids"]
    attention_mask = encoded_output["attention_mask"]

    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)

    last_hidden_states = outputs.last_hidden_state 

    tokens = tokenizer.convert_ids_to_tokens(input_ids[0])
    dense_vectors = last_hidden_states[0]
    return tokens,dense_vectors


# Courses Page.
@app.route('/Courses',methods=['GET','POST'])
def Courses():
    user = db.users.find_one({'username': session['user']})
    if user:
        courlist = user.get('courslist')
    transcript = YouTubeTranscriptApi.get_transcript(courlist[0])
    script = ""
    for text in transcript:
        t = text["text"]
        if t != '[Music]':
            script += t + " "

    subtitle = script

    transfromers_vec(script)
    
    id1=courlist[0]
    id2=courlist[1]
    id3=courlist[2]

    lii = []
    for i in subtitle:
        if i ==' ':
            lii.append('/static/img/space.jpg')
            continue
        if i.isupper():
            i = i.lower()
        if i.isdigit():
            continue
        if not i.isalnum():
            continue
        a='/static/img/'+i+'.jpg'
        lii.append(a)
    data = os.listdir('C:/Users/Sujay R/OneDrive/Desktop/Arivagam.-IIIT--main/static/vdo')
    s = subtitle.split()
    org_words = ['an','the','a','s','of','so']
    li =[]
    for i in s:
        if i ==" ":
            continue
        elif i.isupper():
            i = i.lower()
        elif i.isdigit():
            continue
        elif not i.isalnum():
            continue
        elif i in org_words:
            continue
        elif i+'.webm' in data:
            a='/static/vdo/'+i+'.webm'
            li.append(a)
        else :
            for j in i:
                b='/static/vdo/'+j+'.webm' 
                li.append(b)       
    # print(li) 
    return render_template('Courses.html',subtitle=subtitle,id1=id1,id2=id2,id3=id3,li=li,lii=lii)

# Chat ChatBot Page.
@app.route('/ChatBot',methods=['GET','POST'])
def ChatBot():
    chatbot_li =['/static/vdo/hello.webm', '/static/vdo/welcome.webm','/static/vdo/hello.webm', '/static/vdo/welcome.webm','/static/vdo/hello.webm', '/static/vdo/welcome.webm',
                '/static/vdo/oriented.webm', '/static/vdo/programming.webm', '/static/vdo/language.webm', '/static/vdo/released.webm', '/static/vdo/in.webm', '/static/vdo/thought.webm', '/static/vdo/was.webm', '/static/vdo/older.webm', '/static/vdo/than.webm', '/static/vdo/that.webm', '/static/vdo/from.webm', '/static/vdo/like.webm',
                '/static/vdo/but.webm', '/static/vdo/apparently.webm', '/static/vdo/just.webm', '/static/vdo/vaporwave.webm', '/static/vdo/age.webm', '/static/vdo/being.webm', '/static/vdo/language.webm']*20
    if request.method=='POST':
        user_input = request.form['dbt']
        bot_response = chat(user_input)
        return jsonify({'output': bot_response})
    else:
        return render_template('ChatBot.html',chatbot_li=chatbot_li)


public_key = "pk_test_51OAc4kSCU9tagpDmW1MEp5JyCw7sfmbVqlxs4SYpfxGpoFsCHxbEzW69eKIWK7Sr1XHWx4CROKSLZZ90h7iAHgtT00Zmb1OGcC"
stripe.api_key = "sk_test_51OAc4kSCU9tagpDmxHbWoT7JizAtvE7yZGeKBKWGE7SfojdYPZPW1AIyjmVcS0bXXZF7S0YUsj9unkcXiOFH3Jvn001ZVKT8ir"

@app.route('/stripe_index')
def stripe_index():
    return render_template('stripe_index.html', public_key=public_key)

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

@app.route('/premium')
def premium():
    return render_template('premium.html')

@app.route('/payment', methods=['POST'])
def payment():
    # customer = stripe.Customer.create(email=request.form['stripeEmail'],
    #                                   source=request.form['stripeToken'])

    # charge = stripe.Charge.create(
    #     customer=customer.id,
    #     amount=399, 
    #     currency='INR',
    #     description='Mentor'
    # )

    return redirect(url_for('thankyou'))

#Mentor 
@app.route('/mentor',methods=['GET','POST'])
def mentor():
    avail_mentors = users.find({"mentor":"yes"})
    prof_list =['IoT','Web Master','App Dev']
    pro = random.choice(prof_list)
    return render_template('mentor.html',avail = avail_mentors,pro=pro)

@app.route('/spelltest')
def spelltest():
    return render_template('test1.html')

@app.route('/readtest')
def readtest():
    return render_template('test2.html')

@app.route('/pre',methods=['GET', 'POST'])
def pre():
    if request.method=='POST':
        difficulty = request.form['difficulty'] 
        user = db.users.find_one({'username': session['user']})
        if user:
            db.users.update_one({'username':session['user']},{'$set':{'difflevel':difficulty}})
        return redirect(url_for('puzzle'))
    return render_template('pre.html')

@app.route('/puzzle',methods=['GET', 'POST'])
def puzzle():
    solist = request.form.getlist('grid_data')
    if solist:
        # print(solist)
        user = db.users.find_one({'username': session['user']})
        if user:
            db.users.update_one({'username':session['user']},{'$set':{'solist':solist}})
    user = db.users.find_one({'username': session['user']})
    if user:
        level = user.get('difflevel')
    level = int(level)/100
    game = Sudoku(3).difficulty(0.5)
    num_board = game.board
    nums = []
    for i in num_board:
        for j in i:
            if j is None:
                nums.append(' ')
            else:
                nums.append(j)
    perfect = game.solve()
    soln_board = perfect.board
    setsoln = []
    for i in soln_board:
        for j in i:
            if j is None:
                setsoln.append(' ')
            else:
                setsoln.append(j)
    user = db.users.find_one({'username': session['user']})
    if user:
        db.users.update_one({'username':session['user']},{'$set':{'perlist':setsoln}})
    return render_template('puzzle.html',nums = nums)

@app.route('/solution',methods=['GET','POST'])
def solution():
    result=""
    user = db.users.find_one({'username': session['user']})
    if user:
        check1 = user.get('solist')
        check2 = user.get('perlist')
        score = user.get('leaderboard')
        if check1 == check2:
            result = "Congrats! You have won"
            points = int(score) + 50
            db.users.update_one({'username':session['user']},{'$set':{'leaderboard':str(points)}})
        else:
            result = "Better luck next time"
            points = int(score) - 25
            db.users.update_one({'username':session['user']},{'$set':{'leaderboard':str(points)}})
    else:
        result = "User not found"
    return render_template('solution.html', result=result, nums=check2)

@app.route('/leaderboard',methods=['GET','POST'])
def leaderboard():
    d = {}
    entries = users.find({})
    for entry in entries:
        d[entry.get('firstname')] = entry.get('leaderboard')
    dict1 = {k: v for k, v in sorted(d.items(), key=lambda item: item[1], reverse=True)}
    return render_template('leaderboard.html', leaderboard=dict1)

@app.route('/find',methods=['GET','POST'])
def find():
    sofindlist = request.form.getlist('grid_data')
    if sofindlist:
        org=[]
        for i in sofindlist:
            for j in i:
                if j==',':
                    org.append(0)
                else:
                    org.append(int(j))
        sublists = [org[i:i+9] for i in range(0, len(org), 9)]
        sublists.pop()
        soll = Sudoku(3,3,board=sublists)
        ans = soll.solve()
        kara = ans.board
        nums=[]
        for i in kara:
            for j in i:
                nums.append(j)
        user = db.users.find_one({'username': session['user']})
        if user:
            db.users.update_one({'username':session['user']},{'$set':{'god':nums}})
        return redirect(url_for('findsolution'))
    return render_template('find.html')

@app.route('/findsolution',methods=['GET','POST'])
def findsolution():
    user = db.users.find_one({'username': session['user']})
    if user:
        nums = user.get('god')
    return render_template('findsolution.html',nums=nums)
    
# Meeting In Page.
@app.route('/MeetingIn')
def MeetingIn():
    return render_template('MeetingIn.html')

# Meeting Page.
@app.route('/Meeting')
def Meeting():
    return render_template('Meeting.html')

# Meeting Home Page.
@app.route('/MeetingHome',methods=['GET', 'POST'])
def MeetingHome():
    if request.method=='POST':
        roomID = request.form['roomID']
        return redirect("/vdocall?roomID="+roomID)
    return render_template('MeetingHome.html')

# ________________________________________________Functions________________________________________________
# ChatBot Function.

def chat(prompt):
    import requests

    url = "https://chatgpt-42.p.rapidapi.com/conversationgpt4-2"

    payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "system_prompt": "",
        "temperature": 0.9,
        "top_k": 5,
        "top_p": 0.9,
        "max_tokens": 256,
        "web_access": False
    }
    headers = {
        "x-rapidapi-key": "43cc727829msh5644c8389123bf7p18e60cjsnc980a33f130a",
        "x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.json())
    return response.json()['result']


user_languages = {} 
user_names = {} 
def translate_message(message, source_language, target_language):
    translator = Translator(to_lang = target_language)
    translated_message = translator.translate(message)
    return translated_message

# Group Chat Page.
@app.route('/GroupChat')
def GroupChat():
    return render_template('GroupChat.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('message')
def handle_message(data):
    room = data['room']
    message = data['message']
    source_language = user_languages[room]
    user_name = user_names[request.sid]
    
    for client_room, target_language in user_languages.items():
        if client_room != room: 
            translated_message = translate_message(message, source_language, target_language)
            emit('user_message', {'user': user_name, 'message': translated_message}, room=client_room)

@socketio.on('create')
def handle_create(data):
    room = data['room']
    user_languages[room] = data['language']
    user_names[request.sid] = data['user']
    join_room(room)
    emit('system_message', {'message': f'You have created and joined room {room}.'})
    emit('system_message', {'message': 'Translation is enabled in this room.'}, room=room)

@socketio.on('join')
def handle_join(data):
    room = data['room']
    user_languages[room] = data['language']
    user_names[request.sid] = data['user']
    join_room(room)
    emit('system_message', {'message': f'You have joined room {room}.'})
    emit('system_message', {'message': 'Translation is enabled in this room.'}, room=room)

@socketio.on('leave')
def handle_leave(data):
    room = data['room']
    user_name = user_names[request.sid]
    leave_room(room)
    emit('system_message', {'message': f'{user_name} has left the room.'}, room=room)
    del user_names[request.sid] 
    emit('update_users', {'users': list(user_names.values())}, room=room)  

if __name__== "__main__":
    socketio.run(app, debug=True)