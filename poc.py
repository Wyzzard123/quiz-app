"""This is a proof of concept for the quiz, sans the webpage"""
from collections import namedtuple, defaultdict
import json

def store_json(question_answer_bank):
    """Stores the question answer bank as a JSON file."""

    # This will overwrite the JSON file. Make sure that the make_questions function takes the output of get_questions first.
    with open("question_answer_bank.txt", "w") as outfile:
        json.dump(question_answer_bank, outfile)

# This will store questions and answers and map them to each other

def get_questions(infile='question_answer_bank.txt'):
    """This reads questions and answers from the JSON file we have."""
    question_answer_bank = defaultdict(lambda: [])
    with open(infile) as json_file:
        file_data = json.load(json_file)

        # Convert from json list of lists of two to Topic: Question Answer Tuples
        for topic, list_list in file_data.items():
            for lst in list_list:
                QA = namedtuple('QA', 'question answer')
                question_answer_tuple = QA(question = lst[0], answer = lst[1])
                question_answer_bank[topic].append(question_answer_tuple)
    question_answer_bank = dict(question_answer_bank)
    return question_answer_bank

def make_questions():
    """A simple function that takes questions and adds them to the question_answer_bank. This separates questions and answers by topic.
    For the actual app, this will be done through a webform, and questions which were added previously
    will persist."""
    # User will input questions and answers. User may type "quit" at any time to break out of the loop.
    question_answer_bank = defaultdict(lambda: [])

    #Question and Answer Bank will use the questions that are already stored
    question_answer_bank.update(get_questions())
    while True:
        # Uses .lower() to prevent duplicates of a topic
        topic = input("Type the TOPIC or 'QUIT': ").lower()
        if topic.lower() == "quit":
            break
        
        question = input("Type your QUESTION or 'QUIT': ")
        if question.lower() == "quit":
            break
        answer = input("Type the ANSWER or 'QUIT': ")
        if answer.lower() == "quit":
            break
        
        QA = namedtuple('QA', 'question answer')
        question_answer_tuple = QA(question = question, answer = answer)
        question_answer_bank[topic].append(question_answer_tuple)
    # Convert back to an ordinary dictionary to make the dict easier to handle
    question_answer_bank = dict(question_answer_bank)
    
    # Stores the data as a JSON file so it can persist.
    store_json(question_answer_bank)
    return question_answer_bank


def print_questions(question_answer_bank, startstring="", endstring=""):
    print(startstring)
    for topic, tuple_list in question_answer_bank.items():
        print(f"Topic: {topic}")
        for QA_tuple in tuple_list:
            print(f"Question: {QA_tuple.question}")
            print(f"Answer: {QA_tuple.answer}")
    print(endstring)

initial_question_answer_bank = get_questions()
print_questions(initial_question_answer_bank, "New list")

question_answer_bank = make_questions()

print_questions(question_answer_bank)
