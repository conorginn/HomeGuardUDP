import os
import pathlib
import requests
import json

from pubnub_helper import get_messages, publish_message, grant_token_for_user, store_user_token, pubnub, PubNubCallback
from flask import Flask, session, redirect, request, abort, render_template, jsonify, send_file
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
from db import add_user, find_user, users_collection
from bson.objectid import ObjectId
import google.auth.transport.requests
from datetime import datetime

app = Flask(__name__)


app.secret_key = "HOMEGUARD_SECRET_KEY"


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
        print("Checking session in decorator:", dict(session))
        # Check for user_id or google_id
        if "user_id" not in session and "google_id" not in session:
            print("Unauthorized access. Session data:", dict(session))
            return abort(401)  # Unauthorized
        return function(*args, **kwargs)
    return wrapper

@app.template_filter('datetimeformat')
def datetimeformat(value):
    try:
        return datetime.fromisoformat(value).strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return value  # Fallback if formatting fails
    
@app.route("/", methods=["GET", "POST"])
def manual_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = find_user(username)
        if user and user["password"] == password:
            session["user_id"] = user["user_id"]
            session["username"] = username
            print("User logged in successfully. Session data:", dict(session))
            return redirect("/home")
        else:
            print("Login failed. Incorrect username or password.")
            return render_template("index.html", error=True)
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

@app.route("/home")
@login_is_required
def home():
    username = session.get("username") or session.get("name")
    user = find_user(username)

    if not user:
        return redirect("/")

    recordings = user.get("recordings", [])
    if recordings:
        newest_recording = recordings[-1]
        timestamp = datetime.fromisoformat(newest_recording["timestamp"].replace("Z", "+00:00"))
        newest_recording["timestamp"] = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    else:
        newest_recording = None

    return render_template("home.html", username=username, newest_recording=newest_recording)


# Settings page
@app.route("/settings")
def settings():
    username = session.get("username") or session.get("name")
    user = find_user(username)
    if not username:
        return redirect("/")
    return render_template("settings.html", user=user)

@app.route("/update_username", methods=["POST"])
def update_username():
    username = session.get("username")
    if not username:
        return {"success": False, "message": "User not logged in"}, 400

    data = request.get_json()
    new_username = data.get("username")

    if not new_username:
        return {"success": False, "message": "Invalid request data"}, 400

    # Check if the new username already exists
    if find_user(new_username):
        return {"success": False, "message": "Username already taken"}, 409

    try:
        result = users_collection.update_one(
            {"username": username}, {"$set": {"username": new_username}}
        )
        if result.modified_count > 0:
            session["username"] = new_username  # Update session with the new username
            return {"success": True, "message": "Username updated successfully!"}
        return {"success": False, "message": "Update failed"}, 500
    except Exception as e:
        return {"success": False, "message": str(e)}, 500
    

@app.route("/update_password", methods=["POST"])
def update_password():
    username = session.get("username")
    if not username:
        return {"success": False, "message": "User not logged in"}, 400

    data = request.get_json()
    new_password = data.get("password")

    if not new_password:
        return {"success": False, "message": "Invalid request data"}, 400

    try:
        result = users_collection.update_one(
            {"username": username}, {"$set": {"password": new_password}}
        )
        if result.modified_count > 0:
            return {"success": True, "message": "Password updated successfully!"}
        return {"success": False, "message": "Update failed"}, 500
    except Exception as e:
        return {"success": False, "message": str(e)}, 500
    

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


@app.route("/notifications")
def notifications():
    username = session.get("username") or session.get("name")
    user = find_user(username)
    if not username:
        return redirect("/")
    return render_template("notifications.html", user=user)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if find_user(username):
            return render_template("signup.html", error="Username already exists")

        add_user(username, password)
        return redirect("/")
    return render_template("signup.html")
    

@app.route("/recordings")
def recordings():
    username = session.get("username")
    user = find_user(username)
    
    if not user:
        return redirect("/")

    recordings = user.get("recordings", [])

    sorted_recordings = sorted(recordings, key=lambda x: x['timestamp'], reverse=True)
    
    formatted_recordings = []
    for recording in sorted_recordings:
        timestamp = datetime.fromisoformat(recording["timestamp"].replace("Z", "+00:00"))
        formatted_recordings.append({
            "file_path": recording["file_path"],
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),  
            "date": timestamp.strftime("%Y-%m-%d") 
        })

    return render_template("recordings.html", recordings=formatted_recordings)

@app.route("/register_device", methods=["POST"])
def register_device():
    user_id = session.get("user_id")
    data = request.get_json()
    device_id = data.get("device_id")

    if not device_id:
        return {"success": False, "message": "Device ID is required."}, 400

    success = register_device(user_id, device_id)
    if success:
        return {"success": True, "message": "Device registered successfully!"}
    return {"success": False, "message": "Failed to register device."}


# Logout route
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()  # Clear all session data
    return redirect("/")

    
