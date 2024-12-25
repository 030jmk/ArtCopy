import os  
import json  
from flask import Flask, render_template, jsonify  
from flask_socketio import SocketIO  
import numpy as np  
import random  
import RPi.GPIO as GPIO  
import eventlet  
import queue  
from threading import Lock, Thread  
from datetime import datetime, timedelta  
import subprocess 
import time
  
eventlet.monkey_patch()  
  
app = Flask(__name__)  
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")  
  
BUTTON_PIN = 21  
GPIO.setmode(GPIO.BCM)  
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  
  
rows, cols = 25, 25
grid = np.full((rows, cols, 3), 255, dtype=int)  
  
json_dir = 'button_press_logs'  
os.makedirs(json_dir, exist_ok=True)  
  
current_unix_time = int(datetime.now().timestamp())  
json_file_path = os.path.join(json_dir, f'{current_unix_time}.json')  
  
button_press_data = []  
  
button_queue = queue.Queue()  
grid_lock = Lock()  

def launch_chromium():  
    time.sleep(10)
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
    while True:  
        eventlet.sleep(60)  
        with open(json_file_path, 'w') as f:  
            json.dump(button_press_data, f, indent=4)  
  
def change_random_cell():  
    with grid_lock:  
        try:  
            i, j = random.randint(0, rows - 1), random.randint(0, cols - 1)  
            rgb = [random.randint(0, 255) for _ in range(3)]  
            grid[i, j] = rgb  
            grid_list = grid.tolist()  
            socketio.emit('update_grid', {'grid': grid_list})  
  
            button_press_data.append({  
                'timestamp': int(datetime.now().timestamp()),  
                'row': i,  
                'col': j,  
                'rgb': rgb  
            })  
  
            print(f"Changed cell ({i}, {j}) to new color: {rgb}")  
  
        except Exception as e:  
            print(f"Error in change_random_cell: {e}")  
  
def button_pressed_callback(channel):  
    try:  
        print("Button pressed")  
        button_queue.put_nowait(True)  
    except queue.Full:  
        pass  
  
def process_button_queue():  
    while True:  
        try:  
            button_queue.get(timeout=0.1)
            change_random_cell()  
        except queue.Empty:  
            eventlet.sleep(0.1)  
        except Exception as e:  
            print(f"Error processing button queue: {e}")  
            eventlet.sleep(0.1)  
  
GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING,   
                     callback=button_pressed_callback,   
                     bouncetime=300)  
  
@app.route('/')  
def index():  
    return render_template('index.html')  
  
@app.route('/grid')  
def get_grid():  
    with grid_lock:  
        return jsonify(grid=grid.tolist())  
  
@app.route('/button_presses')  
def get_button_presses():  
    return jsonify(button_presses=button_press_data)  
  
if __name__ == '__main__':  
    try:  
        socketio.start_background_task(process_button_queue)  
        socketio.start_background_task(write_to_json_periodically) 
        socketio.start_background_task(launch_chromium) 
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)  

    finally:  
        GPIO.cleanup()  