import os
import pathlib
import requests
import json

from pubnub_helper import subscribe_to_channel, get_messages, publish_message, grant_token_for_user, store_user_token
from flask import Flask, session, redirect, request, abort, render_template, jsonify
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
from db import add_user, find_user, users_collection
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

@app.route("/update_username", methods=["POST"])
def update_username():
    username = session.get("user")

    data = request.get_json()
    if not data or not data.get("username"):
        return {"success": False, "message": "Invalid request data"}, 400

    new_name = data.get("username")

    # Check if the new username is already taken
    existing_user = find_user(new_name)
    if existing_user:
        return {"success": False, "message": "Username already taken"}, 409

    try:
        result = users_collection.update_one({"username": username}, {"$set": {"username": new_name}})
        if result.modified_count > 0:
            session["user"] = new_name
            return {"success": True}
        return {"success": False, "message": "Update failed"}, 500
    except Exception as e:
        return {"success": False, "message": str(e)}, 500
    

@app.route("/update_password", methods=["POST"])
def update_password():
    username = session.get("user")
    if not username:
        return {"success": False, "message": "User not logged in"}, 400

    data = request.get_json()
    if not data or not data.get("password"):
        return {"success": False, "message": "Invalid request data"}, 400

    new_password = data.get("password")

    try:
        result = users_collection.update_one({"username": username}, {"$set": {"password": new_password}})
        if result.modified_count > 0:
            return {"success": True}
        return {"success": False, "message": "Update failed"}, 500
    except Exception as e:
        return {"success": False, "message": str(e)}, 500
    

@app.route("/test_pubnub", methods=["GET"])
def test_pubnub():
    channel_name = "motion-detection"  
    subscribe_to_channel(channel_name)
    return f"Subscribed to channel: {channel_name}"

@app.route("/send_message", methods=["POST"])
def send_message():
    channel_name = "motion-detection" 
    message = {"text": "Hello from HomeGuard!"}
    publish_message(channel_name, message)
    return "Message sent successfully!"

@app.route("/received_messages", methods=["GET"])
def received_messages():
    """
    Route to display received messages.
    """
    messages = get_messages()
    return jsonify({"messages": messages})

@app.route("/grant_access/<username>", methods=["POST"])
def grant_access(username):
    current_user = session.get("user") or session.get("name")
    # Only admin can grant tokens
    if current_user != "admin":
        return abort(403, "Not authorized")

    # Grant read/write access for demonstration
    token = grant_token_for_user(username, read=True, write=True, ttl=60)
    store_user_token(username, token)
    return jsonify({"message": "Token granted", "token": token})

@app.route("/get_messages", methods=["GET"])
def get_messages_route():
    # Use the get_messages() function from pubnub_helper to return DB messages
    msgs = get_messages()
    return jsonify(msgs)

@app.route("/motion")
def motion_page():
    # Renders motion.html which will poll /get_messages
    return render_template("motion.html")

def assign_tokens_to_all_users():
    users = users_collection.find()
    for user in users:
        username = user["username"]
        if "pubnub_token" not in user or not user["pubnub_token"]:
            print(f"Generating token for user: {username}")
            token = grant_token_for_user(user_id=username, read=True, write=True)
            if token:
                store_user_token(username, token)
                print(f"Token assigned to {username}: {token}")
            else:
                print(f"Failed to generate token for {username}.")

assign_tokens_to_all_users()


# Logout route
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()  # Clear all session data
    return redirect("/")
