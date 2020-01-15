"""This is a proof of concept for the quiz, sans the webpage"""
from collections import namedtuple, defaultdict, deque
import json
import random

#########Section 1: CREATE QUESTION AND ANSWER BANK#######################################

def store_json(question_answer_bank, outfile_json='question_answer_bank.json'):
    """Stores the question answer bank as a JSON file."""

    # This will overwrite the JSON file. Make sure that the input_questions function takes the output of get_questions first.
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

def input_questions():
    """A simple function that takes user input for questions and adds the questions to the question_answer_bank. This separates questions and answers by topic.
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
        try:
            for QA_tuple in question_answer_bank:
                print(f"Question: {QA_tuple.question}")
                print(f"Answer: {QA_tuple.answer}")
                print("")
        except AttributeError:
            # Try this for when a list of mapped QnA with choices is added
            for index, choices_dict in enumerate(question_answer_bank):
                for choice, value in choices_dict.items():
                    if choice == "question":
                        print(f"\nQuestion {index + 1}: {choices_dict['question']}")
                    else:
                        print(f"{choice}: {value.answer}")
                    
    print(endstring)

## Uncomment to test Code to create questions and answers
# initial_question_answer_bank = get_questions()
# print_questions(initial_question_answer_bank, "New list")

# question_answer_bank = input_questions()

# print_questions(question_answer_bank)

#########Section 2: Generate Random Questions#######################################

def generate_qna_from_file(topic="usa", infile='question_answer_bank.json', no_of_questions=5, no_of_choices=4):
    """Generates a list of MCQ questions from the question_answer_bank JSON file for a particular topic and no_of_questions. The number of choices is set to 4 by default."""
    question_answer_bank = get_questions(infile)
    qna_bank_topic = question_answer_bank[topic]
    
    # Check that the number of questions is not more than the number of questions available for the given topic. If it is, update the number of questions accordingly.
    if no_of_questions > len(qna_bank_topic):
        no_of_questions = len(qna_bank_topic)

    # To be returned
    list_of_qnc = []

    # To keep track of to ensure we do not get the same question repeated
    list_of_qa_tuples = []

    # Create a set of answers to generate choices from
    set_of_answers = set(QA_tuple.answer for QA_tuple in qna_bank_topic)

    # Also creating a list to make it easier to generate random choices later
    list_of_answers = list(set_of_answers)

    # If the number of choices is more than the answers we have available, lower the number of choices.
    if no_of_choices > len(set_of_answers):
        no_of_choices = len(set_of_answers)
    
    for no in range(no_of_questions):
        # Add a random QA tuple to the list of questions. The while loop checks that the QA tuple has not already been inserted.
        while (random_QA := random.choice(qna_bank_topic)) in list_of_qa_tuples:
            random_QA = random.choice(qna_bank_topic)
        list_of_qa_tuples.append(random_QA)
        
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
        list_of_qnc.append(new_QNC)
    
    return list_of_qnc
   
## Uncomment to test generate_qna_from_file()
# random_questions = generate_qna_from_file()
# print_questions(random_questions)
# print(random_questions)


#########Section 3: Generate a Quiz from the list#######################################

def map_to_choice(QNC_tuple):
    """This maps a question to A, B, C, D, using QNC (Question and Choices) Tuple output from the generate_qna_from_file function. Returns a dictionary with A, B, C, D as the keys and choices as the values. The values are tuples which contain a correctorwrong answer, which will be 'correct' for the right answer or 'wrong' for the wrong choices. The question is also a key value pair."""
    question, answer, incorrect_choices = QNC_tuple
    
    # Make a named tuple showing whether something is correct or wrong
    CorW = namedtuple("CorW", "answer correctorwrong")
    right_answer = CorW(answer=answer, correctorwrong="correct")
    choices = [right_answer] 
    for incorrect_choice in incorrect_choices:
        wrong_answer = CorW(answer=incorrect_choice, correctorwrong="wrong")
        choices.append(wrong_answer)
    
    # Shuffle the Choices list in place
    random.shuffle(choices)
    choices_dict = {}
    choices_dict['question'] = question

    ascii_A_no = ord("A")
    for index, choice in enumerate(choices):
        letter = chr(ascii_A_no + index)
        choices_dict[letter] = choice
    return choices_dict

## Uncomment to test map_to_choice functionality
# random_questions = generate_qna_from_file()
# # print(random_questions)
# print(map_to_choice(random_questions[0]))

def generate_mapped_questions_from_file(topic="usa", infile='question_answer_bank.json', no_of_questions=5, no_of_choices=4):
    """Generates a full list of questions and choices from a json file. Takes as parameters the file where the questions and answers are stored (JSON), the number of questions, the number of choices per question, and the topic.""" 

    list_of_qnc = generate_qna_from_file(topic, infile, no_of_questions, no_of_choices)

    # This is a list of the QnA to later be called by index number.
    list_of_mapped_qna = []

    for QNC_tuple in list_of_qnc:
        choices_dict = map_to_choice(QNC_tuple)
        list_of_mapped_qna.append(choices_dict)

    return list_of_mapped_qna

## Use this to test mapped_questions functionality

# input_questions()

# list_of_mapped_qna = generate_mapped_questions_from_file(topic="malaysia")

# for item in list_of_mapped_qna:
#     print(item)

# print_questions(list_of_mapped_qna)

def generate_quiz(list_of_mapped_qna):
    """Generates a quiz that takes user input for answers. The questions take the list_of_mapped_qna output from the generate_mapped_questions_from_file function as input. Similar to the print_questions function, but with pauses to allow for user input. Returns a score."""
    
    max_score = len(list_of_mapped_qna)
    score = 0
    
    for index, choices_dict in enumerate(list_of_mapped_qna):
        # The correct answer is the answer where correctorwrong is "correct"
        correct_answer = ""
        
        # choices are the choices n the question.
        set_of_choices = set()
        for choice, value in choices_dict.items():
            if choice == "question":
                print(f"\nQuestion {index + 1}: {choices_dict['question']}")
            else:
                print(f"{choice}: {value.answer}")
                set_of_choices.update([choice])
                if value.correctorwrong == 'correct':
                    correct_answer = choice
        
        given_answer = input("Type your answer here:\n")
        while given_answer not in set_of_choices:
            given_answer = input("Type your answer here FROM THE CHOICES (letters):\n")
        if given_answer.lower() == correct_answer.lower():
            print("Correct!")
            score += 1
        else:
            print(f"Wrong! The answer was {correct_answer}!")
    print(f"Your final score was {score} / {max_score}")
    return score
        
# list_of_mapped_qna = generate_mapped_questions_from_file(topic="usa")
# generate_quiz(list_of_mapped_qna)                  

def instant_quiz(topic="usa", infile='question_answer_bank.json', no_of_questions=5, no_of_choices=4):
    """Generate an instant quiz from a file"""
    list_of_mapped_qna = generate_mapped_questions_from_file(topic, infile, no_of_questions, no_of_choices)
    score = generate_quiz(list_of_mapped_qna)
    return score


# # Uncomment to test out quiz capabilities
# instant_quiz(topic="usa", infile='question_answer_bank.json', no_of_questions=5, no_of_choices=4)


####### Added while making Flask app. To take a temp QnA bank which was randomly generated and to map the questions to the correct answers. #################################
def correct_answers_from_json(infile='temporary_question_answer_bank.json'):
    """Creates a list of tuples from a temporary mapped JSON with the questions and the correct answer choices.""" 

    with open(infile) as json_file:
        json_mapped_questions = json.load(json_file)
    
    list_of_q_and_correct_a = []

    #QNCA is Question and Correct Answer
    QNCA = namedtuple("QNCA", 'question correct_a')

    for QNC in json_mapped_questions:
        question = QNC["question"]
        correct_answer = ""
        for choice, answer in QNC.items():
            if choice == "question":
                continue
            elif answer[1] == "wrong":
                continue
            elif answer[1] == "correct":
                correct_answer = choice
        q_and_correct_a = QNCA(question=question, correct_a=correct_answer)
        
        list_of_q_and_correct_a.append(q_and_correct_a)
    
    return list_of_q_and_correct_a

## Uncomment to test remapping to correct answer choice/letter
# print(correct_answers_from_json())

def reload_questions_from_json(infile = 'temporary_question_answer_bank.json'):
    """Reloads a temporary mapped JSON to recreate an HTML page with the same questions (after submission)."""

    with open(infile) as json_file:
        json_mapped_questions = json.load(json_file)

    return json_mapped_questions
