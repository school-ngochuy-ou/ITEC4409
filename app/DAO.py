from app.models import User, Room, Category, Receipt, ReceiptDetail, ReceiptCustomersDetail
from app import db
from sqlalchemy.sql import func, extract
from datetime import datetime


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


def get_receipts_by_user(id):
	print(id)
	return Receipt.query.filter(Receipt.user_id == id.strip()).all()


def get_receipt(id):

	return Receipt.query.filter(Receipt.id == id.strip()).first()


def get_receipt_details(receipt_id, room_id):

	return ReceiptDetail.query.filter((ReceiptDetail.receipt_id == receipt_id.strip()) &
									  (ReceiptDetail.room_id == room_id.strip())).first()


def count_user(id):

	return User.query.filter(User.id == id.strip()).count()


def save_receipt(receipt):
	db.session.add(receipt)
	db.session.commit()

	return receipt


def save_receipt_detail(detail):
	db.session.add(detail)
	db.session.commit()

	return detail


def save_receipt_customers_detail(detail):
	db.session.add(detail)
	db.session.commit()

	return detail


def delete_receipt_customers_detail(receipt_id):

	return ReceiptCustomersDetail.query.filter(ReceiptCustomersDetail.receipt_detail_receipt_id == receipt_id)\
		.delete()


def get_sale_by_category(month):
	result = db.engine.execute('''
		SELECT
			rd.name,
			SUM(rd.total) AS total,
			round((SUM(rd.total) / rd.overall_total * 100), 2) AS percentage
		FROM (
			SELECT rd.*, o.overall_total, t.name
			FROM receipt_details rd INNER JOIN (
					SELECT r.id AS room_id, c.name
					FROM rooms r INNER JOIN categories c ON r.category_id = c.id
				) t ON rd.room_id = t.room_id, (
					SELECT SUM(total) as overall_total FROM receipt_details dts
					WHERE MONTH(dts.created_date) = ''' + str(month) + '''
				) o
			GROUP BY rd.receipt_id, rd.room_id
		) AS rd
		WHERE MONTH(rd.created_date) = ''' + str(month) + '''
		GROUP BY rd.name;
	'''
	)

	return result


def get_occupation_rate(month):
	result = db.engine.execute('''
		SELECT r.name, SUM(rd.days) AS total, round(SUM(rd.days) / 30 * 100, 2) AS percentage
		FROM receipt_details rd INNER JOIN rooms r ON rd.room_id = r.id
		WHERE MONTH(rd.created_date) = ''' + str(month) + '''
		GROUP BY r.name;
	''')

	return result
