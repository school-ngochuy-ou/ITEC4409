from app import app, mail
from app.admin import *
from app.user import *
from flask import redirect


@app.route("/")
def index():

    return render_template("index.html");


if __name__ == "__main__":
    app.run(debug=True)

