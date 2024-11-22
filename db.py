from pymongo import MongoClient


client = MongoClient("mongodb://localhost:27017/")
db = client["homeguard"]

# Collections
users_collection = db["users"]
# pre_recorded_messages_collection = db["pre_recorded_messages"]

def add_user(username, password):
    user = {
        "username": username,
        "password": password,
        "recordings": [],
        "notifications": []
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