import asyncio
import pymysql
import json
import time
import serial_asyncio
import serial
import re

#------------------- MySQL -------------------
class DatabaseManager:
    def __init__(self, host='127.0.0.1', port=3306, user='root', passwd='root123', charset='utf8', db='radarscan'):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.charset = charset
        self.db = db

    def connect(self):
        """ 创建数据库连接 """
        return pymysql.connect(host=self.host,
                               port=self.port,
                               user=self.user,
                               passwd=self.passwd,
                               charset=self.charset,
                               db=self.db)

    def execute_query(self, query, *args):
        """ 执行查询并返回结果 """
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, args)
                    return cursor.fetchall()
        except pymysql.Error as e:
            print(f"Error executing query: {e}")
            return None

    def insert_data(self, table_name, columns, values):
        """
        插入数据到指定表

        Args:
        - table_name: 表格名称
        - columns: 列名列表，例如 ['column1', 'column2']
        - values: 值列表，例如 [value1, value2]

        Returns:
        - 无
        """
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s']*len(columns))})"
                    cursor.execute(insert_query, values)
                    conn.commit()
        except pymysql.Error as e:
            print(f"Error inserting data: {e}")

#------------------- Helper -------------------
last_data = None
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
    
    @staticmethod
    def detect_serial_ports():
        ports = serial.tools.list_ports.comports()
        if not ports:
            return []
        
        port_list = []
        for port in ports:
            port_info = {
                "name": port.name,
                "description": port.description,
                "device": port.device
            }
            port_list.append(port_info)
        return port_list
    
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

async def receive_data(serial_port):
    while True:
        current_time = DataHelper.get_current_time()
        DBM = DatabaseManager()
        data = await serial_port.read()
        if data:
            DBM.insert_data("src_data", ['src_data', 'time'], [data, current_time])

            try:
                angle, distance = DataHelper.extract_data_from_json(data)
                DBM.insert_data("pro_data", ['distance', 'angle', 'time'], [distance, angle, current_time])
                print("Angle:", angle, "Distance:", distance)
            except json.JSONDecodeError as e:
                print("JSON decode error:", e)
            except KeyError as e:
                print("Key error in JSON data:", e)
            
async def main():
    my_serial_port = SerialPort('COM3', 9600)
    await my_serial_port.open()

    receive_task = asyncio.create_task(receive_data(my_serial_port))
    await receive_task

    await my_serial_port.close()

if __name__ == "__main__":
    asyncio.run(main())
