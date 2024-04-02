import asyncio
import binascii
from pyserial_asyncio import serial_asyncio

class SerialPort:
    def __init__(self, port, baudrate, bytesize=8, parity='N', stopbits=1, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
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
            print("接收到的原始内容：",data)
            #hex_data = binascii.hexlify(data).decode()
            #print("解码后的内容：",hex_data)

async def main():
    my_serial_port = SerialPort('COM1', 9600)
    await my_serial_port.open()

    receive_task = asyncio.create_task(receive_data(my_serial_port))
    await receive_task

    await my_serial_port.close()

if __name__ == "__main__":
    asyncio.run(main())
