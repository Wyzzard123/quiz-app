from flask import Flask, render_template, request, redirect, session
from poc import *
import json
from pymongo import MongoClient
from pprint import pprint
import os
from passlib.hash import pbkdf2_sha256
# from flask_talisman import Talisman

app = Flask(__name__)
# Talisman(app)
#TODO secure passwords

app.secret_key = os.environ.get('QUIZDB_SECRETKEY')

db_user = os.environ.get('QUIZDB_USER')

db_password = os.environ.get('QUIZDB_PASSWORD')

connection_string = f"mongodb+srv://{db_user}:{db_password}@quizapp1-phe85.mongodb.net/test?retryWrites=true&w=majority"

client = MongoClient(connection_string)

quiz_db = client.quiz_app

collection_qna_bank = quiz_db.question_answer_bank

collection_settings = quiz_db.quiz_settings

collection_users = quiz_db.users

collection_temp = quiz_db.temporary_qna_bank

@app.route('/error', methods = ['GET'])
def error():
    """Renders an error page."""
    errorstring = session['error']
    return render_template('error.html', errorstring = errorstring)

# def error_page(errorstring):
#     """Renders an error page."""
    
#     return render_template('error.html', errorstring = "Error")

@app.route('/', methods = ['GET', 'POST'])
def index():
    if not session.get('logged_in'):
        return redirect('/login')
    else:
        return redirect('/quiz_settings')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']

        password_hash = pbkdf2_sha256.hash(password)

        matching_entry = (collection_users.find_one({'username':username}))

        if not matching_entry:
            session['error'] = "No such user!"
            return redirect('/error')

        elif not pbkdf2_sha256.verify(password, matching_entry['password']):
            
            session['error'] = "invalid password!"
            return redirect('/error')
        elif pbkdf2_sha256.verify(password, matching_entry['password']):
            session['logged_in'] = True 
            session['user_id'] = username
            try:
                if session['error']:
                    del session['error']
            except:
                pass


            if collection_settings.find_one({'username':username}) is None:
                # To track whether there are any settings. Otherwise, hide the button which says "New Quiz (Last Used Settings)"
                session['settings_set'] = False
            else:
                session['settings_set'] = True    
            # Redirect to Quiz Settings if the person has any questions. Otherwise, redirect to add_questions instead.
            if collection_qna_bank.find_one({'username':username}) is None:
                # To track whether there are any questions such that we can generate a new quiz
                session['questions'] = False
                return redirect('/quiz_add_questions')
            else:
                session['questions'] = True
                return redirect('/quiz_settings')

            

@app.route('/logout', methods = ['POST'])
def logout():
    if request.method == 'POST':
        session.clear() 
        return render_template('login.html')
    
        

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']

        password_hash = pbkdf2_sha256.hash(password)
        
        matching_entry = (collection_users.find_one({'username':username}))

        if matching_entry:
            
            session['error'] = "User already exists!"
            return redirect('/error')
        else:
            collection_users.insert_one({'username': username, 
            'password': password_hash})

            return redirect('/login')

@app.route('/quiz', methods = ['GET', 'POST'])
def quiz():
    """Randomly generates quizzes and shows the answer/score after submitting."""
    if not session.get('logged_in'):
        return redirect('/login')
    else:
        username = session['user_id']
        if request.method == 'GET':
            # If there is a settings page, go through "try"
            
 
            # print("\ntry\n")
            settings = collection_settings.find_one({'username': username})
            topic = settings['topic']
            no_of_questions = int(settings['no_of_questions'])
            no_of_choices = int(settings['no_of_choices'])

            mapped_questions = generate_mapped_questions_from_db(collection = collection_qna_bank, topic=topic, username = username, no_of_questions=no_of_questions, no_of_choices=no_of_choices)
            
            try:
                # Delete the entry then insert
                collection_temp.delete_one({"username":username})
            except:
                pass
        
            collection_temp.insert_one({"username": username, "temp_qna_bank" : mapped_questions})

            return render_template('quiz_new.html', mapped_questions = mapped_questions, username = username)   
            
            
        elif request.method == 'POST':
            if request.form["quiz_submit_button"]:
                # Used to check what answers were given
                chosen_answers = request.form.to_dict()

                # This will give "None" if there was no answer given for a particular index.
                chosen_answers_list =[]

                mapped_questions = reload_questions_from_db(collection = collection_temp, username=username)['temp_qna_bank']

                correct_answers = correct_answers_from_db(collection = collection_temp, username=username)
                
                # For scoring
                no_of_correct_answers = 0
                no_of_questions = len(mapped_questions)
                
                # List of correct or wrong answers. Follows the order of the mapped_questions.
                correct_or_wrong_list = []
                for QNCA in correct_answers:
                    # Correct answer
                    try:
                        correct_answer = QNCA.correct_a 
                        chosen_answer = chosen_answers[QNCA.question]
                        chosen_answers_list.append(chosen_answer)
                        if chosen_answer == correct_answer:
                            correct_or_wrong_list.append("Correct!")
                            no_of_correct_answers += 1
                        else:
                            correct_or_wrong_list.append("Wrong!")
                    except KeyError:
                        correct_or_wrong_list.append("No answer provided!")
                        chosen_answers_list.append("None")
                percentage_score = round((no_of_correct_answers / no_of_questions) * 100, 2)
                return render_template('quiz_submitted.html', mapped_questions = mapped_questions, correct_answers = correct_answers, no_of_correct_answers = no_of_correct_answers, no_of_questions = no_of_questions, correct_or_wrong_list = correct_or_wrong_list, chosen_answers = chosen_answers, chosen_answers_list=chosen_answers_list, percentage_score = percentage_score, username = username)

    
