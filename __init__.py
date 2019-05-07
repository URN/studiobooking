#!/usr/bin/env python3

from flask import Flask, render_template, request, jsonify, Response
from flask_wtf import Form
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, DateField, SelectField, \
    HiddenField, SubmitField, PasswordField
from datetime import datetime, timedelta
import time
from json import dumps
from functools import wraps

import settings

app = Flask(__name__)
app.config['SECRET_KEY'] = settings.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
app.config['CALENDAR_COLORS'] = settings.CALENDAR_COLORS

db = SQLAlchemy(app)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    contact = db.Column(db.String(120))
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    studio = db.Column(db.Integer)

    def as_dict(self):
        start = self.start.strftime('%Y-%m-%d %H:%M:%S')
        end = self.end.strftime('%Y-%m-%d %H:%M:%S')
        color = app.config['CALENDAR_COLORS'][self.studio]
        if request.authorization:
            title = '%s (%s)' % (self.name, self.contact)
        else:
            title = self.name
        return {'id': self.id,
                'title': title,
                'name': self.name,
                'contact': self.contact,
                'studio': self.studio,
                'start': start,
                'end': end,
                'allDay': False,
                'color': color}

    def __init__(self, name, contact, start, end, studio=0):
        self.name = name
        self.contact = contact
        self.start = start
        self.end = end
        self.studio = studio

    def __repr__(self):
        return '<Booking %r by %r>' % (self.id, self.name)


class BookingForm(Form):
    start = HiddenField()
    name = StringField('Name')
    contact = StringField('Contact')
    date = StringField('Date')
    time = DateField('Starting time')
    duration = StringField('Duration')
    studio = SelectField('Studio',
                         choices=[(0, 'Either'),
                                  (1, 'Studio 1'),
                                  (2, 'Studio 2')],
                         coerce=int)
    submit = SubmitField('Submit')


class LoginForm(Form):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Login')


def check_for_clashes(start, end):
    start = start + timedelta(seconds=1)
    end = end - timedelta(seconds=1)
    print(start)
    print(end)
    if Booking.query.filter(Booking.start.between(start, end)).count() > 0:
        return False
    if Booking.query.filter(Booking.end.between(start, end)).count() > 0:
        return False
    return True


def check_auth(username, password):
    return username == 'admin' and password == settings.PASSWORD


def authenticate():
    return Response('Login!', 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


@app.route('/admin', methods=['GET'])
@requires_auth
def admin():
    form = BookingForm(request.form)
    return render_template('admin.htm', form=form, colors=app.config['CALENDAR_COLORS'])


@app.route('/edit/<int:id>', methods=['POST'])
@requires_auth
def edit_booking(id):
    form = BookingForm(request.form)
    message = {}
    message['text'] = 'Submitted!'
    return render_template('booking_response.htm')


@app.route('/delete/<int:id>', methods=['GET'])
@requires_auth
def delete_booking(id):
    booking = Booking.query.filter(Booking.id == id).first()
    db.session.delete(booking)
    db.session.commit()
    message = {}
    message['text'] = "Deleted booking by " + booking.name
    message['alert'] = 'alert alert-success'
    return render_template('booking_response.htm', message=message)


@app.route('/booking', methods=['GET', 'POST'])
def make_booking():
    form = BookingForm(request.form)
    if request.method == 'POST':
        start = form.start.data
        start = datetime.strptime(form.start.data,
                                  '%a, %d %b %Y %H:%M:%S %Z')
        # TODO: don't do this weird dst stuff
        # better idea to store all times as UTC
        # and render based on users timezone
        if time.localtime().tm_isdst > 0:
            start = start + timedelta(hours=1)
        start = start.replace(tzinfo=None)
        end = datetime.strptime(form.duration.data, '%I:%M%p').time()
        end = datetime.combine(start.date(), end)
        # start = start.strftime('%s')
        # end = end.strftime('%s')
        message = {}
        if check_for_clashes(start, end):
            # booking = Booking(form.name.data, form.date.data)
            booking = Booking(form.name.data, form.contact.data,
                              start,
                              end, form.studio.data)
            db.session.add(booking)
            db.session.commit()
            message['text'] = 'Submitted!'
            message['alert'] = 'alert alert-success'
        else:
            message['text'] = 'Error: Your booking clashes \
                               with a previous booking'
            message['alert'] = 'alert alert-error'
        return render_template('booking_response.htm', message=message)
    return render_template('booking_form.htm', form=form)


@app.route('/events')
def get_events():
    start = datetime.fromtimestamp(float(request.args['start']))
    end = datetime.fromtimestamp(float(request.args['end']))
    events = Booking.query.filter(Booking.start.between(start, end)).all()
    data = list(map(lambda x: x.as_dict(), events))
    return dumps(data)


@app.route('/')
def index():
    form = BookingForm(request.form)
    return render_template('index.htm', form=form, colors=app.config['CALENDAR_COLORS'])


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
