import socket
import sys
import threading
from datetime import datetime
import struct
import json
import logging
# ===== SỬA IP =====
MY_NAME = "CarB"
MY_PORT = 5001

CAR_A_IP = "192.168.239.32"   # IP laptop A
CAR_C_IP = "192.168.239.10"   # IP laptop C
# ==================

NEIGHBORS = [
    (CAR_A_IP, 5000, "CarA"),
    (CAR_C_IP, 5002, "CarC"),
]
logging.basicConfig(
    filename="carA_log.txt",
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def event_id():
    return str(datetime.now().timestamp())

# ---------- PHẦN NHẬN ----------
def recv_loop():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", MY_PORT))
    server.listen(5)

    seen = set()
    print(f"📡 {MY_NAME} listening port {MY_PORT}")

    while True:
        conn, addr = server.accept()
        buf = ""

        while True:
            data = conn.recv(4096).decode("utf-8", errors="ignore")
            if not data: break
            buf += data

            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                try:
                    msg = json.loads(line)
                except:
                    continue

                if msg.get("type") != "EVENT": 
                    continue

                eid = msg.get("event_id")
                if eid in seen: 
                    continue
                seen.add(eid)

                pr = int(msg.get("priority",1))
                act = "KHẨN" if pr>=3 else "GIẢM TỐC" if pr==2 else "THÔNG TIN"

                log = f"{msg['time']} | {msg['from']} | {msg['event_name']} | {pr} | {msg['message']}"
                logging.info(log)

                print("\n=== NHẬN V2V ===")
                print("Từ      :", msg["from"])
                print("Sự kiện :", msg["event_name"])
                print("Ưu tiên :", pr)
                print("Action  :", act)
                print("Nội dung:", msg["message"])
                print("================\n")

        conn.close()

# ---------- PHẦN GỬI ----------
def send_all(name, pr, text):
    payload = {
        "type": "EVENT",
        "event_id": event_id(),
        "time": now(),
        "from": MY_NAME,
        "event_name": name,
        "priority": pr,
        "message": text
    }

    data = (json.dumps(payload, ensure_ascii=False)+"\n").encode()

    for ip, port, who in NEIGHBORS:
        try:
            s = socket.socket()
            s.settimeout(3)
            s.connect((ip, port))
            s.sendall(data)
            s.close()
            print(f"✅ Gửi tới {who}")
        except Exception as e:
            print(f"❌ Lỗi gửi {who}: {e}")

def menu():
    print(f"\n🚗 {MY_NAME}")
    print("1) Phanh gấp (3)")
    print("2) Vật cản (2)")
    print("3) Định vị (1)")
    print("0) Thoát")

# ---------- MAIN ----------
threading.Thread(target=recv_loop, daemon=True).start()

while True:
    menu()
    c = input("Chọn: ")

    if c=="1":
        send_all("EMERGENCY_BRAKE",3,"PHANH GẤP!")
    elif c=="2":
        send_all("OBSTACLE_AHEAD",2,"Có vật cản!")
    elif c=="3":
        send_all("POSITION_UPDATE",1,"Định vị OK")
    elif c=="0":
        break