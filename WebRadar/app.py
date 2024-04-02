from flask import Flask, render_template
from flask_socketio import SocketIO
from threading import Thread
import time

from function.sql import *

app = Flask(__name__)
socketio = SocketIO(app)

db = Database()
data_processor = DataProcessing(db)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

def send_data():
    for distance, angle in data_processor.stream_data_from_database(table_name='radar_data', column_names=['distance', 'angle']):
        socketio.emit('update_data', {'distance': distance, 'angle': angle})
        time.sleep(0.5)

if __name__ == '__main__':
    t = Thread(target=send_data)
    t.daemon = True  # 设置为守护线程，程序退出时自动关闭
    t.start()
    #print("http://127.0.0.1:5000")
    socketio.run(app, debug=True)
