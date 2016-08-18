
studiobooking
=============

A small flask app written to facilitate booking out practice/pre-recording/interview time of URN studio's.

Setup
-----

* Install requirements

    pip install -r requirements.txt

* Change the secret key and admin password

    cp settings.example.py settings.py
    vim settings.py

* Initialise the database

    python createdb.py

* Run

    python studiobooking.py

* Browse to

    http://localhost:5000

In production however this should definitely be served behind nginx or similar, and with a WSGI server (e.g. gunicorn)
