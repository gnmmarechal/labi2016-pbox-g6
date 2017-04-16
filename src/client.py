#!/usr/bin/env python
# encoding=utf-8
import socket
import time
import json
import sys
import cherrypy
import net_funcs

# Some values
app_version = "0.1"
max_msg_size = 65536  # Maximum size of the message in octets
tgt_server = "xcoa.av.it.pt", 8080  # Address/Hostname and port of the server


def main():
    print("PBox Client")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(tgt_server)
    print(sock.send('{"type":"LIST"}\r\n'.encode()))
    rv = net_funcs.recvall(sock).decode()

    sock.close()

    print(rv)


def menu():
    print("PBox Client v" + app_version)
    running = True
    while running:
        usr_input = input(">")


class PBoxClient(object):
    def __init__(self):
        self.actions = Actions()

    @cherrypy.expose
    def index(self):
        return open("resources/index.html", "r").read()


class Actions(object):
    @cherrypy.expose
    def doLogin(self, username=None, password=None):
        return username

cherrypy.quickstart(PBoxClient())