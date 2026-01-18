import socket
import json
from datetime import datetime

# ===== CONFIG WIFI =====
CAR_B_IP = "127.0.0.1"   # nếu chạy cùng máy: đổi thành "127.0.0.1"
PORT = 5000
# =======================

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def send_json(sock, obj):
    data = (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")
    sock.sendall(data)

def send_event(sock, event_name, message, priority):
    """
    Gửi thông báo V2V dạng EVENT + priority
    priority: 3 (cao) / 2 (trung bình) / 1 (thấp)
    """
    event = {
        "type": "EVENT",
        "time": now(),
        "from": "CarA",
        "to": "CarB",
        "event_name": event_name,
        "priority": int(priority),
        "message": message
    }
    send_json(sock, event)
    print(f"✅ ĐÃ GỬI EVENT: {event_name} | priority={priority}")

def menu():
    print("\n🚗 Xe A – EVENT ONLY")
    print("1) 🚨 PHANH GẤP (priority=3)")
    print("2) ⚠️ VẬT CẢN PHÍA TRƯỚC (priority=2)")
    print("3) ℹ️ ĐỊNH VỊ / TRẠNG THÁI (priority=1)")
    print("0) Thoát")

def main():
    print("🚗 Xe A khởi động (CHỈ GỬI EVENT – KHÔNG BSM)")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(5.0)

    try:
        client.connect((CAR_B_IP, PORT))
    except Exception as e:
        print(f"❌ Không kết nối được Xe B: {e}")
        return

    print(f"✅ Đã kết nối Xe B tại {CAR_B_IP}:{PORT}")

    while True:
        menu()
        choice = input("👉 Chọn: ").strip()

        if choice == "1":
            send_event(client, "EMERGENCY_BRAKE",
                       "PHANH GẤP! Xe phía trước giảm tốc đột ngột!",
                       priority=3)

        elif choice == "2":
            send_event(client, "OBSTACLE_AHEAD",
                       "CÓ VẬT CẢN PHÍA TRƯỚC! Giảm tốc ngay!",
                       priority=2)

        elif choice == "3":
            send_event(client, "POSITION_UPDATE",
                       "Định vị: xe A vẫn đang chạy bình thường.",
                       priority=1)

        elif choice == "0":
            print("👋 Xe A thoát.")
            break
        else:
            print("❌ Lựa chọn không hợp lệ")

    client.close()

if __name__ == "__main__":
    main()
