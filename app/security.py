from app import app, login
from app.DAO import get_user, save_user
from app.models import UserRole, User
from flask import request, redirect, render_template
from flask_login import login_user, current_user
import hashlib
import datetime


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
		return redirect("/login")

	if user.password == password:
		login_user(user)

	if user.role is UserRole.ADMIN:
		return redirect("/admin")

	return redirect("/")


def is_user_valid(user):

	return len(user.id) is not 0 and len(user.password) is not 0
