from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback

# PubNub Configuration
pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-8ed390d9-dba9-407a-b13b-908241df610f"  
pnconfig.publish_key = "pub-c-827567a7-63a1-44c0-8e1b-cd2ad828986d"     
pnconfig.uuid = "5a3beb21-75fc-4254-96d6-9f7a7d72f8da"  
pnconfig.ssl = True

pubnub = PubNub(pnconfig)

messages = []

class PubNubCallback(SubscribeCallback):
    def message(self, pubnub, message):
        print(f"Received message: {message.message}")
        messages.append(message.message)  # Store messages in memory

    def presence(self, pubnub, presence):
        print(f"Presence event: {presence.event}")

    def status(self, pubnub, status):
        if status.is_error():
            print(f"Error: {status.error_data}")

# Initialize the listener
pubnub.add_listener(PubNubCallback())

# Function to subscribe to a channel
def subscribe_to_channel(channel_name):
    pubnub.subscribe().channels(channel_name).execute()

# Function to publish a message
def publish_message(channel_name, message):
    pubnub.publish().channel(channel_name).message(message).sync()

def get_messages():
    return messages
