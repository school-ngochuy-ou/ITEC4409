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
            <div class="row ml-4" name="cd-container" data-id=${nextId}>
                <table class="table">
                    <thead class="thead-dark">
                        <th scope="col">Customer name</th>
                        <th scope="col">Type</th>
                        <th scope="col">Citizen ID</th>
                        <th scope="col">Address</th>
                        <th scope="col">Actions</th>
                    </thead>
                    <tbody>
                        <tr name="cd-item-container" data-id=0>
                            <td>
                                <input type="text" class="form-control" placeholder="Customer name"
                                name="cd-customer-name" required="required">
                            </td>
                            <td>
                                <select name="cd-customer-type" required="required"
                                class="form-control">
                                    <option value="DOMESTIC">DOMESTIC</option>
                                    <option value="FOREIGN">FOREIGN</option>
                                </select>
                            </td>
                            <td>
                                <input type="text" class="form-control" placeholder="Citizen ID"
                                name="cd-citizen-id" required="required">
                            </td>
                            <td>
                                <input type="text" class="form-control" placeholder="Address"
                                name="cd-address" required="required">
                            </td>
                            <td>
                                <button type="button" name="cd-item-remove-btn"
                                class="btn btn-danger" onclick="onCDItemRemoveBtn(${nextId}, 0)"
                                >Remove</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <div class="w-100 text-right">
                    <button type="button" name="cd-add-btn"
                    class="btn btn-secondary"
                    onclick="onCDAddBtnClick(${nextId})">Add Customer</button>
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
    let flag = true;

    rooms = Array.from(rooms).map(e => {
        id = e.querySelector("select[id='rd-room-id']").value;
        duration = e.querySelector("input[id='rd-days']").value;
        price = e.querySelector("input[id='rd-price']").value;
        status = e.querySelector("select[id='rd-status']").value;

        if (isEmpty([id, duration, price])) {
            document.getElementById("rd-items-msg").innerText = "Receipt details can not contain empty information";
            flag = false;

            return { };
        }

        document.getElementById("rd-items-msg").innerText = "";

        let cdResult = checkCustomersDetail(parseInt(e.getAttribute('data-id')));

        if (!cdResult.result) {
            flag = false;
            return { };
        }

        return {
            room_id: id,
            days: duration,
            price, status,
            customers_detail: cdResult.customers_detail
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
        result: flag,
        username,
        customer_name: customerName,
        address,
        rooms
    };
}

function checkCustomersDetail(cDId) {
    let root = document.querySelector(`div[name='rd-item'][data-id='${cDId}']`);
    let containers = root.querySelectorAll(`tr[name="cd-item-container"]`);
    let flag = true;
    let customersDetail = Array.from(containers).map(ele => {
        let customerName = ele.querySelector('input[name="cd-customer-name"]').value;
        let type = ele.querySelector('select[name="cd-customer-type"]').value;
        let citizenId = ele.querySelector('input[name="cd-citizen-id"]').value;
        let address = ele.querySelector('input[name="cd-address"]').value;

        if (isEmpty([customerName, type])) {
            alert("Customers name and Customer type information in a room can not be empty");
            flag = false;

            return {};
        }

        return {
            result: flag,
            name: customerName,
            type,
            citizen_id: citizenId,
            address
        };
    })
    .filter(ele => !(Object.keys(ele).length === 0 && ele.constructor === Object));

    if (customersDetail.length <= 0) {
        alert("Customers detail information can not be empty");
        flag = false;
    }

    return {
        result: flag,
        customers_detail: customersDetail
    }
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

function onCDAddBtnClick(cDId) {
    let container = document.querySelector(`div[name='cd-container'][data-id='${cDId}']`);
    let itemContainers = Array.from(container.querySelectorAll(`tr[name='cd-item-container']`));
    let itemQty = itemContainers.length;
    let newItem;

    if (itemQty >= 2) {
        container.querySelector(`button[name='cd-add-btn']`).remove();

        if (itemQty > 2) {
            return;
        }
    }

    newItem = `
        <tr name="cd-item-container" data-id=${++globalCDItemId}>
            <td>
                <input type="text" class="form-control" placeholder="Customer name"
                name="cd-customer-name" required="required">
            </td>
            <td>
                <select name="cd-customer-type" required="required"
                class="form-control">
                    <option value="DOMESTIC">DOMESTIC</option>
                    <option value="FOREIGN">FOREIGN</option>
                </select>
            </td>
            <td>
                <input type="text" class="form-control" placeholder="Citizen ID"
                name="cd-citizen-id" required="required">
            </td>
            <td>
                <input type="text" class="form-control" placeholder="Address"
                name="cd-address" required="required">
            </td>
            <td>
                <button type="button" name="cd-item-remove-btn"
                class="btn btn-danger" onclick="onCDItemRemoveBtn(${cDId}, ${globalCDItemId})"
                >Remove</button>
            </td>
        </tr>
    `;
    container.querySelector("tbody").insertAdjacentHTML("beforeend", newItem);
}

function onCDItemRemoveBtn(cDId, cDItemId) {
    document.querySelector(`div[name='rd-item'][data-id='${cDId}']`)
        .querySelector(`tr[name='cd-item-container'][data-id='${cDItemId}']`)
        .remove();

    if (document.querySelector(`div[name='rd-item'][data-id='${cDId}']`)
        .querySelectorAll(`tr[name='cd-item-container']`)
        .length == 2) {
        document.querySelector(`div[name='cd-container'][data-id='${cDId}']`)
            .insertAdjacentHTML('beforeend', `
                <div class="w-100 text-right">
                    <button type="button" name="cd-add-btn"
                    class="btn btn-secondary"
                    onclick="onCDAddBtnClick(${cDId})">Add Customer</button>
                </div>
            `);
    }
}

async function onMonthSelectChange() {
    let target = document.querySelector('select[name="sales-month-picker"]');
    let value = target.value;
    let res = await fetch(`${window.location}/category?month=${value}`)
                        .then(async res => await res.json())
                        .catch(err => console.error(err));
    let caption = document.querySelector('caption[name="sales-by-category-caption"]');
    let eles = res.sales;
    let container = document.querySelector('tbody[name="sales-by-category-items-container"]');

    if (eles.length == 0) {
        caption.innerText = "No sales found in this month";
        container.innerHTML = "";
        return;
    }

    let dom;

    caption.innerText = "";
    dom = eles.map((ele, index) => `
        <tr>
            <td scope="row">${index + 1}</td>
            <td>${ele.name}</td>
            <td>${ele.total}</td>
            <td>${ele.percentage}%</td>
        </tr>
    `).join('');
    container.innerHTML = dom;

    return;
}

async function onOccupationRateMonthSelectChange() {
    let target = document.querySelector('select[name="occupation-rate-month-picker"]');
    let value = target.value;
    let res = await fetch(`${window.location}/occupation?month=${value}`)
                        .then(async res => await res.json())
                        .catch(err => console.error(err));
    let caption = document.querySelector('caption[name="occupation-rate-caption"]');
    let eles = res.rates;
    let container = document.querySelector('tbody[name="occupation-rate-items-container"]');

    if (eles.length == 0) {
        caption.innerText = "Nothing found";
        container.innerHTML = "";
        return;
    }

    let dom;

    caption.innerText = "";
    dom = eles.map((ele, index) => `
        <tr>
            <td scope="row">${index + 1}</td>
            <td>${ele.name}</td>
            <td>${ele.total}</td>
            <td>${ele.percentage}%</td>
        </tr>
    `).join('');
    container.innerHTML = dom;

    return;
}

var global_item_id;
var globalCDItemId;

window.addEventListener('load', function() {
    global_item_id = Array.from(document.querySelectorAll("[name='rd-item']")).length;
    globalCDItemId = Array.from(document.querySelectorAll("[name='cd-item-container']")).length;
    onMonthSelectChange();
    onOccupationRateMonthSelectChange();
});