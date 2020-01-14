"""This is a proof of concept for the quiz, sans the webpage"""
from collections import namedtuple, defaultdict, deque
import json
import random

#########Section 1: CREATE QUESTION AND ANSWER BANK#######################################

def store_json(question_answer_bank, outfile_json='question_answer_bank.json'):
    """Stores the question answer bank as a JSON file."""

    # This will overwrite the JSON file. Make sure that the make_questions function takes the output of get_questions first.
    with open(outfile_json, "w") as outfile:
        json.dump(question_answer_bank, outfile)

# This will store questions and answers and map them to each other

def get_questions(infile='question_answer_bank.json'):
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
    # Convert back to an ordinary dictionary for storage as a JSON
    question_answer_bank_dict = dict(question_answer_bank)
    
    # Stores the data as a JSON file so it can persist.
    store_json(question_answer_bank)
    return question_answer_bank


def print_questions(question_answer_bank, startstring="", endstring=""):
    """Loops over the questions in the question bank and prints. Takes as arguments a startstring and an endstring. The question_answer_bank can be a dict or a list."""
    print(startstring)
    if type(question_answer_bank) == defaultdict or type(question_answer_bank) == dict:
        for topic, tuple_list in question_answer_bank.items():
            print(f"Topic: {topic}")
            for QA_tuple in tuple_list:
                print(f"Question: {QA_tuple.question}")
                print(f"Answer: {QA_tuple.answer}")
                print("")
    elif type(question_answer_bank) == list:
        for QA_tuple in question_answer_bank:
            print(f"Question: {QA_tuple.question}")
            print(f"Answer: {QA_tuple.answer}")
            print("")
    print(endstring)

## Uncomment to test Code in first section
# initial_question_answer_bank = get_questions()
# print_questions(initial_question_answer_bank, "New list")

# question_answer_bank = make_questions()

# print_questions(question_answer_bank)

#########Section 2: Generate Random Questions#######################################

def generate_qna_from_file(infile='question_answer_bank.json', no_of_questions=5, no_of_choices=4, topic="usa"):
    """Generates a list of MCQ questions from the question_answer_bank JSON file for a particular topic and no_of_questions. The number of choices is set to 4 by default."""
    question_answer_bank = get_questions(infile)
    qna_bank_topic = question_answer_bank[topic]
    
    # Check that the number of questions is not more than the number of questions available for the given topic. If it is, update the number of questions accordingly.
    if no_of_questions > len(qna_bank_topic):
        no_of_questions = len(qna_bank_topic)

    list_of_qna = []

    # Create a set of answers to generate choices from
    set_of_answers = set(QA_tuple.answer for QA_tuple in qna_bank_topic)

    # Also creating a list to make it easier to generate random choices later
    list_of_answers = list(set_of_answers)

    # If the number of choices is more than the answers we have available, lower the number of choices.
    if no_of_choices > len(set_of_answers):
        no_of_choices = len(set_of_answers)
    
    for no in range(no_of_questions):
        # Add a random QA tuple to the list of questions. The while loop checks that the QA tuple has not already been inserted.
        while (random_QA := random.choice(qna_bank_topic)) in list_of_qna:
            random_QA = random.choice(qna_bank_topic)
        # Create a named tuple with the question, answer, and a list of wrong choices
        QNC = namedtuple("QNC", 'question answer incorrect_choices')
        # Correct choice is index 0.
        choices = deque([random_QA.answer])

        # Randomly generate incorrect choices
        for num in range(no_of_choices - 1):
            while (choice := random.choice(list_of_answers)) in choices:
                choice = random.choice(list_of_answers)
            choices.append(choice)
        # Take out incorrect choice
        choices.popleft()
        incorrect_choices = list(choices)

    
        new_QNC = QNC(question=random_QA.question, answer=random_QA.answer, incorrect_choices = incorrect_choices)
        list_of_qna.append(new_QNC)
    
    return list_of_qna
   
## Uncomment to test Code in second section
# random_questions = generate_qna_from_file()
# print_questions(random_questions)
# print(random_questions)


#########Section 3: Generate a Quiz from the list#######################################