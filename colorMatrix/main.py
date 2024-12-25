import os
import json
import random
import time
import queue
import subprocess
from datetime import datetime
from threading import Lock

import numpy as np
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import RPi.GPIO as GPIO
import eventlet

eventlet.monkey_patch()

# Flask and SocketIO initialization
app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

# GPIO configuration
BUTTON_PIN = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Grid configuration
ROWS, COLS = 20, 20
grid = np.full((ROWS, COLS, 3), 255, dtype=int)

# Button press logging setup
JSON_DIR = 'button_press_logs'
os.makedirs(JSON_DIR, exist_ok=True)
json_file_path = os.path.join(JSON_DIR, f"{int(datetime.now().timestamp())}.json")
button_press_data = []

# Threading and queue setup
button_queue = queue.Queue()
grid_lock = Lock()

def launch_chromium():
    """
    Launch Chromium in fullscreen mode with the web app.
    """
    time.sleep(10)  # Wait for the server to initialize
    subprocess.Popen([
        'chromium-browser',
        '--start-fullscreen',
        '--app=http://localhost:5000',
        '--noerrdialogs',
        '--disable-infobars',
        '--disable-session-crashed-bubble',
        '--disable-features=InfiniteSessionRestore',
        '--force-device-scale-factor=1'
    ])

def write_to_json_periodically():
    """
    Periodically write button press data to a JSON file.
    """
    while True:
        eventlet.sleep(60)
        with open(json_file_path, 'w') as f:
            json.dump(button_press_data, f, indent=4)

def change_random_cell():
    """
    Change a random cell in the grid to a random color and emit the update via SocketIO.
    """
    with grid_lock:
        i, j = random.randint(0, ROWS - 1), random.randint(0, COLS - 1)
        rgb = [random.randint(0, 255) for _ in range(3)]
        grid[i, j] = rgb
        socketio.emit('update_grid', {'grid': grid.tolist()})

        button_press_data.append({
            'timestamp': int(datetime.now().timestamp()),
            'row': i,
            'col': j,
            'rgb': rgb
        })
        print(f"Changed cell ({i}, {j}) to new color: {rgb}")

def button_pressed_callback(channel):
    """
    Callback for button press events. Adds an event to the queue.
    """
    try:
        print("Button pressed")
        button_queue.put_nowait(True)
    except queue.Full:
        pass

def process_button_queue():
    """
    Process button press events from the queue.
    """
    while True:
        try:
            button_queue.get(timeout=0.1)
            change_random_cell()
        except queue.Empty:
            eventlet.sleep(0.1)
        except Exception as e:
            print(f"Error processing button queue: {e}")
            eventlet.sleep(0.1)

# GPIO button press detection
GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, callback=button_pressed_callback, bouncetime=300)

# Flask routes
@app.route('/')
def index():
    """
    Render the main index page.
    """
    return render_template('index.html')

@app.route('/grid')
def get_grid():
    """
    Return the current grid as JSON.
    """
    with grid_lock:
        return jsonify(grid=grid.tolist())

@app.route('/button_presses')
def get_button_presses():
    """
    Return the logged button press data as JSON.
    """
    return jsonify(button_presses=button_press_data)

if __name__ == '__main__':
    try:
        # Start background tasks
        socketio.start_background_task(process_button_queue)
        socketio.start_background_task(write_to_json_periodically)
        socketio.start_background_task(launch_chromium)

        # Run the Flask application
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    finally:
        GPIO.cleanup()
