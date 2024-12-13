from pymongo import MongoClient
import uuid

# Connect to the MongoDB database
client = MongoClient("mongodb://localhost:27017/")
db = client["homeguard"]
users_collection = db["users"]

# Iterate over all users and add a `user_id` field if not present
users = users_collection.find()
for user in users:
    # Generate a unique `user_id` if it doesn't already exist
    user_id = str(uuid.uuid4())
    print(f"Adding user_id {user_id} to user {user['username']}")

    # Update the user document with the new `user_id`
    users_collection.update_one({"_id": user["_id"]}, {"$set": {"user_id": user_id}})
print("All users updated with user_id!")
