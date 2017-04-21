#!/usr/bin/env python
# encoding=utf-8
import socket
import time
import os
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

# Terminal-based Interface
def main():
    print("PBox Client v" + app_version + "\n")

    print("\nEnter \"help\" to see all the available commands")
    while True:
        usr_input = raw_input(">")

        # Parse user input
        if usr_input == "quit" or usr_input == "exit":
            break
        if usr_input == "clear" or usr_input == "cls":
            # This may not work on Windows if ANSI support is not enabled
            os.system("cls")
            sys.stderr.write("\x1b[2J\x1b[H")
        else:
            print(BColors.FAIL + "Error. Invalid command. Type \"help\" to see all available commands.\n" + BColors.ENDC)

    sys.exit(0)


# Other functions
def menu():  # Testing Function, used during development to test functions
    print("PBox Client v" + app_version + "\n")
    box_list = get_box_list(tgt_server)
    box_names = []
    for box in box_list[u"payload"]:
        box_names.append(box[u"name"])
    box_names = prettyfy(box_names, ", ")
    print(BColors.BOLD + "Existing Boxes:\n" + BColors.ENDC + box_names + "\n")
    print(BColors.BOLD + "Number of Boxes: " + BColors.ENDC + str(get_box_number(box_list)))

    print(get_message("84917_lolol", tgt_server))
    put_message("84917_lolol", "Boas pessoal aqui estou com mais um videowsdf", tgt_server)
    put_message("84917_lolol", "Boas pessoal aqui estou com mais um video2eq211wsdf", tgt_server)
    put_message("84917_lolol", "Boas pessoal aqui estou com mais um videoesasdawsdf", tgt_server)
    print(prettyfy(get_messages("84917_lolol", tgt_server), "\n"))


# Other functions
def validate_string(string, is_message=False):

    if is_message and len(string) > max_msg_size:
        chars_to_rem = len(string) - max_msg_size
        string = string[:-chars_to_rem]  # Trims messages to maximum size if they exceed it
    return string


def prettyfy(element, separator):
    return (u'' + separator).join(element).encode('utf-8').strip()


# Server functions
def delete_message(box_name, (server_address, server_port), called_from_dms=False, signature="-1"):
    get_message(box_name, (server_address, server_port), called_from_dms, signature)


def delete_messages(box_name, (server_address, server_port), signature="-1"):
    get_messages(box_name, (server_address, server_port), signature)


def get_message(box_name, (server_address, server_port), called_from_gms=False, signature="-1"):
    msg = '{ "type": "GET", "name": "' + validate_string(box_name) + '", "timestamp":' + str(int(time.time())) + ', "sig": "' + signature + '"}\r\n'
    if signature == "-1":
        msg = '{ "type": "GET", "name": "' + validate_string(box_name) + '", "timestamp":' + str(int(time.time())) + "}\r\n"
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((server_address, server_port))
    except Exception as e:
        print(BColors.FAIL + "Connection error! Error Message:")
        print(e)
        sys.exit(-1)
    sock.send(msg.encode())
    reply = net_funcs.recv_all(sock).decode()
    sock.close()
    # {"content": "Boas pessoal aqui estou com mais um video", "timestamp": 1492778665, "code": "OK", "type": "RESULT"}
    # {"content": "Box is empty", "timestamp": 1492778718, "code": "ERROR", "type": "RESULT"}
    dic_reply = json.loads(reply)

    if not dic_reply[u"code"] == "OK" or not dic_reply[u"type"] == "RESULT":
        if dic_reply[u"content"] == "Box is empty" and dic_reply[u"code"] == "ERROR":
            if not called_from_gms:
                return BColors.FAIL + "There are no messages in the box!" + BColors.ENDC
            return BColors.FAIL + "There are no messages in the box!" + BColors.ENDC, 1  # Returns 1 as exit code
        else:
            print(BColors.FAIL + "Unknown error!" + BColors.ENDC)
            sys.exit(-1)
    else:
        return dic_reply[u"content"]


def get_messages2(box_name, box_list, (server_address, server_port), signature="-1"):  # Second possible implementation of the function
    # get_messages is used instead, as it doesn't need to update box_list to get all messages, as it doesn't rely
    # on that, and just fetches the messages directly, until it hits the end.
    return_messages = []
    msg_count = get_box_msg_number(box_name, box_list)
    if msg_count == 0:
        return get_message(box_name, (server_address, server_port), True, signature)[0]
    c = 0
    while c < msg_count:
        return_messages.append(get_message(box_name, (server_address, server_port), True, signature))
        c += 1
    return return_messages


