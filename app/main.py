from app import app, mail, db
from app.admin import *
from app.user import *
from app.DAO import get_rooms as dao_get_rooms, get_room as dao_get_room, get_categories, get_category, save_room,\
    get_receipts, count_user, save_receipt, get_receipt, get_receipt_details, get_receipts_by_user,\
    save_receipt_detail, save_receipt_customers_detail, delete_receipt_customers_detail
from app.models import RoomStatus, get_roles_as_dict, Receipt, ReceiptDetail, PaymentStatus,\
    get_payment_status_as_dict, CustomerType, ReceiptCustomersDetail
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
    if current_user.role is UserRole.CUSTOMER:
        return redirect("/login")

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
    if current_user.role is UserRole.CUSTOMER:
        return "Unauthorized", 401

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
    items = data.get("rooms")
    save_receipt(new_receipt)
    details = []
    receipt_total = 0.0

    for item in items:
        item["receipt_id"] = new_receipt.id
        status = item["status"]

        if status is None or len(status) == 0:
            item["status"] = PaymentStatus.PENDING
        else:
            item["status"] = PaymentStatus[status]

        new_item = ReceiptDetail(item)
        save_receipt_detail(new_item)
        customers_detail = item["customers_detail"]

        if len(customers_detail) < 1 or len(customers_detail) > 3:
            return 'Customers detail in a room can not be empty', 400

        cds = []

        for cd in customers_detail:
            new_customers_detail = ReceiptCustomersDetail(cd)
            new_customers_detail.receipt_detail_receipt_id = new_item.receipt_id
            new_customers_detail.receipt_detail_room_id = new_item.room_id
            save_receipt_customers_detail(new_customers_detail)
            cds.append(new_customers_detail)

        new_item.customers_detail = cds
        new_item.update_stats()
        details.append(new_item)
        receipt_total += new_item.total

    new_receipt.details = details
    new_receipt.total = receipt_total
    save_receipt(new_receipt)

    return '', 200


@app.route("/receipts/<state>", methods=["GET"])
@login_required
def obtain_receipts(state):
    if current_user.role is UserRole.CUSTOMER:
        return "Unauthorized", 401

    if state != "new" and state != "view":
        state = "view"

    if state == "new":
        return render_template("/receipts.html", roles=get_roles_as_dict(), rooms=dao_get_rooms(), state=state,
                               payment_status=get_payment_status_as_dict(),
                               customer_types=[CustomerType.DOMESTIC, CustomerType.FOREIGN])

    return render_template("/receipts.html", roles=get_roles_as_dict(), list=get_receipts(), state=state)


@app.route("/receipt/<receipt_id>", methods=["GET", "POST"])
@login_required
def receipt_details(receipt_id):
    receipt = get_receipt(receipt_id)

    if receipt is None:
        return render_template("/receipt_details.html", roles=get_roles_as_dict(), error="Receipt not found")

    if request.method == "GET":
        if current_user.role is UserRole.CUSTOMER and receipt.user_id != current_user.id:

            return render_template("/receipt_details.html", roles=get_roles_as_dict(), error="Access denied")

        return render_template("/receipt_details.html", roles=get_roles_as_dict(), receipt=receipt,
                               rooms=dao_get_rooms(), payment_status=get_payment_status_as_dict(),
                               read_only=current_user.role == UserRole.CUSTOMER,
                               customer_types=[CustomerType.DOMESTIC, CustomerType.FOREIGN])

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
    items = data.get("rooms")

    if len(items) == 0:
        return "Receipt items can not be empty", 400

    details = []
    receipt_total = 0.0
    delete_receipt_customers_detail(receipt.id)

    for item in items:
        item["receipt_id"] = receipt_id
        status = item["status"]

        if status is None or len(status) == 0:
            item["status"] = PaymentStatus.PENDING
        else:
            item["status"] = PaymentStatus[status]

        new_item = get_receipt_details(item["receipt_id"], item["room_id"])

        if new_item is not None:
            new_item.days = int(item["days"])
            new_item.price = float(item["price"])
            new_item.status = item["status"]
            new_item.total = new_item.days * new_item.price
        else:
            new_item = ReceiptDetail(item)

        save_receipt_detail(new_item)
        customers_detail = item["customers_detail"]

        if len(customers_detail) < 1 or len(customers_detail) > 3:
            return 'Customers detail in a room can not be empty', 400

        cds = []

        for cd in customers_detail:
            new_customers_detail = ReceiptCustomersDetail(cd)
            new_customers_detail.receipt_detail_receipt_id = new_item.receipt_id
            new_customers_detail.receipt_detail_room_id = new_item.room_id
            save_receipt_customers_detail(new_customers_detail)
            cds.append(new_customers_detail)

        new_item.customers_detail = cds
        new_item.update_stats()
        details.append(new_item)
        receipt_total += new_item.total

    receipt.details = details
    receipt.total = receipt_total
    db.session.commit()

    return '', 200


@app.route("/u/receipts")
@login_required
def get_personal_receipts():

    return render_template("personal_receipts.html", list=get_receipts_by_user(current_user.id), roles=get_roles_as_dict())


if __name__ == "__main__":
    app.run(debug=True)
