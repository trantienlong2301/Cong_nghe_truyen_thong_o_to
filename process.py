import socket
import sys
import threading
import time
import struct
import random
import msvcrt

if len(sys.argv) < 2:
    print(" Thiếu tham số, dùng giá trị mặc định để test")
    length = 2.0
    width  = 1.5
    car_id = "TEST"
else:
    
    car_id = int(sys.argv[1])

SERVER_ADDR = ("127.0.0.1", 6000)

MCAST_GRP = "224.1.1.1"
MCAST_PORT = 5007

lat = lon = speed = heading = struct.pack("<f", 0)
warning = threading.Event()

def crc16_ccitt(data: bytes, poly=0x1021, init=0xFFFF):
    crc = init
    for b in data:
        crc ^= (b << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc

# ===== nhận multicast =====
def receive_multicast():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    #  BẮT BUỘC trên Windows
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except:
        pass  # Windows có thể không hỗ trợ

    sock.bind(("", MCAST_PORT))

    mreq = struct.pack(
        "4sl",
        socket.inet_aton(MCAST_GRP),
        socket.INADDR_ANY
    )
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        data, _ = sock.recvfrom(1024)
        recv_crc = struct.unpack("<H", data[-2:])[0]
        calc_crc = crc16_ccitt(data[:-2])
        if recv_crc != calc_crc:
            print(" CRC lỗi")
            continue

        id = data[1]
        if (id == car_id) :
            continue
        lat, lon, speed, heading = struct.unpack("<ffff", data[2:18])
        type = data[0]
        if (type == 0):
            print(
                f"Xe {id} | "
                f"Kinh do={lat:.6f} Vi do={lon:.6f} "
                f"Van toc ={speed:.2f} Huong={heading:.1f}"
            )
        else:
            print(
                f"Warning "
                f"Xe {id} | "
                f"Kinh do={lat:.6f} Vi do={lon:.6f} "
                f"Van toc ={speed:.2f} Huong={heading:.1f}"
            )



# ===== gửi dữ liệu =====
def send_data():
    global lat, lon, speed,heading,warning
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while True:
        if(not warning.is_set()):
            lat = random.uniform(10.0, 11.0)
            lon = random.uniform(106.0, 107.0)
            speed = random.uniform(0, 30)
            heading = random.uniform(0, 360)
            type = 0x00
        else:
            type = 0x01
            speed = 0
        payload = struct.pack(
            "<ffff",   # little-endian float
            lat, lon, speed, heading
        )
    
        body = struct.pack("B", type) + struct.pack("B", car_id) + payload
        crc = crc16_ccitt(body)
        package = body + struct.pack("<H", crc)
        sock.sendto(package, SERVER_ADDR)
        time.sleep(0.1)

def keyboard_listener():
    global warning
    print("Nhan SPACE de bat/tat WARNING")

    while True:
        if msvcrt.kbhit():          # có phím được nhấn
            key = msvcrt.getch()
            if key == b' ':         # SPACE
                if warning.is_set():
                    warning.clear()
                    print("WARNING OFF")
                else:
                    warning.set()
                    print("WARNING ON")
        time.sleep(0.05)

if __name__ == "__main__":
    print(f" Xe {car_id} khởi động",flush=True)

    threading.Thread(target=receive_multicast, daemon=True).start()
    threading.Thread(
        target=keyboard_listener,
        daemon=True
    ).start()
    send_data()
