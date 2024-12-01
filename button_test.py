import RPi.GPIO as GPIO
import time

# Set GPIO mode
GPIO.setmode(GPIO.BCM)

# Define the button pin
button_pin = 4

# Set up the button pin as input with an internal pull-up resistor
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    print("Press the button...")
    while True:
        if GPIO.input(button_pin) == GPIO.LOW:  # Button is pressed
            print("Button Pressed!")
        time.sleep(0.1)  # Debounce delay
except KeyboardInterrupt:
    GPIO.cleanup()
    print("Exiting...")
