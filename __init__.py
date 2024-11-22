import os
import pathlib
import requests
import json

from flask import Flask, session, redirect, request, abort, render_template
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
from db import add_user, find_user
import google.auth.transport.requests

app = Flask(__name__)

app.secret_key = "HOMEGUARD_SECRET_KEY"

test_user = {
    "username": "user1",
    "password": "abc123"
}

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid"],
    redirect_uri="https://homeguard.website/callback"
)

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "user" not in session and "google_id" not in session:
            return abort(401)  # Unauthorized
        return function(*args, **kwargs)
    return wrapper

@app.route("/", methods=["GET", "POST"])
def manual_login():
    if request.method == "POST":
        # Retrieve the username and password from the form
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Search for the user in the database
        user = find_user(username)
        
        if user and user["password"] == password:
            # If the user is found and the password matches, log them in
            session["user"] = username
            return redirect("/home")
        else:
            # Render the login page with an error message if login fails
            return render_template("index.html", error=True)
    
    # Render the login page for GET requests
    return render_template("index.html")



@app.route("/google_login")
def google_login():
    # Redirect to Google's OAuth 2.0 login
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials.id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")  
    session["name"] = id_info.get("name")
    print(session["google_id"])
    print(session["name"])
    return redirect("/home")

# Home page
@app.route("/home")
@login_is_required
def home():
    username = session.get("user") or session.get("name")  # Use username or Google name
    return render_template("home.html", username=username)

# Settings page
@app.route("/settings")
def settings():
    username = session.get("user") or session.get("name")
    user = find_user(username)
    if not user:
        return redirect("/")
    return render_template("settings.html", user=user)



# Logout route
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()  # Clear all session data
    return redirect("/")
