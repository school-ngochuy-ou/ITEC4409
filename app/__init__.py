from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import json
import os


app = Flask(__name__)
app.secret_key = '\xc4qr\xfa\xd97_6.\xa3\xf8\x13\x1ds\xa8y'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost/python_hotel"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = True
module_dir = os.path.dirname(__file__)

with open(os.path.join(module_dir, "config.json")) as f:
	json_config = json.load(f)

app.config.update(dict(
	DEBUG=True,
	MAIL_SERVER='smtp.office365.com',
	MAIL_PORT=587,
	MAIL_USE_TLS=True,
	MAIL_USE_SSL=False,
	MAIL_USERNAME=json_config["mail"]["MAIL_USERNAME"],
	MAIL_PASSWORD=json_config["mail"]["MAIL_PASSWORD"],
	MAIL_DEFAULT_SENDER=json_config["mail"]["MAIL_DEFAULT_SENDER"],
))

db = SQLAlchemy(app=app)
mail = Mail(app)
login = LoginManager(app=app)
