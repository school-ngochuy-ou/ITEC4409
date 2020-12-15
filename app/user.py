from app import app, login, mail
from app.DAO import get_user, save_user
from app.models import UserRole, User, get_roles_as_dict
from flask import request, redirect, render_template, url_for
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
import hashlib
import datetime
import uuid
import re
import enum


admin_user = get_user("admin")

if not admin_user:
	admin_user = User(id="admin", password=str(hashlib.md5("admin".encode("utf-8")).hexdigest()),
					  email="ngochuy.ou@gmail.com", name="Administrator", role=UserRole.ADMIN)
	save_user(admin_user)


class RegistrationErrors(enum.Enum):
	USERNAME = 0
	PASSWORD = 1
	EMAIL = 2
	NONE = 3


registration_handlers = dict()
registration_handlers[RegistrationErrors.USERNAME] = "Username can not be empty"
registration_handlers[RegistrationErrors.PASSWORD] = "Password can not be empty"
registration_handlers[RegistrationErrors.EMAIL] = "Invalid email"
registration_handlers[RegistrationErrors.NONE] = ""


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
	email = request.form.get("email")
	user = User(id=id, password=password, email=email)
	err = is_user_valid(user)

	if err is not RegistrationErrors.NONE:
		return redirect("/register?message=" + registration_handlers[err])

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
@login_required
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

	id = request.form.get("id")
	password = request.form.get("password")
	password = str(hashlib.md5(password.strip().encode("utf-8")).hexdigest())
	user = get_user(id)

	if user is None:
		return render_template("login.html", message="User not found")

	if not user.is_active:
		return render_template("login.html", message="Your account is locked")

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

	user.password_reset_token = str(uuid.uuid4())
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


@app.route("/u/edit/<id>", methods=["GET", "POST"])
@login_required
def edit_user(id):
	user = get_user(id)

	if user is None:
		return render_template("edit_account.html", error="User not found", roles=get_roles_as_dict())

	if request.method == "GET":
		if user.id != current_user.id:
			return render_template("edit_account.html", error="Access denied", roles=get_roles_as_dict())

		return render_template("edit_account.html", user=user, roles=get_roles_as_dict())

	name = request.form["name"].strip()
	email = request.form["email"].strip()
	password = request.form["password"].strip()
	re_password = request.form["re-password"].strip()
	user.name = name
	user.email = email

	if len(password) != 0:
		if password != re_password:
			return render_template("edit_account.html", user=user, message="Password and Re-password must match", roles=get_roles_as_dict())

	user.password = str(hashlib.md5(password.encode("utf-8")).hexdigest())
	err = is_user_valid(user)

	if err is not RegistrationErrors.NONE:
		return render_template("edit_account.html", user=user, message=registration_handlers[err], roles=get_roles_as_dict())

	save_user(user)

	return render_template("edit_account.html", user=user, message="DONE", roles=get_roles_as_dict())


def is_user_valid(user):
	if len(user.id) == 0:
		return RegistrationErrors.USERNAME

	if len(user.password) == 0:
		return RegistrationErrors.PASSWORD

	regex = r'[\w.-]+@[\w.-]+'

	if re.search(regex, user.email) is None:
		return RegistrationErrors.EMAIL

	return RegistrationErrors.NONE
