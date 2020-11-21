import enum
import datetime
from app import db
from sqlalchemy import Column, Integer, String, Float,\
	Enum, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship
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
	BOOKED = 1
	VACANT = 2
	OCCUPIED = 3
	UNAVAILABLE = 4


class Room(BaseModel):
	__tablename__ = "rooms"

	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(String(255), nullable=False)
	price = Column(Float, nullable=False)
	status = Column(Enum(RoomStatus), nullable=False)
	category_id = Column(Integer, ForeignKey(Category.id), nullable=False)

	def __str__(self):
		return self.name


class UserRole(enum.Enum):
	ADMIN = 1
	CUSTOMER = 2
	MANAGER = 3
	EMPLOYEE = 4


class User(BaseModel, UserMixin):
	__tablename__ = "users"

	id = Column(String(255), nullable=False, primary_key=True)
	name = Column(String(255), nullable=True)
	password = Column(String(255), nullable=False)
	role = Column(Enum(UserRole), nullable=False, default=UserRole.CUSTOMER)
	email = Column(String(255), nullable=False)
	password_reset_token = Column(String(255), nullable=False)

	def __str__(self):
		return self.name


if __name__ == "__main__":
	db.create_all()
