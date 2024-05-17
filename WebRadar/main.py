from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocket, WebSocketDisconnect
import asyncio
from typing import List
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from utils.serial_module import SerialPort, DataHelper
import serial.tools.list_ports
from serial.serialutil import SerialException

import os
import webbrowser


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

serial_port = None

async def find_available_serial_port():
    while True:
        print("正在尝试寻找端口...")
        com_ports = serial.tools.list_ports.comports()
        if any("COM3" in port.device for port in com_ports):
            print("发现可用端口，正在连接...")
            webbrowser.open("http://127.0.0.1:8000")
            return "COM3"
        await asyncio.sleep(0.5)  # 每秒检查一次

@app.on_event("startup")
async def startup_event():
    global serial_port
    while True:
        try:
            com_port = await find_available_serial_port()
            serial_port = SerialPort(com_port, 115200)
            await serial_port.open()
            asyncio.create_task(read_from_serial())
            break  # 如果没有发生异常，则跳出循环
        except SerialException as e:
            print(f"发生异常: {e}")
            print("重新寻找可用端口...")
        except PermissionError as e:
            print(f"权限错误: {e}")
            print("尝试重新寻找可用端口...")

@app.on_event("shutdown")
async def shutdown_event():
    await serial_port.close()

async def read_from_serial():
    while True:
        data = await serial_port.read()
        print(data)
        result = DataHelper.process_data(data)
        if result is not None:
            #print(result)
            await manager.broadcast(result)
        await asyncio.sleep(0.01)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        disconnected_websockets = []
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except WebSocketDisconnect:
                disconnected_websockets.append(connection)
        for connection in disconnected_websockets:
            self.disconnect(connection)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                print("WebSocket task was cancelled")
                break
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("WebSocket was disconnected")
    finally:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)