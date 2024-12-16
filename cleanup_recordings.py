from pymongo import MongoClient
from datetime import datetime, timedelta

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"  # Update if needed
DB_NAME = "homeguard"  # Your database name
COLLECTION_NAME = "users"  # Collection with user documents

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db[COLLECTION_NAME]

# Define the time threshold (60 days ago)
threshold_date = datetime.now() - timedelta(days=60)

# Iterate through users and clean up recordings
users = users_collection.find({})
total_deleted = 0

for user in users:
    # Filter recordings to keep only recent ones
    recent_recordings = []
    for recording in user.get("recordings", []):
        try:
            # Ensure all timestamps are offset-naive
            recording_time = datetime.fromisoformat(recording["timestamp"]).replace(tzinfo=None)
            if recording_time >= threshold_date:
                recent_recordings.append(recording)
        except ValueError as e:
            print(f"Skipping invalid timestamp: {recording['timestamp']} - {e}")

    # Calculate number of deleted recordings
    deleted_count = len(user.get("recordings", [])) - len(recent_recordings)
    total_deleted += deleted_count
    
    # Update the user document with the filtered recordings
    if deleted_count > 0:
        users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"recordings": recent_recordings}}
        )
        print(f"Deleted {deleted_count} old recordings for user: {user['username']}")

print(f"Total deleted recordings: {total_deleted}")

# Close the connection
client.close()
