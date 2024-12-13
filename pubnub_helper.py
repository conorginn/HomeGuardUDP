import os
from datetime import datetime, timezone
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
        print(f"Received message from PubNub: {msg}")
        msg["received_at"] = datetime.now(timezone.utc).isoformat()

        # Retrieve the currently logged-in user's `user_id` from the session
        user_id = session.get("user_id")
        if not user_id:
            print("No user logged in. Cannot store notification.")
            return

        # Add the message to the user's notifications
        try:
            notification = {
                "notification_id": str(ObjectId()),
                "type": msg.get("event", "info"),
                "message": msg,
                "timestamp": msg["received_at"]
            }
            # Update the user's document in the `users` collection
            users_collection.update_one(
                {"user_id": user_id},  # Match the user by their `user_id`
                {"$push": {"notifications": notification}}
            )
            print(f"Notification successfully stored for user_id: {user_id}")
        except Exception as e:
            print(f"Error storing notification for user_id {user_id}: {e}")

    def presence(self, pubnub, presence):
        print(f"Presence event: {presence.event}")

    def status(self, pubnub, status):
        if status.is_error():
            print(f"PubNub Error: {status.error_data}")
        else:
            print("PubNub connection status:", status.category)

pubnub.add_listener(PubNubCallback())

def subscribe_to_channel(channel_name):
    pubnub.subscribe().channels(channel_name).execute()

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