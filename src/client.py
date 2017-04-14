#!/usr/bin/env python
# encoding=utf-8
import socket
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
    rv = sock.recv(1024)
    sock.close()

    print(rv)

# Runs main function
if __name__ == "__main__":
    main()
