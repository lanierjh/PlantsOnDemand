# Importing necessary modules
import os
import pathlib
import flask
from flask import Flask, redirect, url_for, request, render_template, session, abort
import secrets 
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport import requests
from google.auth.transport.requests import Request
from google.oauth2 import id_token
import os
import pathlib
import requests
from cachecontrol import CacheControl
import requests
from pip._vendor import cachecontrol
import google.auth.transport.requests

# Creating a Flask application instance
app = Flask(__name__)

# Generating a secret key using the secrets module (not currently used in the code)
secret_key = secrets.token_hex(32)
print(secret_key)

# Google Client ID obtained from the Google Developer Console
GOOGLE_CLIENT_ID = "138083707001-9rt68g745qcbjuhisjumsf6hnle2111s.apps.googleusercontent.com"

# Constructing the path for the 'client_secret.json' file using the pathlib module
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

# Creating a Flow instance for OAuth 2.0 authentication with Google
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", 
            "https://www.googleapis.com/auth/userinfo.email", 
            "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)
# "https://www.googleapis.com/auth/user.addresses.read" maybe if we decide to add the location another useful one owould be calendar

# Creating a decorator function that checks if the user is in session before accessing protected areas
def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()
    return wrapper

# Route for displaying the login page
@app.route("/login_page")
def login_page():
    return render_template("login.html")

# Route for initiating the login process with Google OAuth
@app.route("/login/google")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route("/callback")
def callback():
    # This function should handle data received from Google endpoint
    # An "endpoint" is a specific URL on a web server where data can be accessed.
    # In this case, Google's OAuth 2.0 endpoint is where the user is redirected
    # after granting permission to your application.

    # Override the OAUTHLIB_INSECURE_TRANSPORT variable for local development
    # this is a quick fix to it for only local development
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Fetch the access token from Google after the user grants permission
    flow.fetch_token(authorization_response=request.url)

    # Checking if the state returned by Google matches the one stored in the session
    if not session["state"] == request.args["state"]:
        abort(500) # state doesn't match

    # Obtaining the credentials containing the access token and other information
    credentials = flow.credentials

    # Create a request session with caching for better performance
    request_session = requests.Session()
    cached_session = CacheControl(request_session)
    token_request = Request(session=cached_session)

    # Verify the ID token to get user information
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    # Save user information in the session for future use
    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    print(id_info)
    #session["email_adress"] = id_info.get("e")

    # Redirect to the protected area after successful authentication
    return redirect("/protected_area")

# Route to clear the local session for the user (log out)
# just redirects to home page 
@app.route("/signout")
def logout():
    session.clear()
    return redirect("/")

# Route for the home page
@app.route("/")
def home():
    return render_template('home.html')

# Route for displaying the protected area after successful login
@app.route("/protected_area")
@login_is_required
def protected_area():
    return render_template('protected_area.html')


if __name__ == "__main__":
    # Setting the app's secret key for session management: might have questions about the security of this procedure?
    app.secret_key = "a16d378de074a6f025a0015ebbf8c490dbfa6e2545436920823c6248c2f53256"
    # Running the Flask application in debug mode
    app.run(debug=True)
