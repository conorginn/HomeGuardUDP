import RPi.GPIO as GPIO
import time

PIR_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

print("Monitoring action")

try:
	while True:
		if GPIO.input(PIR_PIN):
			print("Motion!")
		else:
			print("No motion")
			
		# print(f"GPIO state: {motion_detection}")
		time.sleep(0.5)

except KeyboardInterrupt:
	print("\nExiting program.")

finally:
	GPIO.cleanup()