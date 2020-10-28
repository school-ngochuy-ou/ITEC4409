from app import app
from flask import render_template, request
import app.utils as utils


@app.route("/")
def render_index():
    return render_template('index.html', categories=utils.load_categories())


@app.route("/products")
def render_products():
    return render_template('products.html', products=utils.load_products())


@app.route("/products/<int:product_id>")
def render_product_details(product_id):
    id = product_id
    product = utils.load_product(id)

    if product is None:
        return render_template('not_found.html')

    return render_template('product_details.html', model=product)


if __name__ == "__main__":
    app.run(debug=True)

