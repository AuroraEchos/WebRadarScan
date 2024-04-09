from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO
from datetime import datetime

import random

def generate_random_distance():
    return random.randint(0, 250)


app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/', methods = ['GET', 'POST'])
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # 在连接建立时，向客户端发送初始数据
    while True:
        distance = generate_random_distance()
        print("Sending distance:", distance)
        socketio.emit('update_data', {'data': distance})

if __name__ == '__main__':
    print("http://127.0.0.1:5000")
    socketio.run(app, debug=True)