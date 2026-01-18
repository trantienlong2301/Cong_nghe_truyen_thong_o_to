import socket
import subprocess
import time
import sys

MCAST_GRP = "224.1.1.1"
MCAST_PORT = 5007
# LOCAL_PORT = 6000


# def multicast_server():
#     print(" Multicast server đang chạy...", flush=True)

#     recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     recv_sock.bind(("0.0.0.0", LOCAL_PORT))

#     send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
#     send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

#     try:
#         while True:
#             data, addr = recv_sock.recvfrom(1024)
#             send_sock.sendto(data, (MCAST_GRP, MCAST_PORT))

#     except KeyboardInterrupt:
#         print(" Server dừng", flush=True)

#     finally:
#         recv_sock.close()
#         send_sock.close()


if __name__ == "__main__":
    #  server chạy trong process hiện tại
    # import threading
    # threading.Thread(target=multicast_server, daemon=True).start()

    # time.sleep(1)

    cars = [
        ("Xe 1", "process.py", "1"),
        ("Xe 2", "process.py", "2"),
        ("Xe 3", "process.py", "3"),
        ("Xe 4", "process.py", "4"),
    ]

    procs = []

    for title, script, cid in cars:
        cmd = (
            f'cmd /k "title Xe {cid} && {sys.executable} {script} {cid}"'
        )

        p = subprocess.Popen(
            cmd,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        procs.append(p)
   

    #  giữ main sống đúng cách
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n Tắt toàn bộ xe")
        for p in procs:
            subprocess.call(
                ["taskkill", "/F", "/T", "/PID", str(p.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
