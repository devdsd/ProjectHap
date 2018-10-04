from flask import Flask, render_template, url_for, redirect, request, flash

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title='Home Page')

@app.route('/about')
def about():
    return render_template('about.html', title='About Hap')

if __name__ == '__main__':
    app.run(debug=True, port=8080)