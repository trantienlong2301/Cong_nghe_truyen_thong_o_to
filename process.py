import socket
import sys
import threading
from datetime import datetime
import struct
import json
import logging

if len(sys.argv) < 2:
    print(" Thiếu tham số, dùng giá trị mặc định để test")
    car_id = "TEST"
else:
    
    car_id = sys.argv[1]

# SERVER_ADDR = ("127.0.0.1", 6000)

MCAST_GRP = "225.225.225.225"
MCAST_PORT = 5007


def safe_json_load(line):
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None

def setup_logger():
    logging.basicConfig(
        filename=f"{car_id}_log.txt",
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def send_json(sock, obj):
    data = (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")
    sock.sendto(data,(MCAST_GRP, MCAST_PORT))

def send_event(sock, event_name, message, priority):
    """
    Gửi thông báo V2V dạng EVENT + priority
    priority: 3 (cao) / 2 (trung bình) / 1 (thấp)
    """
    event = {
        "type": "EVENT",
        "time": now(),
        "from": f"{car_id}",
        "event_name": event_name,
        "priority": int(priority),
        "message": message
    }
    send_json(sock, event)
    print(f" ĐÃ GỬI EVENT: {event_name} | priority={priority}")
    
# ===== nhận multicast =====
def receive_multicast():
    setup_logger()

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

    buffer = ""

    while True:
        try:
            data = sock.recv(4096).decode("utf-8", errors="ignore")
            if not data:
                print(" khong co data\n")
                break
        except Exception as e:
            print(f" Lỗi recv: {e}")
            break
        buffer += data

        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            if not line.strip():
                continue

            msg = safe_json_load(line)
            if not msg:
                continue

            if msg.get("type") == "EVENT":
                id = msg.get("from", "")
                if id == car_id:
                    continue
                t = msg.get("time", "")
                event_name = msg.get("event_name", "UNKNOWN")
                message = msg.get("message", "")
                priority = int(msg.get("priority", 1))

                # ghi log: priority cao ghi WARNING
                log_line = f"from={id} prio={priority} time={t} event={event_name} msg={message}"
                if priority >= 3:
                    logging.warning(log_line)
                else:
                    logging.info(log_line)

                # in màn hình
                print("=====================================")
                print(f"NHẬN TIN NHẮN V2V từ xe {id}")
                print(f"Time     : {t}")
                print(f"Event    : {event_name}")
                print(f"Priority : {priority}")
                print(f"Message  : {message}")
                if priority >= 3:
                    print("Action   : CẢNH BÁO KHẨN / PHANH GẤP")
                elif priority == 2:
                    print("Action   : CẢNH BÁO / GIẢM TỐC")
                else:
                    print("Action   : THÔNG TIN / THEO DÕI")
                print("=====================================\n")




# ===== gửi dữ liệu =====
def send_data():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        while True:
            choice = input(" Chọn: ").strip()

            if choice == "1":
                send_event(sock, "EMERGENCY_BRAKE",
                        "PHANH GẤP! Xe phía trước giảm tốc đột ngột!",
                        priority=3)

            elif choice == "2":
                send_event(sock, "OBSTACLE_AHEAD",
                        "CÓ VẬT CẢN PHÍA TRƯỚC! Giảm tốc ngay!",
                        priority=2)

            elif choice == "3":
                send_event(sock, "POSITION_UPDATE",
                        "Định vị: xe A vẫn đang chạy bình thường.",
                        priority=1)

            elif choice == "0":
                print(" Xe A thoát.")
                break
            else:
                print(" Lựa chọn không hợp lệ")
    except Exception as e:
        print("LỖI:", e)
        input("Nhấn Enter để thoát...")



if __name__ == "__main__":
    print(f" Xe {car_id} khởi động",flush=True)

    threading.Thread(target=receive_multicast, daemon=True).start()
    
    send_data()
