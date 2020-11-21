from app import app, login, mail
from app.DAO import get_user, save_user
from app.models import UserRole, User
from flask import request, redirect, render_template, url_for
from flask_login import login_user, current_user, logout_user
from flask_mail import Message
import hashlib
import datetime
import uuid


@login.user_loader
def load_user(user_id):
	return get_user(user_id)


@app.route("/register", methods=["GET", "POST"])
def register():
	if request.method == "GET":
		if current_user.is_authenticated:
			return redirect("/")

		return render_template("/register.html", message=request.args.get("message"))

	id = request.form.get("id")
	password = request.form.get("password")
	user = User(id=id, password=password)

	if not is_user_valid(user):
		return redirect("/register?message=Username and password can not be empty")

	if get_user(id) is not None:
		return redirect("/register?message=Username is taken")

	user.id = id
	user.password = str(hashlib.md5(password.strip().encode("utf-8")).hexdigest())
	user.role = UserRole.CUSTOMER
	user.is_active = True
	user.created_date = datetime.datetime.utcnow()
	save_user(user)
	login_user(user)

	return redirect("/")


@app.route("/logout", methods=["GET"])
def logout():
	if current_user.is_authenticated:
		logout_user()

	return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "GET":
		if current_user.is_authenticated:
			return redirect("/")

		return render_template("/login.html")

	message = ""
	id = request.form.get("id")
	password = request.form.get("password")
	password = str(hashlib.md5(password.strip().encode("utf-8")).hexdigest())
	user = get_user(id)

	if user is None:
		return render_template("login.html", message="User not found")

	if user.password == password:
		login_user(user)

		if user.role is UserRole.ADMIN:
			return redirect("/admin")

		return redirect("/")

	return render_template("login.html", message="Invalid password")


@app.route("/u/forgot/<id>")
def forgot_password(id):
	user = get_user(id)

	if id is None or user is None:
		return render_template("login.html", message="User not found")

	user.password_reset_token = str(uuid.uuid4());
	msg = Message("Reset your password", recipients=[user.email])
	url = url_for("reset_password", id=id, token=user.password_reset_token, _external=True)
	msg.html = "<a href='" + url + "'>Click here to reset your password</a>"

	with app.app_context():
		mail.send(msg)

	save_user(user)

	return render_template("login.html", message="Check your email (inbox, spam) to reset your password.")


@app.route("/u/reset/<id>", methods=['GET', 'POST'])
def reset_password(id):
	user = get_user(id)
	token = request.args.get("token")

	if id is None or user is None:

		return render_template("login.html", message="User not found")

	if request.method == "GET":
		if token == user.password_reset_token:

			return render_template("reset_password.html", user_id=id, message="")

		return render_template("login.html", message="Invalid token")

	password = request.form["password"]
	re_password = request.form["re-password"]

	if password != re_password:
		return render_template("reset_password.html", user_id=id, message="Password and Re-password must match")

	user.password = str(hashlib.md5(password.strip().encode("utf-8")).hexdigest())
	user.password_reset_token = None
	save_user(user)

	return render_template("login.html")


def is_user_valid(user):
	return len(user.id) is not 0 and len(user.password) is not 0
