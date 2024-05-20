import serial_asyncio
import re

#------------------- Helper -------------------
last_data = None
class DataHelper:
    def __init__(self):
        pass
    
    @staticmethod
    def process_data(data):
        global last_data
        
        lines = data.split(b'\n')
        for line in lines:
            line = line.strip().decode('utf-8')
            if line:
                if line == 'ERROR':
                    result = {"angle": 0, "distance": 0}
                else:
                    match = re.match(r'Angle:(\d+)Distance:(\d+)', line)
                    if match:
                        angle = int(match.group(1))
                        distance = int(match.group(2))
                        if angle != last_data:
                            result = {"angle": angle, "distance": distance}
                            last_data = angle
                        else:
                            result = None
                    else:
                        result = None
                return result

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

