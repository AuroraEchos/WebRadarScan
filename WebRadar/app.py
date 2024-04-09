from flask import Flask, render_template, request, redirect, url_for
from gevent import pywsgi


app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    print("http://127.0.0.1:5000")
    server = pywsgi.WSGIServer(('127.0.0.1', 5000), app)
    server.serve_forever()
    