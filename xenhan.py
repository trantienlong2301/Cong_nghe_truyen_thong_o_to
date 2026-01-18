import socket
import json
import logging

HOST = "0.0.0.0"
PORT = 5000

def safe_json_load(line):
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None

def setup_logger():
    logging.basicConfig(
        filename="car_b_log.txt",
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

def main():
    setup_logger()

    print("🚗 Xe B – EVENT RECEIVER (có priority + log cảnh báo)")
    print(f"✅ Lắng nghe tại {HOST}:{PORT}\n")
    print("📄 Log file: car_b_log.txt\n")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)

    while True:
        print("📡 Đang chờ Xe A kết nối...")
        conn, addr = server.accept()
        print(f"✅ Xe A kết nối từ {addr}\n")

        buffer = ""

        while True:
            try:
                data = conn.recv(4096).decode("utf-8", errors="ignore")
                if not data:
                    print("❌ Xe A ngắt kết nối\n")
                    break
            except Exception as e:
                print(f"❌ Lỗi recv: {e}")
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
                    t = msg.get("time", "")
                    event_name = msg.get("event_name", "UNKNOWN")
                    message = msg.get("message", "")
                    priority = int(msg.get("priority", 1))

                    # ghi log: priority cao ghi WARNING
                    log_line = f"from={addr} prio={priority} time={t} event={event_name} msg={message}"
                    if priority >= 3:
                        logging.warning(log_line)
                    else:
                        logging.info(log_line)

                    # in màn hình
                    print("=====================================")
                    print("NHẬN TIN NHẮN V2V (Xe B)")
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

        conn.close()

if __name__ == "__main__":
    main()