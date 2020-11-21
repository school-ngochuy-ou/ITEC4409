from app.models import Category, Room, User, UserRole
from app import db, app
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose, Admin, AdminIndexView
from flask_login import current_user, logout_user
from flask import redirect, url_for


class MyAdminIndexView(AdminIndexView):
	@expose('/')
	def index(self):
		print("----" + str(current_user.role))
		if not current_user.is_authenticated or current_user.role is not UserRole.ADMIN:
			return redirect(url_for('login'))

		return super(MyAdminIndexView, self).index()


admin = Admin(app=app, name="Hotel", template_mode="bootstrap4", index_view=MyAdminIndexView())


class BaseRecordView(ModelView):
	form_excluded_columns = ("created_date", )
	can_export = False

	def is_accessible(self):
		return current_user.is_authenticated and current_user.role is UserRole.ADMIN


class PermanentRecordView(BaseRecordView):
	can_delete = False


class LogoutView(BaseView):

	@expose("/")
	def index(self):
		if current_user.is_authenticated:
			logout_user()

		return redirect("/admin")

	def is_accessible(self):
		return current_user.is_authenticated and current_user.role is UserRole.ADMIN


class CategoryView(PermanentRecordView):
	form_excluded_columns = BaseRecordView.form_excluded_columns + ("rooms", )
	form_columns = ["name", "price", "notes", "is_active"]
	column_list = ["name", "price", "notes", "created_date", "is_active"]


class RoomView(PermanentRecordView):
	form_excluded_columns = BaseRecordView.form_excluded_columns + ("rooms", )
	form_columns = ["name", "price", "status", "category", "is_active"]
	column_list = ["name", "price", "status", "category", "created_date", "is_active"]


class UserView(PermanentRecordView):

	can_create = False
	column_display_pk = True
	form_columns = ["id", "name", "role", "is_active"]
	column_exclude_list = ["password"]
	column_list = ["id", "name", "role", "created_date", "is_active"]
	column_labels = dict(id="Username")


admin.add_view(CategoryView(Category, db.session))
admin.add_view(RoomView(Room, db.session))
admin.add_view(UserView(User, db.session))
admin.add_view(LogoutView(name="Log out"))
