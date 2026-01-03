import multiprocessing
import os
import time

def open_terminal(title, script,length,width,id):
    os.system(f'start "{title}" cmd /k python "{script}" {length} {width} {id}')

if __name__ == "__main__":
    print("Mở 2 terminal riêng...")

    p1 = multiprocessing.Process(
        target=open_terminal,
        args=("Xe 1", "process.py","2.0","1.5","1")
    )

    p2 = multiprocessing.Process(
        target=open_terminal,
        args=("Xe 2", "process.py","2.0","1.5","2")
    )

    p1.start()
    p2.start()
