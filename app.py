from flask import Flask, render_template, url_for, redirect, request, flash
from createevents import CreateEvent

app = Flask(__name__)
app.config['SECRET_KEY'] ='SECRET'

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title='Home Page')

@app.route('/about')
def about():
    return render_template('about.html', title='About Hap')

@app.route('/createevent', methods=['GET', 'POST'])
def createevent():
    form = CreateEvent()
    if form.validate_on_submit():
        flash('Event Created successfully', 'success')
        return redirect(url_for('home'))
    return render_template('createevent.html', title='Create Event', form=form)

if __name__ == '__main__':
    app.run(debug=True, port=8080)