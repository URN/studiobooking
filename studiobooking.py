from flask import Flask, render_template, request
from flask.ext.wtf import Form
from wtforms import TextField, DateField, validators

app = Flask(__name__)


class Booking(Form):
    name = TextField('Name')
    date = DateField('Date')


@app.route('/admin')
def admin():
    return 'admin'


@app.route('/booking', methods=['GET', 'POST'])
def booking():
    form = Booking(request.form)
    return render_template('booking_form.htm', form=form)


@app.route('/')
def index():
    return render_template('index.htm')
    return 'Hello World!'


if __name__ == '__main__':
    app.debug = True
    app.config['SECRET_KEY'] = '123'
    app.run()
