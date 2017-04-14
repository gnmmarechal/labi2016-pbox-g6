#!/usr/bin/env python
# encoding=utf-8
import socket
import sys
import time
import json

# Some values
max_msg_size = 65536  # Maximum size of the message in octets
tgt_server = "xcoa.av.it.pt", 8080  # Address/Hostname and port of the server


def main():
    print("PBox Client")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Connecting to " + tgt_server[0] + ":" + str(tgt_server[1]))
    sock.connect(tgt_server)
    print(sock.send('{"type":"LIST"}\r\n'.encode()))
    rv = recvall(sock).decode()

    sock.close()

    print(rv)

def recvall(sock):
    sock.setblocking(0)
    data_array = []
    data = ""

    start_time = time.time()

    while 1:
        if data_array and time.time() - start_time > 2:
            break
        elif time.time() - start_time > 4:
            break

        try:
            data = sock.recv(8192)
            if data:
                data_array.append(data)
                start_time = time.time()
            else:
                time.sleep(0.1)
        except:
            pass


    return b"".join(data_array)


# Runs main function
if __name__ == "__main__":
    main()
