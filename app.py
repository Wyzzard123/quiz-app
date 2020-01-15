from flask import Flask, render_template, request, redirect
from poc import *
import json
app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def index():
    return redirect('/quiz')

@app.route('/quiz', methods = ['GET', 'POST'])
def quiz():
    if request.method == 'GET':
        mapped_questions = generate_mapped_questions_from_file(topic="nature", infile="question_answer_bank.json", no_of_questions=6, no_of_choices=4)
        print(mapped_questions)
        
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

    
    
