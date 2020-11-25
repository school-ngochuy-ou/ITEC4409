from app.models import User, Room, Category, Receipt, ReceiptDetail
from app import db


def get_user(id):
	if not id:
		return None

	return User.query.filter(User.id == id.strip()).first()


def save_user(user):
	db.session.add(user)
	db.session.commit()

	return user


def get_rooms():

	return Room.query.all()


def get_room(id):
	if not id:
		return None

	return Room.query.filter(Room.id == id.strip()).first()


def get_categories():

	return Category.query.all()


def get_category(id):

	return Category.query.filter(Category.id == id.strip()).first()


def save_room(room):
	db.session.add(room)
	db.session.commit()

	return room


def get_receipts():

	return Receipt.query.all()


def get_receipt_detail(id):

	return ReceiptDetail.query.filter(ReceiptDetail.receipt_id == id.strip()).all()


def count_user(id):

	return User.query.filter(User.id == id.strip()).count()


def save_receipt(receipt):
	db.session.add(receipt)
	db.session.commit()

	return receipt
