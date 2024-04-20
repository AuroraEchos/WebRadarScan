import asyncio
import json
import time
import serial_asyncio

#------------------- Utils -------------------
class DataHelper:
    def __init__(self):
        pass

    @staticmethod
    def extract_data_from_json(byte_data):
        string_data = byte_data.decode('utf-8')
        data_dict = json.loads(string_data)
        angle = data_dict['angle']
        distance = data_dict['distance']
        
        return angle, distance

    @staticmethod
    def get_current_time():
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
        return current_time

#------------------- Serial -------------------

class SerialPort:
    def __init__(self, port, baudrate, bytesize=8, parity='N', stopbits=1, timeout=1, xonxoff=False, rtscts=True, dsrdtr=True):
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.xonxoff = xonxoff
        self.rtscts = rtscts
        self.dsrdtr = dsrdtr
        self.serial = None

    async def open(self):
        self.serial = await serial_asyncio.open_serial_connection(
            url=self.port,
            baudrate=self.baudrate,
            bytesize=self.bytesize,
            parity=self.parity,
            stopbits=self.stopbits,
            timeout=self.timeout
        )

    async def write(self, data):
        self.serial[1].write(data)
        await self.serial[1].drain()

    async def read(self):
        return await self.serial[0].read(100)

    async def close(self):
        self.serial[1].close()
        await self.serial[1].wait_closed()

async def receive_data(serial_port):
    while True:
        data = await serial_port.read()
        if data:
            angle, distance = DataHelper.extract_data_from_json(data)
            print("Angle:", angle, "Distance:", distance)

async def periodic_time():
    while True:
        print("Performing a periodic task...")
        await asyncio.sleep(5)  # 模拟耗时任务，每5秒执行一次
            
async def main():
    my_serial_port = SerialPort('COM3', 115200)
    await my_serial_port.open()

    receive_task = asyncio.create_task(receive_data(my_serial_port))
    periodic_task = asyncio.create_task(periodic_time())
    
    await asyncio.gather(receive_task, periodic_task)

    await my_serial_port.close()

if __name__ == "__main__":
    asyncio.run(main())
