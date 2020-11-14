from app import app
from app.admin import *
from app.security import *
from flask import redirect


@app.route("/")
def index():
    return redirect("/admin")


if __name__ == "__main__":
    app.run(debug=True)

