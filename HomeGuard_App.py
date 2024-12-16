from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
import subprocess
import time
import os

# PubNub Configuration
pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-8ed390d9-dba9-407a-b13b-908241df610f"
pnconfig.publish_key = "pub-c-827567a7-63a1-44c0-8e1b-cd2ad828986d"
pnconfig.secret_key = "sec-c-NmM0OTU0MDYtMGE5Zi00YTM0LThiOGEtZjViM2MyMGZlNmVj"
pnconfig.uuid = "pi_motion_sensor_1"
pubnub = PubNub(pnconfig)

# Server Information for SCP Transfer
SERVER_USER = "ubuntu"  # Server username
SERVER_HOST = "52.18.71.193"  # Server IP or hostname
SERVER_PATH = "/var/www/homeguard_website/static/recordings"  # Server's video directory

# Recording Directory on the Pi
LOCAL_PATH = "/home/haroldt2/recordings"
if not os.path.exists(LOCAL_PATH):
    os.makedirs(LOCAL_PATH)

# Function to Transfer File via SCP
def transfer_file(file_path):
    try:
        print(f"Transferring {file_path} to server...")
        scp_command = [
            "scp", file_path, f"{SERVER_USER}@{SERVER_HOST}:{SERVER_PATH}"
        ]
        subprocess.run(scp_command, check=True)
        print("File transferred successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during SCP transfer: {e}")
        return False

# Function to Send Metadata via PubNub
def publish_metadata(filename, timestamp):
    try:
        pubnub.publish().channel("motion-detection").message({
            "event": "Motion Alert",
            "message": "Motion detected at front door!",
            "device_id": "pi_motion_sensor_1",
            "file_path": filename,  # Only filename
            "timestamp": timestamp
        }).sync()
        print("Metadata published to PubNub.")
    except Exception as e:
        print(f"Error sending metadata to PubNub: {e}")

# Main Script
try:
    print("Starting motion detection script...")
    # Initialize Camera
    picam2 = Picamera2()
    video_config = picam2.create_video_configuration(main={"size": (640, 480)})
    picam2.configure(video_config)

    while True:
        # Generate file names
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        h264_file = os.path.join(LOCAL_PATH, f"motion_{timestamp}.h264")
        mp4_file = os.path.join(LOCAL_PATH, f"motion_{timestamp}.mp4")

        # Simulate motion detection
        print("Motion detected! Recording video...")
        encoder = H264Encoder(bitrate=1000000)
        output = FileOutput(h264_file)

        try:
            # Start Recording
            picam2.start_recording(encoder, output)
            time.sleep(5)  # Record for 5 seconds
            picam2.stop_recording()
            print(f"Recording saved: {h264_file}")
        except Exception as e:
            print(f"Error during recording: {e}")
            continue

        # Convert H.264 to MP4
        print("Converting video to MP4 format...")
        try:
            subprocess.run([
                "ffmpeg", "-i", h264_file, "-c:v", "copy", mp4_file
            ], check=True)
            os.remove(h264_file)  # Delete the H.264 file
            print(f"Conversion complete: {mp4_file}")
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg conversion failed: {e}")
            continue

        # Transfer File to Server
        if transfer_file(mp4_file):
            # Publish Metadata to PubNub after successful transfer
            filename = os.path.basename(mp4_file)  # Only send the filename
            publish_metadata(filename, time.strftime("%Y-%m-%d %H:%M:%S"))

            # Clean up local MP4 file
            os.remove(mp4_file)
            print("Local MP4 file deleted after successful transfer.")
        else:
            print("File transfer failed. Skipping metadata publishing.")

        # Delay before checking for motion again
        time.sleep(10)

except KeyboardInterrupt:
    print("Script interrupted. Exiting...")
finally:
    picam2.close()
    print("Camera closed.")
