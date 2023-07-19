import os
import pathlib
import flask
from flask import Flask, redirect, url_for, request, render_template, session, abort
import secrets 
from google_auth_oauthlib.flow import Flow

app = Flask(__name__)

# way to create a secret key: tho we don't use it but we must remember
secret_key = secrets.token_hex(32)
print(secret_key)

GOOGLE_CLIENT_ID = "138083707001-9rt68g745qcbjuhisjumsf6hnle2111s.apps.googleusercontent.com"

client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

# which API's the user will have access to 
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)

# we create a wrapper to help us prevent a user who isn't in session from accessing a protected area
def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()
    return wrapper

# login has the same explanation with logout 
@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

# call back receives data from the Google endpoint
@app.route("/callback")
def callback():
    pass

# clear our local session from our user
@app.route("/signout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/protected_area")
@login_is_required
def protected_area():
    return render_template('protected_area.html')

if __name__ == "__main__":
    app.secret_key = "a16d378de074a6f025a0015ebbf8c490dbfa6e2545436920823c6248c2f53256"
    app.run(debug=True)
