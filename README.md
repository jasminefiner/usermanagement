# Flask User Management System
This repository contains code for a user management system built in Flask. I built this partly as a way of learning how the Flask framework works, and also so I didn't have to repeat the same code when building different apps that each required user management systems.

## Installation and setup
### Clone the repository

```
$ git clone https://github.com/jasminefiner/usermanagement.git`
$ cd usermanagement
```

### Initialise the virtual environment

```
$ python3 -m venv venv
$ . venv/bin/activate
```

### Add environment variables
Environment variables need to be specified so that flask knows where to look for your application, for setting up the email functionality and for storing database & encryption information. The ones below do not have default values. Other environment variables are specified in `config.py` and have default valuse. However, you can change them if you wish.
*Note: If you store these variables inside a .env file, then remember not to include them in commits - they need to be private.*
```
$ export FLASK_APP='usermanagement.py'
$ export FLASK_DEBUG=True
$ export SECRET_KEY='some_very_random_string'
$ export MAIL_USERNAME=<gmail-username>
$ export MAIL_PASSWORD=<gmail-password>
```

### Install the dependencies
```
$ pip install -r requirements.txt
```

### Initalise the database
```
$ flask db init
$ flask db migrate -m 'some commit message'
$ flask db upgrade
```

## Running the application
Make sure you have activated the virtual environment and exposed all the environment variables before this step.
```
$ flask run
```

## Testing the application
Testing is done with python's `unittest` package and can be initialised with a cli command.
```
$ flask test
```
## Final thoughts
Feedback is always welcome on these projects. If you find any bugs or code that could be written better then feel free to let me know by creating a new issue or sending me an email.
