from app import app, mail
from app.admin import *
from app.security import *
from flask import redirect


@app.route("/")
def index():
    # msg = Message("Reset your password", recipients=["ngochuy.ou@gmail.com"], sender="ngochuy.ou.services@hotmail.com")
    # msg.body = "Click here to reset your password"
    # with app.app_context():
    #     mail.send(msg)

    return render_template("index.html");


if __name__ == "__main__":
    app.run(debug=True)

