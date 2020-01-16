from flask import Flask, render_template, request, redirect
from poc import *
import json
app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def index():
    return redirect('/quiz_settings')

@app.route('/quiz', methods = ['GET', 'POST'])
def quiz():
    """Randomly generates quizzes and shows the answer/score after submitting."""
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
def topic():
    """Set topic, number of questions and number of choices for quiz."""
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
