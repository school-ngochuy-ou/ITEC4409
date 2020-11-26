async function isUserExist(username) {
    return await fetch(`/u/exists/${username}`, {
        method: "GET"
    })
    .then(res => res.status == 200 ? true : false)
}

async function onUsernameInputBlur() {
    username = document.getElementById('username-input').value;
    username = String(username).replace(/^\s+|\s+$/g, '');

    let exists = await isUserExist(username);

    if (!exists) {
        document.getElementById('username-input-msg').innerText = "User not found";

        return;
    }

    document.getElementById('username-input-msg').innerText = "";

    return;
}

async function onAddItemClick() {
    let root = document.getElementById('receipt-items-container');
    let res = await fetch("/rooms", {
        method: "GET",
        headers: {
            "Content-Type": "application/json"
        }
    })
    .then(res => res)
    .then(async res => await res.json());
    let options = res.rooms.map(e => `<option value="${e.id}">${e.name}</option>`).join(' ');
    let nextId = global_item_id++;
    let html = `
        <div class="row" name="rd-item" data-id=${nextId}>
            <div class="col">
                <div class="form-group">
                    <label for="rd-room-id" class="text-primary">Room</label>
                    <select class="form-control" id="rd-room-id" required="required">
                        ${options}
                    </select>
                </div>
            </div>
            <div class="col">
                <div class="form-group">
                    <label for="rd-days" class="text-primary">Duration (days)</label>
                    <input type="number" class="form-control" placeholder="Duration"
                    name="duration" min="1" id="rd-days">
                </div>
            </div>
            <div class="col">
                <div class="form-group">
                    <label for="rd-price" class="text-primary">Price</label>
                    <input type="number" class="form-control" placeholder="Price"
                    name="price" min="1.0" id="rd-price">
                </div>
            </div>
            <div class="col">
                <div class="form-group">
                    <label for="rd-status" class="text-primary">Status</label>
                    <select class="form-control" id="rd-status" required="required">
                        <option value="PENDING" class="text-muted">PENDING</option>
                        <option value="PAID" class="text-success">PAID</option>
                    </select>
                </div>
            </div>
            <div class="col">
                <div class="form-group">
                    <label class="text-primary">Actions</label></br>
                    <button class="btn btn-danger" type="button"
                    onclick="onRDRemoveBtnClick(${nextId})">
                    Remove</button>
                </div>
            </div>
        </div>
    `;
    root.insertAdjacentHTML('beforeend', html);
}

function onRDRemoveBtnClick(id) {
    let elements = document.querySelectorAll("[name='rd-item']");
    let root = document.getElementById('receipt-items-container');

    root.innerHTML = "";
    elements = Array.from(elements).filter(ele => parseInt(ele.getAttribute("data-id")) != id)
                    .forEach(e => root.appendChild(e));
}

function checkRDForm() {
    let form = document.getElementById("rd-form");
    let rooms = document.querySelectorAll("[name='rd-item']");

    rooms = Array.from(rooms).map(e => {
        id = e.querySelector("select[id='rd-room-id']").value;
        duration = e.querySelector("input[id='rd-days']").value;
        price = e.querySelector("input[id='rd-price']").value;
        status = e.querySelector("select[id='rd-status']").value;

        if (isEmpty([id, duration, price])) {
            document.getElementById("rd-items-msg").innerText = "Receipt details can not contain empty information";

            return { };
        }

        document.getElementById("rd-items-msg").innerText = "";

        return {
            room_id: id,
            days: duration,
            price, status
        };
    }).filter(ele => !(Object.keys(ele).length === 0 && ele.constructor === Object));

    if (rooms.length == 0) {
        return { result: false }
    }

    let username = document.getElementById("username-input").value;
    let customerName = document.getElementById("customer_name").value;
    let address = document.getElementById("address").value;

    if (isEmpty(username)) {
        username = null;

        if (isEmpty([customerName, address])) {
            document.getElementById('username-input-msg').innerText = "Customer information can not be empty";

            return { result: false };
        }

        document.getElementById('username-input-msg').innerText = "";
    }

    if (rooms.length == 0 ) {
        document.getElementById('username-input-msg').innerText = "Receipt details can not be empty";

        return { result: false };
    }

    document.getElementById('username-input-msg').innerText = "";

    return {
        result: true,
        username,
        customer_name: customerName,
        address,
        rooms
    };
}

async function onRDSubmit() {
    let checkResult = checkRDForm();

    if (!checkResult.result) {
        return;
    }

    let body = {
        username: checkResult.username,
        customer_name: checkResult.customer_name,
        address: checkResult.address,
        rooms: checkResult.rooms,
        status: checkResult.status
    };
    let res = await fetch('/create_receipt', {
        method: "POST",
        body: JSON.stringify(body),
        headers: {
            "Content-Type": "application/json"
        }
    });

    if (res.ok) {
        alert("Success")
        return;
    }

    alert("Error: " + await res.text())
    return;
}

const isEmpty = (ele) => {
    if (Array.isArray(ele)) {
        return ele.map(ele => ele == null || ele.length == 0).includes(true);
    }

    return ele == null || ele.length == 0;
}

async function onRDEditSubmit() {
    let checkResult = checkRDForm();

    if (!checkResult.result) {
        return;
    }

    let body = {
        username: checkResult.username,
        customer_name: checkResult.customer_name,
        address: checkResult.address,
        rooms: checkResult.rooms,
        status: checkResult.status
    };

    let res = await fetch(window.location, {
        method: "POST",
        body: JSON.stringify(body),
        headers: {
            "Content-Type": "application/json"
        }
    });

    if (res.ok) {
        alert("Success")
        return;
    }

    alert("Error: " + await res.text())
    return;
}

var global_item_id;

window.addEventListener('load', function () {
    global_item_id = Array.from(document.querySelectorAll("[name='rd-item']")).length;
});