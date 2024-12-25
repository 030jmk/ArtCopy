from flask import Flask
import RPi.GPIO as GPIO
import requests
import time

app = Flask(__name__)

# GPIO Setup
BUTTON_PIN = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Configuration
MAIN_SERVER_URL = 'http://192.168.1.XXX:5000'  # Replace with Pi #2's IP address

def button_pressed_callback(channel):
    try:
        print("Button pressed - requesting cell selection")
        response = requests.post(f'{MAIN_SERVER_URL}/select_cell')
        if response.status_code == 200:
            print("Cell selection request successful")
        else:
            print(f"Error: Server returned status code {response.status_code}")
    except Exception as e:
        print(f"Error sending request: {e}")

# Set up GPIO event detection
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, 
                     callback=button_pressed_callback, 
                     bouncetime=300)

if __name__ == '__main__':
    try:
        print("Button Pi running. Press Ctrl+C to exit.")
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        GPIO.cleanup()
