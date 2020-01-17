"""Refactoring Proof of Concept (poc.py) code to use MongoDB instead of JSON files."""
import os
from pymongo import MongoClient
from poc import *
from pprint import pprint


if __name__ == "__main__":
    # You will need your own MongoDB Database and environment variables to implement this.
    db_user = os.environ.get('QUIZDB_USER')
    db_password = os.environ.get('QUIZDB_PASSWORD')


    connection_string = f"mongodb+srv://{db_user}:{db_password}@quizapp1-phe85.mongodb.net/test?retryWrites=true&w=majority"

    client = MongoClient(connection_string)

    # Placeholder username. Community questions should be available to all.
    username = "community"

    quiz_db = client.quiz_app
    collection_qna_bank = quiz_db.question_answer_bank
    collection_settings = quiz_db.quiz_settings

    pprint(list(collection_qna_bank.find({'topic':'colours'}, {'_id':0,'question':1, 'answer':1})))
    pprint(list(collection_settings.find()))
   