def get_messages(box_name, (server_address, server_port), signature="-1"):
    return_messages = []
    while True:
        message = get_message(box_name, (server_address, server_port), True, signature)
        if len(message) == 2:  # If two values are returned, that means the message is empty
            if return_messages == []:
                return_messages.append(message[0])
            break
        else:
            return_messages.append(message)
    return return_messages


def put_message(box_name, message, (server_address, server_port)):
    msg = '{ "type": "PUT", "name": "' + validate_string(box_name) + '", "timestamp":' + str(int(time.time())) + ', "content": "' + validate_string(message, True) + '" }\r\n'
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((server_address, server_port))
    except Exception as e:
        print(BColors.FAIL + "Connection error! Error Message:")
        print(e)
        sys.exit(-1)
    sock.send(msg.encode())
    reply = net_funcs.recv_all(sock).decode()
    sock.close()
    # {"timestamp": 1492776513, "code": "OK", "type": "RESULT"}
    dic_reply = json.loads(reply)

    if not len(dic_reply) == 3 or not dic_reply[u"code"] == "OK" or not dic_reply[u"type"] == "RESULT":
        print(BColors.FAIL + "Error sending message." + BColors.ENDC)
        return 1
    else:
        print(BColors.OKGREEN + "Message Sent! Timestamp: " + str(dic_reply[u"timestamp"]) + BColors.ENDC)
        return 0


def create_box(box_name, (server_address, server_port), pubk="-1", sig="-1"):  # Creates a box, optional with security
    # SECURITY NOT IMPLEMENTED
    msg = '{ "type": "CREATE", "name": "' + validate_string(box_name) + '", "timestamp":' + str(int(time.time())) + ' }\r\n'
    if pubk != "-1" or sig != "-1":
        msg = '{ "type": "CREATE", "name": "' + validate_string(box_name) + '", timestamp":' + str(int(time.time())) + ', "pubk": "' + pubk + '", "sig": "' + sig + '" }\r\n'  # Not implemented
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((server_address, server_port))
    except Exception as e:
        print(BColors.FAIL + "Connection error! Error Message:")
        print(e)
        sys.exit(-1)
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
                sys.exit(-1)
        else:
            print(BColors.FAIL + "Unknown Error." + BColors.ENDC)
            sys.exit(-1)
    elif len(dic_reply) == 4:  # Checking content of error message
        if dic_reply[u"code"] == "ERROR":
            print(BColors.FAIL + "Error Message:" + BColors.ENDC)
            print(dic_reply[u"content"])
            if not dic_reply[u"content"] == "Box already exists":  # If the error is not the expected one, quit
                sys.exit(-1)
        else:
            print(BColors.FAIL + "Unknown Error." + BColors.ENDC)
            sys.exit(-1)
    else:
        print(BColors.FAIL + "Unknown Error." + BColors.ENDC)
        sys.exit(-1)


def get_box_msg_number(box_name, box_list):
    box_index = get_box_index(validate_string(box_name), box_list)
    if box_index == -1:
        print(BColors.FAIL + "Box doesn't exist!" + BColors.ENDC)
        sys.exit(-1)

    return box_list[u"payload"][box_index][u"size"]


def get_box_index(box_name, box_list):
    index = 0
    while index < get_box_number(box_list):
        if box_list[u"payload"][index][u"name"] == box_name:
            return index
        index += 1
    return -1


def get_box_number(box_list):
    return len(box_list[u"payload"])


def get_box_list((server_address, server_port)):
    msg = '{ "type": "LIST" }\r\n'
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((server_address, server_port))
    except Exception as e:
        print(BColors.FAIL + "Connection error! Error Message:")
        print(e)
        sys.exit(-1)
    sock.send(msg.encode())
    reply = net_funcs.recv_all(sock).decode()
    sock.close()
    dic_reply = json.loads(reply)
    if dic_reply[u"code"] != "OK":
        print("Server Reply Code: " + BColors.FAIL + str(dic_reply[u"code"]) + BColors.ENDC + '\n Expected "OK"')
        sys.exit(-1)
    if dic_reply[u"type"] != "RESULT":
        print("Server Reply Type: " + BColors.FAIL + str(dic_reply[u"type"]) + BColors.ENDC + '\n Expected "RESULT"')
        sys.exit(-1)
    return dic_reply


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
        box_list = get_box_list(tgt_server)
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

main()