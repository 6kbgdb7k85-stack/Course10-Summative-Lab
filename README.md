# Course10-Summative-Lab

## Description
Personal Notes app backend for Course 10 summative lab

## Setup
- clone repo
- run pipenv install
- run pipenv shell
- navigate to server directory
- run export FLASK_APP=app.py
- run export FLASK_RUN_PORT=5555
- run flask db upgrade
- run python seed.py
    - passwords for test users are username+'password'

## Usage
- run pipenv shell if not already in pipenv shell
- navigate to server directory if not already there
- within pipenv environment run python app.py
- use Postman to test endpoints

## Features/Endpoints
- /signup
    - POST: create new user with input username and password and return jwt auth token to log in the new user
- /login
    - POST: return jwt auth token to log in existing user
- /me
    - GET: check for jwt auth token to ensure user is logged in
- /notes
    - GET: return paginated list of notes owned by the user
        - page and per_page default to 1 and 5 respectively
    - POST: create new note with input data
- /notes/:note_id
    - GET: return details of the note
    - PATCH: update note details from input data
    - DELETE: remove note from database