from app import app, mail, db
from app.admin import *
from app.user import *
from app.DAO import get_rooms as dao_get_rooms, get_room as dao_get_room, get_categories, get_category, save_room,\
    get_receipts, count_user, save_receipt, get_receipt, get_receipt_details
from app.models import RoomStatus, get_roles_as_dict, Receipt, ReceiptDetail, PaymentStatus
from flask import redirect, jsonify


@app.route("/")
def index():

    return render_template("index.html", roles=dict({
        "customer": UserRole.CUSTOMER,
        "admin": UserRole.ADMIN
    }))


@app.route("/u/exists/<id>")
def is_user_exists(id):
    if count_user(id) > 0:
        return '', 200

    return '', 404


@app.route("/rooms")
@login_required
def get_rooms():
    if current_user.role is UserRole.CUSTOMER:
        return redirect("/")

    if request.headers.get("Content-Type") == "application/json":

        return jsonify(rooms=[e.serialize() for e in dao_get_rooms()])

    return render_template("rooms.html", rooms=dao_get_rooms(), roles=get_roles_as_dict())


@app.route("/room/<id>", methods=["GET", "POST"])
@login_required
def get_room_details(id):
    room = dao_get_room(id)

    if room is None:
        return render_template("room_details.html", error="Room not found")

    if request.method == "GET":

        return render_template("room_details.html", room=room, room_status=[RoomStatus.VACANT, RoomStatus.UNAVAILABLE,
                                                                            RoomStatus.BOOKED, RoomStatus.OCCUPIED],
                               categories=get_categories(), roles=get_roles_as_dict())

    status = request.form["status"]
    room.status = RoomStatus[status]

    if current_user.role is UserRole.ADMIN or current_user.role is UserRole.MANAGER:
        category_id = request.form["category"]
        room.category = get_category(category_id)
        room.name = request.form["name"]
        room.price = float(request.form["price"])

    save_room(room)

    return redirect(url_for("get_rooms"))


@app.route("/create_receipt", methods=["POST"])
@login_required
def create_receipt():
    data = request.get_json()
    user_id = data.get("username")
    customer_name = data.get("customer_name")
    address = data.get("address")
    user = get_user(user_id)
    new_receipt = Receipt()

    if not user:
        if len(customer_name) == 0 and len(address) == 0:
            return "Invalid request", 400

        new_receipt.customer_name = customer_name
        new_receipt.address = address
        user_id = None

    new_receipt.user_id = user_id
    rooms = data.get("rooms")
    save_receipt(new_receipt)
    details = []

    for room in rooms:
        room["receipt_id"] = new_receipt.id
        room["status"] = PaymentStatus.PENDING
        new_room = ReceiptDetail(room)
        details.append(new_room)

    new_receipt.details = details
    save_receipt(new_receipt)

    return '', 200


@app.route("/receipts/<state>", methods=["GET"])
@login_required
def obtain_receipts(state):
    if state != "new" and state != "view":
        state = "view"

    if state == "new":
        return render_template("/receipts.html", roles=get_roles_as_dict(), rooms=dao_get_rooms(), state=state)

    return render_template("/receipts.html", roles=get_roles_as_dict(), list=get_receipts(), state=state)


@app.route("/receipt/<receipt_id>", methods=["GET", "POST"])
@login_required
def receipt_details(receipt_id):
    receipt = get_receipt(receipt_id)

    if receipt is None:
        return render_template("/receipt_details.html", roles=get_roles_as_dict(), error="Receipt not found")

    if request.method == "GET":
        return render_template("/receipt_details.html", roles=get_roles_as_dict(), receipt=receipt, rooms=dao_get_rooms())

    data = request.get_json()
    user_id = data.get("username")
    customer_name = data.get("customer_name")
    address = data.get("address")
    user = get_user(user_id)

    if not user:
        if len(customer_name) == 0 and len(address) == 0:
            return "Invalid request", 400

        receipt.customer_name = customer_name
        receipt.address = address
        user_id = None

    receipt.user_id = user_id
    rooms = data.get("rooms")

    if len(rooms) == 0:
        return "Receipt items can not be empty", 400

    details = []

    for detail in rooms:
        detail["receipt_id"] = receipt_id
        detail["status"] = PaymentStatus.PENDING
        new_detail = get_receipt_details(detail["receipt_id"], detail["room_id"])

        if new_detail is not None:
            new_detail.days = int(detail["days"])
            new_detail.price = float(detail["price"])
            new_detail.total = new_detail.days * new_detail.price
        else:
            new_detail = ReceiptDetail(detail)

        details.append(new_detail)

    receipt.details = details
    db.session.commit()

    return '', 200


if __name__ == "__main__":
    app.run(debug=True)
