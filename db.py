from pymongo import MongoClient
import uuid

client = MongoClient("mongodb://localhost:27017/")
db = client["homeguard"]

# Collections
users_collection = db["users"]
messages_collection = db["messages"]

def add_user(username, password):
    user = {
        "username": username,
        "password": password,
        "recordings": [],
        "notifications": [],
        "pubnub_token": None
    }
    return users_collection.insert_one(user)

def find_user(username):
    return users_collection.find_one({"username": username})

def add_notification(user_id, notification_type, message):
    notification = {
        "notification_id": str(uuid.uuid4()),
        "type": notification_type,
        "message": message
    }
    return users_collection.update_one(
        {"_id": user_id},
        {"$push": {"notifications": notification}}
    )