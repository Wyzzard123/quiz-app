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

# @app.route('/error', methods = ['GET'])
# def error():
#     """Renders an error page."""
    
#     return render_template('error.html', errorstring = "Error")

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
            return render_template("error.html", errorstring = "No such user!")

        elif not pbkdf2_sha256.verify(password, matching_entry['password']):
            print("invalid password")
            
            return render_template("error.html", errorstring = "Invalid password")
        elif pbkdf2_sha256.verify(password, matching_entry['password']):
            session['logged_in'] = True 
            session['user_id'] = username
            print(session)
            return redirect('/quiz_settings')


        

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
            
            return render_template("error.html", errorstring = "User already exists!")
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
        if request.method == 'GET':
            # If there is a settings page, go through "try"
            
            try:
                settings_file = "quiz_settings.json"

                with open(settings_file, "r") as settingsfile:
                    settings = json.load(settingsfile)
                topic = settings['topic']
                no_of_questions = int(settings['no_of_questions'])
                no_of_choices = int(settings['no_of_choices'])

                mapped_questions = generate_mapped_questions_from_file(topic=topic, infile="question_answer_bank.json", no_of_questions=no_of_questions, no_of_choices=no_of_choices)
                
                
                temp_json_file = "temporary_question_answer_bank.json"

                with open(temp_json_file, "w") as tempfile:
                    json.dump(mapped_questions, tempfile)

                return render_template('quiz_new.html', mapped_questions = mapped_questions)   
            
            # Otherwise (eg if the website is accessed for the first time without going through the settings page), go through the default parameters in "except"
            except:
                mapped_questions = generate_mapped_questions_from_file(topic="nature", infile="question_answer_bank.json", no_of_questions=6, no_of_choices=4)
                
                temp_json_file = "temporary_question_answer_bank.json"

                with open(temp_json_file, "w") as tempfile:
                    json.dump(mapped_questions, tempfile)

                return render_template('quiz_new.html', mapped_questions = mapped_questions)
        elif request.method == 'POST':
            if request.form["quiz_submit_button"]:
                # Used to check what answers were given
                chosen_answers = request.form.to_dict()

                # This will give "None" if there was no answer given for a particular index.
                chosen_answers_list =[]

                mapped_questions = reload_questions_from_json()
                correct_answers = correct_answers_from_json()
                
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
                return render_template('quiz_submitted.html', mapped_questions = mapped_questions, correct_answers = correct_answers, no_of_correct_answers = no_of_correct_answers, no_of_questions = no_of_questions, correct_or_wrong_list = correct_or_wrong_list, chosen_answers = chosen_answers, chosen_answers_list=chosen_answers_list, percentage_score = percentage_score)

    
@app.route('/quiz_settings', methods = ['GET', 'POST'])
def quiz_settings():
    """Set topic, number of questions and number of choices for quiz."""
    if not session.get('logged_in'):
        return redirect('/login')
    else:
        if request.method == 'GET':
            infile = "question_answer_bank.json"

            with open(infile) as json_file:
                file_data = json.load(json_file)

            topics = sorted(file_data.keys())
            return render_template('quiz_settings.html', topics=topics) 
        elif request.method == 'POST':
            
            if request.form["quiz_topic_button"]:
                
                settings = request.form.to_dict()
                topic = settings['topic']
                no_of_questions = int(settings['no_of_questions'])
                no_of_choices = int(settings['no_of_choices'])

                mapped_questions = generate_mapped_questions_from_file(topic=topic, infile="question_answer_bank.json", no_of_questions=no_of_questions, no_of_choices=no_of_choices)
                
                
                temp_json_file = "temporary_question_answer_bank.json"

                with open(temp_json_file, "w") as tempfile:
                    json.dump(mapped_questions, tempfile)

                settings_file = "quiz_settings.json"

                with open(settings_file, "w") as settingsfile:
                    json.dump(settings, settingsfile)

                return render_template('quiz_new.html', mapped_questions = mapped_questions)   
                #TODO create new json file for different users

@app.route('/quiz_add_questions', methods = ['GET', 'POST'])
def quiz_add_questions():
    """Add a new question."""
    if not session.get('logged_in'):
        return redirect('/login')
    else:
        if request.method == 'GET':
            infile = "question_answer_bank.json"

            with open(infile) as json_file:
                file_data = json.load(json_file)

            topics = sorted(file_data.keys())
            return render_template('quiz_add_questions.html', topics=topics) 
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

                infile = "question_answer_bank.json"
                
                with open(infile) as json_file:
                    file_data = json.load(json_file)
                
                question_answer_bank = get_questions(infile)

                QA = namedtuple('QA', 'question answer')
                question_answer_tuple = QA(question = new_question, answer = new_answer)
                question_answer_bank[new_topic].append(question_answer_tuple)

                store_json(question_answer_bank, infile)


                
                # To regenerate add_questions.html page with the new topic included
                with open(infile) as json_file:
                    file_data = json.load(json_file)
                topics = sorted(file_data.keys())


                return render_template('quiz_questions_added.html', topics=topics, new_topic=new_topic,new_question=new_question,new_answer=new_answer)
        
