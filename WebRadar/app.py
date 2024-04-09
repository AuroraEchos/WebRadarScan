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
            # 生成随机的雷达数据
            distance = random.randint(0, 4000)  # 随机生成一个距离值（0 到 4000 之间的整数）
            angle = random.randint(0, 360)  # 随机生成一个角度值（0 到 360 之间的整数）

            # 将生成的雷达数据发送给客户端
            socketio.emit('update_data', {'distance': distance, 'angle': angle})
            
            # 等待一段时间再继续发送数据（这里设定为每隔 1 秒发送一次）
            time.sleep(1)
        except Exception as e:
            print("Error sending data to frontend:", e)

if __name__ == '__main__':
    # 启动一个新线程，在其中定期发送数据给前端
    send_data_thread = threading.Thread(target=send_data_to_frontend)
    send_data_thread.daemon = True
    send_data_thread.start()

    socketio.run(app, debug=True)
    