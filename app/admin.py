from app.models import Category, Room, User
from app import db, admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask_login import current_user, logout_user
from flask import redirect


class BaseRecordView(ModelView):
	form_excluded_columns = ("is_active", "created_date", )
	can_export = False

	def is_accessible(self):
		return current_user.is_authenticated


class PermanentRecordView(BaseRecordView):
	can_delete = False


class LogoutView(BaseView):
	@expose("/")
	def index(self):
		logout_user()

		return redirect("/admin")

	def is_accessible(self):
		return current_user.is_authenticated


class CategoryView(PermanentRecordView):
	form_excluded_columns = BaseRecordView.form_excluded_columns + ("rooms", )
	column_list = ["name", "price", "notes", "created_date", "is_active"]


class RoomView(PermanentRecordView):
	form_excluded_columns = BaseRecordView.form_excluded_columns + ("rooms", )
	column_list = ["name", "price", "status", "category", "created_date", "is_active"]


class UserView(PermanentRecordView):

	can_create = False
	column_display_pk = True
	form_columns = ["id", "name", "role"]
	column_exclude_list = ["password"]
	column_list = ["id", "name", "role", "created_date", "is_active"]
	column_labels = dict(id="Username")


admin.add_view(CategoryView(Category, db.session))
admin.add_view(RoomView(Room, db.session))
admin.add_view(UserView(User, db.session))
admin.add_view(LogoutView(name="Log out"))
