from app.models import Category, Room
from app import db, admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask_login import current_user, logout_user
from flask import redirect


class BaseRecordView(ModelView):
	form_excluded_columns = ("is_active", "created_date")

	def is_accessible(self):
		return current_user.is_authenticated


class PermanentRecordView(BaseRecordView):
	can_delete = False
	can_export = False


class LogoutView(BaseView):
	@expose("/")
	def index(self):
		logout_user()

		return redirect("/admin")

	def is_accessible(self):
		return current_user.is_authenticated


admin.add_view(PermanentRecordView(Category, db.session))
admin.add_view(PermanentRecordView(Room, db.session))
admin.add_view(LogoutView(name = "Log out"))
