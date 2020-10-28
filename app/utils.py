import json


def load_categories():
    with open('mock/category.json') as f:
        return json.load(f)


def load_products():
    with open('mock/products.json') as f:
        return json.load(f)


def load_product(id):
    with open('mock/products.json') as f:
        products = json.load(f)

    for p in products:
        if p["id"] == id:
            return p

    return None
