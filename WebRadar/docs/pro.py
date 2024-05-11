import re

def process_data(data):
    lines = data.split(b'\n')
    for line in lines:
        line = line.strip().decode('utf-8')  # 去除首尾空白字符并解码
        if line:
            if line == 'ERROR':
                result = {"Angle": 0, "Distance": 0}
            else:
                match = re.match(r'Angle:(\d+)Distance:(\d+)', line)
                if match:
                    angle = int(match.group(1))
                    distance = int(match.group(2))
                    result = {"Angle": angle, "Distance": distance}
                else:
                    result = None
            print(result)

# 测试
data = b'Angle:082Distance:0193\nAngle:083Distance:0662\nERROR\n'
process_data(data)