@app.route('/quiz_settings', methods = ['GET', 'POST'])
def quiz_settings():
    """Set topic, number of questions and number of choices for quiz."""
    if not session.get('logged_in'):
        return redirect('/login')
    else:
        username = session['user_id']
        if request.method == 'GET':
            topics = sorted((collection_qna_bank.distinct('topic', {'username':username})))
            
            return render_template('quiz_settings.html', topics=topics, username = username) 
        elif request.method == 'POST':
            
            if request.form["quiz_topic_button"]:
                
                settings = request.form.to_dict()
                topic = settings['topic']
                no_of_questions = int(settings['no_of_questions'])
                no_of_choices = int(settings['no_of_choices'])

                mapped_questions = generate_mapped_questions_from_db(collection=collection_qna_bank, topic=topic, username = username, no_of_questions= no_of_questions, no_of_choices=no_of_choices)
                
                # collection_temp will be used as the temporary QnA bank for different users.
                try:
                    collection_temp.delete_one({"username":username})
                except:
                    pass
                
                collection_temp.insert_one({"username":username, "temp_qna_bank": mapped_questions})
                
                try:
                    collection_settings.delete_one({'username':username})
                except:
                    pass

                collection_settings.insert_one({'username':username, 'topic':topic, 'no_of_questions':no_of_questions, 'no_of_choices':no_of_choices})
                
                session['settings_set'] = True
                return render_template('quiz_new.html', mapped_questions = mapped_questions, username = username)   
                #TODO create new json file for different users

@app.route('/quiz_add_questions', methods = ['GET', 'POST'])
def quiz_add_questions():
    """Add a new question."""
    if not session.get('logged_in'):
        return redirect('/login')
    else:
        username = session['user_id']
        if request.method == 'GET':

            topics = sorted((collection_qna_bank.distinct('topic', {'username':username})))

            if collection_settings.find_one({'username':username}) is None:
                # To track whether there are any settings. Otherwise, hide the button which says "New Quiz (Last Used Settings)"
                session['settings_set'] = False
            else:
                session['settings_set'] = True   

            return render_template('quiz_add_questions.html', topics=topics, questions = session['questions'], settings= session['settings_set'],username = username) 
        elif request.method == 'POST':
            # Adds a new question and/or topics to the existing JSON file. 
            
            if request.form["add_new_questions"]:
                new_questions = request.form.to_dict()
                
                if new_questions['topic'] == 'NEW_TOPIC':
                    new_topic = new_questions['add_new_topic'].lower()
                    new_question = new_questions['new_question']
                    new_answer = new_questions['new_answer']
                else: 
                    new_topic = new_questions['topic'].lower()
                    new_question = new_questions['new_question']
                    new_answer = new_questions['new_answer']

                collection_qna_bank.insert_one({'username': username,'topic':new_topic, 'question':new_question, 'answer': new_answer})
  
                # To regenerate add_questions.html page with the new topic included
                topics = sorted((collection_qna_bank.distinct('topic', {'username':username})))

                session['questions'] = True

                if collection_settings.find_one({'username':username}) is None:
                # To track whether there are any settings. Otherwise, hide the button which says "New Quiz (Last Used Settings)"
                    session['settings_set'] = False
                else:
                    session['settings_set'] = True    

                return render_template('quiz_questions_added.html', topics=topics, new_topic=new_topic,new_question=new_question,new_answer=new_answer, questions = session['questions'], settings= session['settings_set'], username = username)
        
