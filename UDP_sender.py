import socket
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

print("[Sender] UDP Sender started")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
count = 0

while True:
    msg = f"Message {count}"
    sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))
    print("[Sender] Sent:", msg)
    count += 1
    time.sleep(0.1)
