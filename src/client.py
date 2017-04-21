#!/usr/bin/env python3
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


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def main():
    print("PBox Client\n")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(tgt_server)
    print(sock.send('{"type":"LIST"}\r\n'.encode()))
    rv = net_funcs.recv_all(sock).decode()

    sock.close()

    print(rv)


def menu():
    print("PBox Client v" + app_version + "\n")
    box_list = get_box_list(tgt_server[0], tgt_server[1])
    if box_list[u"code"] != "OK":
        print("Server Reply Code: " + BColors.FAIL + str(box_list[u"code"]) + BColors.ENDC + '\n Expected "OK"')
        sys.exit(-1)
    if box_list[u"type"] != "RESULT":
        print("Server Reply Type: " + BColors.FAIL + str(box_list[u"type"]) + BColors.ENDC + '\n Expected "RESULT"')
        sys.exit(-1)

    box_names = []
    for box in box_list[u"payload"]:
        box_names.append(box[u"name"])
    box_names = u', '.join(box_names).encode('utf-8').strip()
    print(BColors.BOLD + "Existing Boxes:\n" + BColors.ENDC + box_names + "\n")
    print(BColors.BOLD + "Number of Boxes: " + BColors.ENDC + str(get_box_number(box_list)))

    put_message("84917_lolol", "Boas pessoal aqui estou com mais um video",tgt_server[0], tgt_server[1])


# Other functions
def validate_string(string, is_message = False)

    if is_message and len(string) > max_msg_size:
        chars_to_rem = len(string) - max_msg_size
        string = string[:-chars_to_rem]
    return string


# Server functions
def put_message(box_name, message, server_address, server_port):
    msg = '{ "type": "PUT", "name": "' + validate_string(box_name) + '", "timestamp":' + str(int(time.time())) + ', "content": "' + validate_string(message) + '" }\r\n'
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_address, server_port))
    sock.send(msg.encode())
    reply = net_funcs.recv_all(sock).decode()
    sock.close()
    dic_reply = json.loads(reply)
    print reply


def create_box(box_name, server_address, server_port, pubk="-1", sig="-1"):  # Creates a box, optional with security
    # SECURITY NOT IMPLEMENTED
    msg = '{ "type": "CREATE", "name": "' + validate_string(box_name) + '", "timestamp":' + str(int(time.time())) + ' }\r\n'
    if pubk != "-1" or sig != "-1":
        msg = '{ "type": "CREATE", "name": "' + validate_string(box_name) + '", timestamp":' + str(int(time.time())) + ', "pubk": "' + pubk + '", "sig": "' + sig + '" }\r\n'  # Not implemented
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_address, server_port))
    sock.send(msg.encode())
    reply = net_funcs.recv_all(sock).decode()
    sock.close()
    dic_reply = json.loads(reply)
    # {"content": "Box already exists", "timestamp": 1492735160, "code": "ERROR", "type": "RESULT"}
    # {"timestamp": 1492735147, "code": "OK", "type": "RESULT"}
    if len(dic_reply) == 3:  # Now check if the reply code is OK
        if dic_reply[u"type"] == "RESULT":
            if dic_reply[u"code"] == "OK":
                print(BColors.OKGREEN + 'Created box "' + validate_string(box_name) + '" successfully!')
                return "OK"
            else:
                print(BColors.FAIL + "Error." + BColors.ENDC)
                exit(-1)
        else:
            print(BColors.FAIL + "Unknown Error." + BColors.ENDC)
            exit(-1)
    elif len(dic_reply) == 4:  # Checking content of error message
        if dic_reply[u"code"] == "ERROR":
            print(BColors.FAIL + "Error Message:" + BColors.ENDC)
            print(dic_reply[u"content"])
            if not dic_reply[u"content"] == "Box already exists":  # If the error is not the expected one, quit
                exit(-1)
        else:
            print(BColors.FAIL + "Unknown Error." + BColors.ENDC)
            exit(-1)
    else:
        print(BColors.FAIL + "Unknown Error." + BColors.ENDC)
        exit(-1)


def get_box_msg_number(box_name, box_list):
    box_index = get_box_index(validate_string(box_name), box_list)
    if box_index == -1:
        print(BColors.FAIL + "Box doesn't exist!" + BColors.ENDC)

    return box_list[u"payload"][box_index][u"size"]


def get_box_index(box_name, box_list):
    index = 0
    while index < get_box_number(box_list):
        if box_list[u"payload"][index][u"name"] == box_name:
            return index
        index = index + 1
    return -1


def get_box_number(box_list):
    return len(box_list[u"payload"])


def get_box_list(server_address, server_port):
    msg = '{ "type": "LIST" }\r\n'
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_address, server_port))
    sock.send(msg.encode())
    reply = net_funcs.recv_all(sock).decode()
    sock.close()
    return json.loads(reply)


# CherryPy Part of PBoxClient
class PBoxClient(object):
    def __init__(self):
        self.actions = Actions()

    @cherrypy.expose
    def index(self):
        return open("resources/index.html", "r").read()


class Actions(object):
    @cherrypy.expose
    def doListBoxes(self):
        print("PBox Client v" + app_version + "\n")
        box_list = get_box_list(tgt_server[0], tgt_server[1])
        if box_list[u"code"] != "OK":
            print("Server Reply Code: " + BColors.FAIL + str(box_list[u"code"]) + BColors.ENDC + '\n Expected "OK"')
            sys.exit(-1)
        if box_list[u"type"] != "RESULT":
            print("Server Reply Type: " + BColors.FAIL + str(box_list[u"type"]) + BColors.ENDC + '\n Expected "RESULT"')
            sys.exit(-1)

        box_names = []
        for box in box_list[u"payload"]:
            box_names.append(box[u"name"])
        box_names = u', '.join(box_names).encode('utf-8').strip()
        print(BColors.BOLD + "Existing Boxes:\n" + BColors.ENDC + box_names + "\n")
        print(BColors.BOLD + "Number of Boxes: " + BColors.ENDC + str(get_box_number(box_list)))
        print(get_box_index(u"abc", box_list))
        return box_names

# cherrypy.quickstart(PBoxClient())

menu()