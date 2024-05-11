from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocket, WebSocketDisconnect
import asyncio
from typing import List
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from serial_module import SerialPort, DataHelper

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

serial_port = SerialPort('COM3', 115200)

@app.on_event("startup")
async def startup_event():
    await serial_port.open()
    asyncio.create_task(read_from_serial())

@app.on_event("shutdown")
async def shutdown_event():
    await serial_port.close()


async def read_from_serial():
    while True:
        data = await serial_port.read()
        result = DataHelper.process_data(data)
        if result is not None:
            print(result)
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