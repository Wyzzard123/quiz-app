"""Importing JSON files into MongoDB database."""
import os
from pymongo import MongoClient
from poc import *

# You will need your own MongoDB Database and environment variables to implement this.
db_user = os.environ.get('QUIZDB_USER')
db_password = os.environ.get('QUIZDB_PASSWORD')


connection_string = f"mongodb+srv://{db_user}:{db_password}@quizapp1-phe85.mongodb.net/test?retryWrites=true&w=majority"

client = MongoClient(connection_string)

# Placeholder username. Community questions should be available to all.
username = "community"

quiz_db = client.quiz_app
collection_qna_bank = quiz_db.question_answer_bank
with open("question_answer_bank.json", "r") as json_file:
    question_answer_bank = json.load(json_file)

"""Importing QNA Bank into Database"""
# for topic, questions in question_answer_bank.items():
#     for QNA_pair in questions:
#         question = QNA_pair[0]
#         answer = QNA_pair[1]
#         qna_document = {
#             'username': username,
#             'topic': topic,
#             'question': question, 'answer':answer
#         }
#         collection_qna_bank.insert_one(qna_document)
# client.close()

"""Importing User Settings into Database"""
# with open("quiz_settings.json", "r") as settings_file:
#     quiz_settings = json.load(settings_file)

# topic = quiz_settings["topic"]
# no_of_questions = quiz_settings["no_of_questions"]
# no_of_choices = quiz_settings["no_of_choices"]

# settings = {
#     'username': username,
#     'topic' : topic,
#     'no_of_questions' : no_of_questions,
#     'no_of_choices' : no_of_choices}

# collection_settings = quiz_db.quiz_settings
# collection_settings.insert_one(settings)
