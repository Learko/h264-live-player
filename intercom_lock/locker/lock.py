#!/usr/bin/env python3

import sys

from curio import run, spawn, TaskGroup
from curio.socket import *

from time import sleep
from multiprocessing import Process



async def locker(host, port):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    sock.bind((host, port))
    sock.listen(SOMAXCONN)

    sys.stdout.write('\033[2J')
    sys.stdout.write(f'\033[1;HServer listening at [{host}:{port}]')
    sys.stdout.flush()

    # Lock animation
    with open('lock_gif.txt') as f:
        lock = f.readlines()
    
    lock_open = [lock[i*40:(i+1)*40] for i in range(40, 80)]
    lock_close = [lock[i*40:(i+1)*40] for i in range(80, 120)]
    print_lock_state(lock_open[0])

    async with sock, TaskGroup() as g:
        while True:
            conn, addr = await sock.accept()
            await g.spawn(lock_handle, conn, *addr, lock_open, lock_close)


async def lock_handle(conn, addr, port, lock_open, lock_close):
    async with conn:
        data = await conn.recv(1024)
        ip, action = data.decode().split()
        sys.stdout.write(f'\033[2;H\033[39m[{addr}:{port}] >>> {ip} [{action.upper()}]')
        sys.stdout.flush()

        await conn.sendall('unlocked'.encode())

        # Opening animation.
        for lock_state in lock_open:
            print_lock_state(lock_state)
            sleep(0.03)
        
        # Lock is open.
        sleep(3)

        # Closing animation.
        for lock_state in lock_close:
            print_lock_state(lock_state)
            sleep(0.03)


def print_lock_state(lock):
    sys.stdout.write('\033[4;H')
    sys.stdout.write(''.join(lock[1:])+'\r\n')
    sys.stdout.flush()


if __name__ == '__main__':
    if sys.version_info < (3, 6):
        sys.exit('Python 3.6 or later is required.\n')

    try:
        run(locker, 'localhost', 31337)
    except KeyboardInterrupt:
        sys.stdout.write('\033[2J')
        sys.stdout.write('\033[;H')
        sys.stdout.flush()
