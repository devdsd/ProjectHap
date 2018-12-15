import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail


app = Flask(__name__)
app.config['SECRET_KEY'] = '2BB80D537B1DA3E38BD30361AA855686BDE0EACD7162FEF6A25FE97BF527A25B'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/hap'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
# app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
# app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
# app.config['MAIL_PORT'] = 2525
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
# app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USERNAME'] = '6d4a7e8b79b139'
app.config['MAIL_PASSWORD'] = '87183f92a8e9f1'
mail = Mail(app)

from hap import routes