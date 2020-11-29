import enum
import datetime
from app import db
from sqlalchemy import Column, Integer, String, Float, \
	Enum, ForeignKey, Boolean, Date, ForeignKeyConstraint
from sqlalchemy.orm import relationship, backref
from flask_login import UserMixin


class BaseModel(db.Model):
	__abstract__ = True

	is_active = Column(Boolean, default=True)
	created_date = Column(Date, nullable=False, default=datetime.datetime.utcnow())


class Category(BaseModel):
	__tablename__ = "categories"

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(255), nullable=False)
	price = Column(Float, nullable=False)
	notes = Column(String(255), nullable=True)
	rooms = relationship("Room", backref="category", lazy=True)

	def __str__(self):
		return self.name


class RoomStatus(enum.Enum):
	BOOKED = "BOOKED"
	VACANT = "VACANT"
	OCCUPIED = "OCCUPIED"
	UNAVAILABLE = "UNAVAILABLE"


class UserRole(enum.Enum):
	ADMIN = "ADMIN"
	CUSTOMER = "CUSTOMER"
	MANAGER = "MANAGER"
	EMPLOYEE = "EMPLOYEE"


class User(BaseModel, UserMixin):
	__tablename__ = "users"

	id = Column(String(255), nullable=False, primary_key=True)
	name = Column(String(255), nullable=True)
	password = Column(String(255), nullable=False)
	role = Column(Enum(UserRole), nullable=False, default=UserRole.CUSTOMER)
	email = Column(String(255), nullable=False)
	password_reset_token = Column(String(255), nullable=True)
	receipts = relationship("Receipt", backref="user", lazy=True)

	def __str__(self):
		return self.name


class Room(BaseModel):
	__tablename__ = "rooms"

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(255), nullable=False)
	price = Column(Float, nullable=False)
	status = Column(Enum(RoomStatus), nullable=False)
	category_id = Column(Integer, ForeignKey(Category.id), nullable=False)

	def __str__(self):
		return self.name

	def serialize(self):
		return {
			"id": self.id,
			"name": self.name,
			"price": self.price,
			"status": self.status.value,
			"category_id": self.category_id
		}


class Receipt(BaseModel):
	__tablename__ = "receipts"

	id = Column(Integer, primary_key=True, autoincrement=True)
	address = Column(String(255), nullable=True)
	customer_name = Column(String(255), nullable=True)
	total = Column(Float, nullable=False, default=0.0)
	user_id = Column(String(255), ForeignKey(User.id), nullable=True)


class PaymentStatus(enum.Enum):
	PAID = "PAID"
	PENDING = "PENDING"


class ReceiptDetail(BaseModel):
	__tablename__ = "receipt_details"

	def __init__(self, args):
		if type(args) is dict:
			self.receipt_id = args.get("receipt_id")
			self.room_id = args.get("room_id")
			self.days = int(args.get("days"))
			self.price = float(args.get("price"))
			self.status = args.get("status")
			self.total = self.days * self.price
			self.customers_detail = args.get("customers_detail")

	def update_stats(self):
		price = self.price

		if price is None:
			price = self.room.price

		if len(self.customers_detail) == 3:
			price += (price * 0.25)

		has_foreigner = False

		for detail in self.customers_detail:
			if detail.type == CustomerType.FOREIGN:
				has_foreigner = True
				break

		if has_foreigner:
			price += price * 0.5

		self.total = price * self.days

	receipt_id = Column(Integer, ForeignKey(Receipt.id), primary_key=True)
	room_id = Column(Integer, ForeignKey(Room.id), primary_key=True)
	days = Column(Integer, nullable=False, default=1)
	price = Column(Float, nullable=False, default=0.0)
	total = Column(Float, nullable=False, default=0.0)
	status = Column(Enum(PaymentStatus), nullable=False)
	room = relationship(Room, backref=backref("details", cascade="all, delete-orphan"))
	receipts = relationship(Receipt, backref=backref("details", cascade="all, delete-orphan"))


class CustomerType(enum.Enum):
	DOMESTIC = "DOMESTIC"
	FOREIGN = "FOREIGN"


class ReceiptCustomersDetail(BaseModel):
	__tablename__ = "receipt_customers_detail"
	__table_args__ = (
		ForeignKeyConstraint(
			['receipt_detail_receipt_id', 'receipt_detail_room_id'],
			['receipt_details.receipt_id', 'receipt_details.room_id'],
		),
	)

	def __init__(self, args):
		if type(args) is dict:
			self.name = args.get("name")
			self.type = args.get("type")
			self.citizen_id = args.get("citizen_id")
			self.address = args.get("address")

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(255), nullable=False)
	type = Column(Enum(CustomerType), nullable=False)
	citizen_id = Column(String(12), nullable=True)
	address = Column(String(255), nullable=True)
	receipt_detail_receipt_id = Column(Integer, nullable=False)
	receipt_detail_room_id = Column(Integer, nullable=False)
	receipt_detail = db.relationship(ReceiptDetail, backref=db.backref('customers_details', lazy=True))


def get_roles_as_dict():

	return dict({
		"customer": UserRole.CUSTOMER,
		"admin": UserRole.ADMIN,
		"manager": UserRole.MANAGER,
		"employee": UserRole.EMPLOYEE,
	})


def get_payment_status_as_dict():

	return dict({
		"paid": PaymentStatus.PAID,
		"pending": PaymentStatus.PENDING,
	})


def get_customer_type_as_dict():

	return dict({
		"domestic": CustomerType.DOMESTIC,
		"foreign": CustomerType.FOREIGN
	})


if __name__ == "__main__":
	db.create_all()
