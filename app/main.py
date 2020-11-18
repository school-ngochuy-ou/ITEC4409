from app import app
from app.admin import *
from app.security import *
from flask import redirect


@app.route("/")
def index():

    return render_template("index.html");


if __name__ == "__main__":
    app.run(debug=True)

