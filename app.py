from flask import Flask, render_template, request, redirect
from poc import *
app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def index():
    return redirect('/quiz')

@app.route('/quiz', methods = ['GET', 'POST'])
def quiz():
    if request.method == 'GET':
        mapped_questions = generate_mapped_questions_from_file()
        print(mapped_questions)
        return render_template('quiz.html', mapped_questions = mapped_questions)
    elif request.method == 'POST':
        # if request.form["quiz_submit_button"]
        mapped_questions = generate_mapped_questions_from_file()
        return render_template('quiz.html', mapped_questions = mapped_questions)

    
    
