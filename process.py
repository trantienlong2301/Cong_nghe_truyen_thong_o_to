import socket
import time
import threading
import sys
import struct
import numpy as np
import zlib

Length = float(sys.argv[1])
Width = float(sys.argv[2])
Id = int(sys.argv[3])

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

data = {
    "ID": None,
    "Type": None,
    "Chieu dai": None,
    "Chieu rong": None,
    "Kinh do": None,
    "Vi do": None,
    "Van toc": None,
    "Huong": None,
    "Thoi gian": None
}
message = bytearray(49)
message[0:4] = b'\xA1\xB2\xC3\xD4'
message[41:45] = b'\xE5\xF6\x7A\x8B'
message[4:8] = struct.pack('<I', Id)
message[9:13] = struct.pack('<f', Length)
message[13:17] = struct.pack('<f', Width)

print("[Sender] UDP Sender started")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
count_periodic = 0
count_warning = 0

def periodic_task():
    period = 1
    next_time = time.perf_counter()

    while True:
        next_time += period
        vi_tri = np.random.uniform(-180, 180, size=3)
        van_toc = np.random.uniform(10,80)
        date = time.time()
        message[8] = 0x00
        message[17:21] = struct.pack('<f', vi_tri[0])
        message[21:25] = struct.pack('<f', vi_tri[1])
        message[25:29] = struct.pack('<f', van_toc)
        message[29:33] = struct.pack('<f', vi_tri[2])
        message[33:41] = struct.pack('<f', time)
        message[45::] = zlib.crc32(message[0:45])
        sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
        count_periodic +=1
        sleep_time = next_time - time.perf_counter()
        if sleep_time > 0:
            time.sleep(sleep_time)

def warning_task():
    period = 0.1
    next_time = time.perf_counter()

    while True:
        next_time +=period
        a = np.random.randint(0,30)
        if a ==1:
            vi_tri = np.random.uniform(-180, 180, size=3)
            van_toc = np.random.uniform(10,80)
            date = time.time()
            message[8] = 0x01
            message[17:21] = struct.pack('<f', vi_tri[0])
            message[21:25] = struct.pack('<f', vi_tri[1])
            message[25:29] = struct.pack('<f', van_toc)
            message[29:33] = struct.pack('<f', vi_tri[2])
            message[33:41] = struct.pack('<f', time)
            message[45::] = zlib.crc32(message[0:45])
            sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
            count_warning +=1

        sleep_time = next_time - time.perf_counter()
        if sleep_time > 0:
            time.sleep(sleep_time)

if __name__ == "__main__":
    periodic_thread = threading.Thread(
        target=periodic_task,
        daemon=True
    )
    periodic_thread.start()

    warning_thread = threading.Thread(
        target=warning_task,
        daemon=True
    )
    warning_thread.start()

    while True:
        packet, addr = sock.recvfrom(1024)

        if len(packet) != 49:
            print("Invalid packet length")
            continue

        # ===== Kiểm tra header =====
        if packet[0:4] != b'\xA1\xB2\xC3\xD4':
            print("Invalid header")
            continue

        # ===== Kiểm tra tail =====
        if packet[41:45] != b'\xE5\xF6\x7A\x8B':
            print("Invalid tail")
            continue

        # ===== Kiểm tra CRC =====
        crc_recv = struct.unpack('<I', packet[45:49])[0]
        crc_calc = zlib.crc32(packet[0:45])

        if crc_recv != crc_calc:
            print("CRC error")
            continue

        # ===== Giải mã dữ liệu =====
        data = {
            "ID": struct.unpack('<f', packet[4:8])[0],
            "Type": packet[8],
            "Chieu dai": struct.unpack('<f', packet[9:13])[0],
            "Chieu rong": struct.unpack('<f', packet[13:17])[0],
            "Kinh do": struct.unpack('<f', packet[17:21])[0],
            "Vi do": struct.unpack('<f', packet[21:25])[0],
            "Van toc": struct.unpack('<f', packet[25:29])[0],
            "Huong": struct.unpack('<f', packet[29:33])[0],
            "Thoi gian": struct.unpack('<d', packet[33:41])[0],
        }

        
