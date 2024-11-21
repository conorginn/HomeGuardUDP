from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
import RPi.GPIO as GPIO
import time
import cv2
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

# PubNub configuration
pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-8ed390d9-dba9-407a-b13b-908241df610f"  
pnconfig.publish_key = "pub-c-827567a7-63a1-44c0-8e1b-cd2ad828986d"  
pnconfig.uuid = "raspberry-pi-motion"  # Unique identifier for this client
pubnub = PubNub(pnconfig)

# Function to publish messages
def publish_message(message):
    pubnub.publish().channel("motion-detection").message(message).sync()

# PIR sensor setup
PIR_PIN = 17  # GPIO pin 
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

# Initializes the Picamera2
picam2 = Picamera2()
video_config = picam2.create_video_configuration(main={"size": (640, 480)})
picam2.configure(video_config)
picam2.start()

print("Waiting for motion...")

try:
    while True:
        # Checks for motion from the PIR sensor
        if GPIO.input(PIR_PIN):
            print("Motion detected!")
            publish_message({"event": "motion_detected", "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")})

            # Creates a filename for the video
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            encoder = H264Encoder(10000000)
            filename = FfmpegOutput(f"/home/haroldt2/motion_{timestamp}.mp4")

            # Starts recording the video
            picam2.start_recording(encoder, output=filename)

            # Records video for 5 seconds while showing the live feed
            start_time = time.time()
            while time.time() - start_time < 5:
                frame = picam2.capture_array()
                cv2.imshow("Live Camera Feed", frame)

                # Exits if 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    raise KeyboardInterrupt

            picam2.stop_recording()
            print(f"Video saved as {filename}")

        time.sleep(0.1)  # Short delay to avoid high CPU usage

except KeyboardInterrupt:
    print("\nExiting...")
finally:
    # Cleans up resources
    GPIO.cleanup()
    picam2.close()
    cv2.destroyAllWindows()
