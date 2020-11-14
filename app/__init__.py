from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = '\xc4qr\xfa\xd97_6.\xa3\xf8\x13\x1ds\xa8y'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost/python_hotel"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = True

db = SQLAlchemy(app=app)

admin = Admin(app=app, name="Hotel", template_mode="bootstrap4")

login = LoginManager(app=app)