from app.models import User, Room, Category
from app import db


def get_user(id):

	return User.query.filter(User.id == id.strip()).first()


def save_user(user):
	db.session.add(user)
	db.session.commit()

	return user


def get_rooms():

	return Room.query.all()


def get_room(id):

	return Room.query.filter(Room.id == id.strip()).first()


def get_categories():

	return Category.query.all()


def get_category(id):

	return Category.query.filter(Category.id == id.strip()).first()


def save_room(room):
	db.session.add(room)
	db.session.commit()

	return room
