# Random Quiz Generator

In order to prepare for exams and professional certifications (which generally follow an MCQ format), I wished to have an easy-to-use software to test myself with. However, writing the questions and all the different choices would make the test useless for me, as I would instantly know which choices were wrong.

Enter the Random Quiz Generator, which takes care of coming up with the different choices for you. Instead of coming up with choices, you need only type in the questions and correct answers. The Random Quiz Generator will spin up the other choices from the database of other answers that you have keyed in.

As of 18/01/2020, the app has been deployed onto Heroku at https://wyz-quiz-app.herokuapp.com/. It currently supports user accounts, adding new topics and questions, changing settings (topic, number of questions and number of choices for each question), randomly generating questions for a given topic and immediate feedback.

To test out the app, feel free to use this account which was meant to provide a common pool of quiz questions:

```
Username: community
Password: admin
```
Set the topic to "Nature" for actual quiz questions. The topic "USA" is there for testing purposes, but the quiz answers themselves are nonsense.


## Getting Started

The app consists of app.py, a poc.py module (proof of concept) which contains various helper functions, and the templates. 

### Prerequisites

To run the software, you will need Python 3.8.1, as the new walrus operator (":=") has been used. See runtime.txt (which you will need if deploying to Heroku.)

You will also need to set three environment variables on your system, representing a MongoDB database key, a MongoDB password and a randomly generated secret key (for Flask sessions). You can also set these as config vars in Heroku.

Assuming you have pip installed, all other prerequisites can be installed using the following code:
```
pip install -r requirements.txt
```

Remember to add any other requirements later on by typing:

```
pip freeze > requirements.txt
```

It is recommended that you use a virtual environment. See https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/

### Deploying onto Heroku

To deploy this app onto Heroku, you have to set your config vars as stated above.

The Procfile will take care of telling Heroku that this is a web-app, and to listen on whatever port that Heroku sets.
```
web: gunicorn -b :$PORT app:app
```

Heroku also requires "requirements.txt" and "runtime.txt" to tell it what versions of the software to use.


## Tests

```
#TODO
```


## Versioning

```
#TODO
```

## Outstanding Tasks

```
#TODO
```

To make this app even better, this app needs (feel free to add more):
1. The ability to add and delete questions.
2. The ability to share questions with other users.
3. More robust security for passwords and user data.
4. Optimizing the code to make it run faster, especially when more data is added.

## Other Notes

Many of the helper functions in poc.py are there because this program was originally made to use JSON instead of MongoDB. These were then refactored to use MongoDB.

The JSON files can also be ignored for the same reason, but they could be useful for testing. In fact, using the flask app locally with JSON is probably much faster than using the web-app at the moment.

## Author

* **Wyz Kim-Chan** - *Initial work* - https://wyz-quiz-app.herokuapp.com/


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
