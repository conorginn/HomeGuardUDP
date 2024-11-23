from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-8ed390d9-dba9-407a-b13b-908241df610f"
pnconfig.publish_key = "pub-c-827567a7-63a1-44c0-8e1b-cd2ad828986d"
pnconfig.uuid = "5a3beb21-75fc-4254-96d6-9f7a7d72f8da" 
pnconfig.ssl = True

pubnub = PubNub(pnconfig)

print("PubNub initialized successfully.")
