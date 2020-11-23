from app import app, mail
from app.admin import *
from app.user import *
from app.DAO import get_rooms as dao_get_rooms, get_room as dao_get_room, get_categories, get_category, save_room
from app.models import RoomStatus
from flask import redirect


@app.route("/")
def index():

    return render_template("index.html", customer_role=UserRole.CUSTOMER)


@app.route("/rooms")
@login_required
def get_rooms():
    if current_user.role is UserRole.CUSTOMER:
        return redirect("/")

    return render_template("rooms.html", rooms=dao_get_rooms())


@app.route("/room/<id>", methods=["GET", "POST"])
@login_required
def get_room_details(id):
    room = dao_get_room(id)

    if room is None:
        return render_template("room_details.html", error="Room not found")

    if request.method == "GET":

        return render_template("room_details.html", room=room, room_status=[RoomStatus.VACANT, RoomStatus.UNAVAILABLE,
                                                                            RoomStatus.BOOKED, RoomStatus.OCCUPIED],
                               admin_role=UserRole.ADMIN, categories=get_categories(),
                               manager_role=UserRole.MANAGER)

    status = request.form["status"]
    room.status = RoomStatus[status]

    if current_user.role is UserRole.ADMIN or current_user.role is UserRole.MANAGER:
        category_id = request.form["category"]
        room.category = get_category(category_id)
        room.name = request.form["name"]
        room.price = float(request.form["price"])

    save_room(room)

    return redirect(url_for("get_rooms"))


if __name__ == "__main__":
    app.run(debug=True)

