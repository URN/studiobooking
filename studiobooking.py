from flask import Flask, render_template, request
from flask.ext.wtf import Form
from flask.ext.sqlalchemy import SQLAlchemy
from wtforms import TextField, DateField, SelectField, HiddenField, SubmitField
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = '123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'
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
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    studio = db.Column(db.Integer)

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
        start = datetime.strptime(form.start.data, '%a, %d %b %Y %H:%M:%S %Z') + timedelta(hours=1)
        end = datetime.strptime(form.duration.data, '%I:%M%p').time()
        end = datetime.combine(start.date(), end)
        print start
        print end
        #booking = Booking(form.name.data, form.date.data)
        booking = Booking(form.name.data, form.contact.data, form.start.data,
                          form.duration.data, form.studio.data)
        return 'submitted'
    return render_template('booking_form.htm', form=form)


@app.route('/')
def index():
    form = BookingForm(request.form)
    return render_template('index.htm', form=form)


if __name__ == '__main__':
    app.debug = True
    app.run()
