from app import app, login
from app.models import User
from flask import request, redirect
from flask_login import login_user
import hashlib


@login.user_loader
def load_user(user_id):
	return User.query.get(user_id)


@app.route("/login_admin", methods=["GET", "POST"])
def login_admin():
	if request.method == "POST":
		id = request.form.get("id")
		password = request.form.get("password")
		password = str(hashlib.md5(password.strip().encode("utf-8")).hexdigest())
		user = User.query.filter(User.id == id.strip(), User.password == password.strip()).first()

		if user:
			login_user(user)

	return redirect("/admin")
