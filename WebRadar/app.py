from flask import Flask, render_template
import random
import threading
from flask_socketio import SocketIO
import time

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/', methods = ['GET', 'POST'])
def index():
    return render_template('index.html')


def send_data_to_frontend():
    while True:
        try:
            distance = random.randint(0, 4000)
            angle = random.randint(0, 180)

            socketio.emit('update_data', {'distance': distance, 'angle': angle})   
            
            # 每隔100ms发送一次数据
            time.sleep(0.5)
        
        except Exception as e:
            print("Error sending data to frontend:", e)

if __name__ == '__main__':
    send_data_thread = threading.Thread(target=send_data_to_frontend)
    send_data_thread.daemon = True
    send_data_thread.start()

    socketio.run(app, debug=True)
    