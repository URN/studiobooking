from flask import Flask, render_template, request, jsonify, Response
from flask.ext.wtf import Form
from flask.ext.sqlalchemy import SQLAlchemy
from wtforms import TextField, DateField, SelectField, \
    HiddenField, SubmitField, PasswordField
from datetime import datetime, timedelta
from json import dumps
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = '123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'
app.config['CALENDAR_COLORS'] = ['#3D862D',  # either
                                 '#3C76B4',  # studio 1
                                 '#998333',  # studio 2
                                 '#733426',  # admin event
                                 ]
db = SQLAlchemy(app)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    contact = db.Column(db.String(120))
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)
    studio = db.Column(db.Integer)

    def as_dict(self):
        start = datetime.fromtimestamp(self.start).strftime('%Y-%m-%d %H:%M:%S')
        end = datetime.fromtimestamp(self.end).strftime('%Y-%m-%d %H:%M:%S')
        start = datetime.fromtimestamp(self.start).isoformat()
        end = datetime.fromtimestamp(self.end).isoformat()
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
    name = TextField('Name')
    contact = TextField('Contact')
    date = TextField('Date')
    time = DateField('Starting time')
    duration = TextField('Duration')
    studio = SelectField('Studio',
                         choices=[(0, 'Either'),
                                  (1, 'Studio 1'),
                                  (2, 'Studio 2')],
                         coerce=int)
    submit = SubmitField('Submit')


class LoginForm(Form):
    username = TextField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Login')


def check_for_clashes(start, end):
    start = int(start)+1
    end = int(end)-1
    if Booking.query.filter(Booking.start.between(start, end)).count() > 0:
        return False
    if Booking.query.filter(Booking.end.between(start, end)).count() > 0:
        return False
    return True


def check_auth(username, password):
    return username == 'admin' and password == 'bookings'


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
    return render_template('admin.htm', form=form)


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
    message['text'] = "Deleted booking by "+booking.name
    message['alert'] = 'alert alert-success'
    return render_template('booking_response.htm', message=message)


@app.route('/booking', methods=['GET', 'POST'])
def make_booking():
    form = BookingForm(request.form)
    if request.method == 'POST':
        start = form.start.data
        start = datetime.strptime(form.start.data,
                                  '%a, %d %b %Y %H:%M:%S %Z') + \
                                  timedelta(hours=1)
        end = datetime.strptime(form.duration.data, '%I:%M%p').time()
        end = datetime.combine(start.date(), end)
        start = start.strftime('%s')
        end = end.strftime('%s')
        message = {}
        if check_for_clashes(start, end):
            #booking = Booking(form.name.data, form.date.data)
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
    start = request.args['start']
    end = request.args['end']
    events = Booking.query.filter(Booking.start.between(start, end)).all()
    data = map(lambda x: x.as_dict(), events)
    return dumps(data)


@app.route('/')
def index():
    form = BookingForm(request.form)
    return render_template('index.htm', form=form)


if __name__ == '__main__':
    app.debug = True
    app.run()
