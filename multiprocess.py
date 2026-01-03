import multiprocessing
import os
import time

def worker_terminal(process_name, delay):
    # Tạo lệnh chạy trong cửa sổ cmd mới
    cmd = f"""
    title {process_name}
    python -c "import time; print('[%s] Đang chạy...'); 
    """ % (process_name, process_name, delay, process_name)

    # Mở cửa sổ cmd mới
    os.system(f'start " {process_name} " cmd /k {cmd}')

    # Không cần execvp vì start đã mở cửa sổ riêng

def main():
    print("Đang tạo 2 cửa sổ terminal riêng trên Windows...")

    p1 = multiprocessing.Process(target=worker_terminal, args=("Process-1", 1.0))
    p2 = multiprocessing.Process(target=worker_terminal, args=("Process-2", 1.5))

    p1.start()
    p2.start()

    print("Đã mở 2 cửa sổ riêng!")

if __name__ == "__main__":
    main()