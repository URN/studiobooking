from flask import Flask, render_template, request, jsonify
from flask.ext.wtf import Form
from flask.ext.sqlalchemy import SQLAlchemy
from wtforms import TextField, DateField, SelectField, HiddenField, SubmitField
from datetime import datetime, timedelta
from json import dumps

app = Flask(__name__)
app.config['SECRET_KEY'] = '123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'
app.config['CALENDAR_COLORS'] = ['#3D862D',  # either
                                 '#3C76B4',  # studio 1
                                 '#998333',  # studio 2
                                 '#733426',  # admin event
                                 ]
db = SQLAlchemy(app)


#class User(db.Model):
    #id = db.Column(db.Integer, primary_key=True)
    #username = db.Column(db.String(80), unique=True)
    #email = db.Column(db.String(120), unique=True)

    #def __init__(self, username, email):
        #self.username = username
        #self.email = email

    #def __repr__(self):
        #return '<User %r>' % self.username


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
        return {'title': self.name,
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


@app.route('/admin')
def admin():
    return 'admin'


@app.route('/booking', methods=['GET', 'POST'])
def make_booking():
    form = BookingForm(request.form)
    if request.method == 'POST':
        print form.start.data
        start = form.start.data
        start = datetime.strptime(form.start.data,
                                  '%a, %d %b %Y %H:%M:%S %Z') + \
                                  timedelta(hours=1)
        end = datetime.strptime(form.duration.data, '%I:%M%p').time()
        end = datetime.combine(start.date(), end)
        print start.strftime('%s')
        print end.strftime('%s')
        #booking = Booking(form.name.data, form.date.data)
        booking = Booking(form.name.data, form.contact.data,
                          start.strftime('%s'),
                          end.strftime('%s'), form.studio.data)
        db.session.add(booking)
        db.session.commit()
        message = {}
        message['text'] = 'Submitted!'
        message['alert'] = 'alert alert-success'
        return render_template('booking_response.htm', message=message)
    return render_template('booking_form.htm', form=form)


@app.route('/events')
def get_events():
    start = request.args['start']
    end = request.args['end']
    events = Booking.query.filter(Booking.start.between(start, end)).all()
    data = map(lambda x: x.as_dict(), events)
    print data
    print events[1].as_dict()
    return dumps(data)
    return jsonify(events[1].as_dict())


@app.route('/')
def index():
    form = BookingForm(request.form)
    return render_template('index.htm', form=form)


if __name__ == '__main__':
    app.debug = True
    app.run()
