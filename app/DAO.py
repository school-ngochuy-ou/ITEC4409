from app.models import User
from app import db


def get_user(id):

	return User.query.filter(User.id == id.strip()).first()


def save_user(user):
	db.session.add(user)
	db.session.commit()

	return user
