from flask import Flask, render_template
from flask_socketio import SocketIO
import numpy as np
import random
from flask import jsonify
import eventlet
from threading import Lock

# Monkey patch before any other imports
eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

# Grid setup
rows, cols = 10, 10
grid = np.full((rows, cols, 3), 255, dtype=int)
grid_lock = Lock()

def change_random_cell():
    with grid_lock:
        try:
            i, j = random.randint(0, rows - 1), random.randint(0, cols - 1)
            grid[i, j] = [random.randint(0, 255) for _ in range(3)]
            grid_list = grid.tolist()
            socketio.emit('update_grid', {'grid': grid_list})
            print(f"Changed cell ({i}, {j}) to new color")
            return True
        except Exception as e:
            print(f"Error in change_random_cell: {e}")
            return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/grid')
def get_grid():
    with grid_lock:
        return jsonify(grid=grid.tolist())

@app.route('/select_cell', methods=['POST'])
def select_cell():
    if change_random_cell():
        return jsonify(success=True)
    return jsonify(success=False), 500

if __name__ == '__main__':
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("Shutting down...")
