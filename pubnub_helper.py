import os
from datetime import datetime, timezone, timedelta
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from db import users_collection
from bson.objectid import ObjectId

pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-8ed390d9-dba9-407a-b13b-908241df610f"
pnconfig.publish_key = "pub-c-827567a7-63a1-44c0-8e1b-cd2ad828986d"
pnconfig.secret_key = "sec-c-NmM0OTU0MDYtMGE5Zi00YTM0LThiOGEtZjViM2MyMGZlNmVj"
pnconfig.uuid = "homeguard-server"
pnconfig.ssl = True

pubnub = PubNub(pnconfig)

class PubNubCallback(SubscribeCallback):
    def message(self, pubnub, message):
        msg = message.message
        print(f"Received message: {msg}")

        device_id = msg.get("device_id")
        if not device_id:
            print("Error: No device_id provided.")
            return

        # Find user linked to this device_id
        user = users_collection.find_one({"devices": device_id})
        if not user:
            print(f"No user found for device_id: {device_id}")
            return

        user_id = user["user_id"]
        now = datetime.now(timezone.utc)

        # Check for cooldown (last notification time)
        last_notification = None
        if "notifications" in user and user["notifications"]:
            last_notification = user["notifications"][-1]  # Most recent notification
        
        if last_notification:
            last_timestamp = datetime.fromisoformat(last_notification["timestamp"])
            if (now - last_timestamp) < timedelta(seconds=30):
                print(f"Cooldown active. No notification sent for user: {user['username']}")
                return

        # Create a notification if cooldown has passed
        notification = {
            "notification_id": str(ObjectId()),
            "type": msg.get("event", "info"),
            "message": msg.get("message"),
            "timestamp": now.isoformat()
        }

        # Update user's notifications
        users_collection.update_one(
            {"user_id": user_id},
            {"$push": {"notifications": notification}}
        )
        print(f"Notification stored for user: {user['username']}")

pubnub.add_listener(PubNubCallback())
pubnub.subscribe().channels("motion-detection").execute()

def publish_message(channel_name, message):
    pubnub.publish().channel(channel_name).message(message).sync()

def get_messages():
    cursor = messages_collection.find().sort("_id", -1).limit(10)
    msgs = list(cursor)
    for m in msgs:
        m["_id"] = str(m["_id"])
    return msgs

def grant_token_for_user(user_id, read=False, write=False, ttl=60):
    try:
        builder = pubnub.grant_token().ttl(ttl)
        channel_access = Channel.id("motion-detection")
        if read:
            channel_access.read()
        if write:
            channel_access.write()

        envelope = builder.channels([channel_access]) \
            .authorized_uuid(user_id) \
            .sync()

        token = envelope.result.token
        print(f"Generated token for {user_id}: {token}")
        return token
    except Exception as e:
        print(f"Error generating token for user {user_id}: {e}")
        return None

def store_user_token(username, token):
    users_collection.update_one({"username": username}, {"$set": {"pubnub_token": token}})

def get_user_token(username):
    user = users_collection.find_one({"username": username})
    if user:
        return user.get("pubnub_token")
    return None