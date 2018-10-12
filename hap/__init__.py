from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SECRET_KEY'] = '2BB80D537B1DA3E38BD30361AA855686BDE0EACD7162FEF6A25FE97BF527A25B'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/hap'
db = SQLAlchemy(app)

from hap import routes