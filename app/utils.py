import json


def load_categories():
    with open('mock/category.json') as f:
        return json.load(f)


def load_products(kw=None, from_price=None, to_price=None):
    with open('mock/products.json') as f:
        products = json.load(f)

        if kw:
            products = [p for p in products if p["name"].find(kw) >= 0]

        if from_price and to_price:
            from_price = float(from_price)
            to_price = float(to_price)
            products = [p for p in products if p["price"] >= from_price and p["price"] <= to_price]

        return products


def load_product(id):
    with open('mock/products.json') as f:
        products = json.load(f)

    for p in products:
        if p["id"] == id:
            return p

    return None
