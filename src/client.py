#!/usr/bin/env python
# encoding=utf-8
# This program is to be ran with Python 2.7, as that was the interpreter used for testing.
import sys
import socket
import time
# import os
import json
import cherrypy
import net_funcs
from colorama import init
init()

if sys.version_info >= (3, 0):
    raise SystemExit('Please run this program using Python 2.7.')
# Some values
app_version = "0.2"
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
    CLEAR = '\x1b[2J\x1b[H'


# Terminal-based Interface
def main():
    print("PBox Client v" + app_version + "\n")

    print("\nEnter \"help\" to see all the available commands")
    while True:
        usr_input = raw_input(">").strip()

        # Parse user input
        if usr_input == "quit" or usr_input == "exit":
            break
        if usr_input == "clear" or usr_input == "cls":
            #os.system("cls")  # Windows command :/. Detecting whether a terminal supports ANSI escape codes is not that
            # simple, and although using both os.system("cls") and sys.stderr.write("\x1b[2J\x1b[H") works on Windows
            # and Linux (using Bash, at least), it's a dirty solution. Not to mention that it doesn't always work properly.
            # Other codes like the ones used for coloured text will be messed up. Therefore, this approach was discarded.
            # As such, colorama was used. However, this brings issues if using something like PyCharm, which natively
            # supports ANSI escape codes, to run the program. However, I've decided to keep this approach because it
            # was the cleaner of all the approaches I tried.
            sys.stderr.write(BColors.CLEAR)
        elif usr_input == "list" or usr_input == "list_boxes" or usr_input == "lboxes":
            show_list()
        elif usr_input == "create" or usr_input == "create_box" or usr_input == "cbox":
            show_create()
        elif usr_input == "show_msg" or usr_input == "rmsg" or usr_input == "read_msg":
            show_showmsg1()
        elif usr_input == "show_msgs" or usr_input == "rmsgs" or usr_input == "read_msgs":
            show_showallmsg()
        elif usr_input == "send_msg" or usr_input == "smsg":
            show_putmsg()
        elif usr_input == "delete_msg" or usr_input == "del_msg" or usr_input == "dmsg":
            show_delmsg()
        elif usr_input == "delete_msgs" or usr_input == "del_msgs" or usr_input == "dmsgs":
            show_delmsgs()
        elif usr_input == "ver":
            print(app_version)
        elif usr_input == "help" or usr_input == "man":
            show_help()
        else:
            print(BColors.FAIL + "Error. Invalid command. Type \"help\" to see all available commands.\n" + BColors.ENDC)

    sys.exit(0)


def show_help():
    print("PBox Client v" + app_version)
    print("\nAuthors: Mário Liberato & Jorge Oliveira\n")
    print("Available Commands:")
    print("- list | list_boxes | lboxes - Lists and shows the number of existing boxes")
    print("- create | create_box | cbox - Creates a box")
    print("- show_msg | read_msg | rmsg - Reads the oldest message from a box")
    print("- show_msgs | read_msgs | rmsgs - Reads all messages from a box")
    print("- send_msg | smsg - Sends a message to a box")
    print("- delete_msg | del_msg | dmsg - Deletes the oldest message from a box")
    print("- delete_msgs | del_msgs | dmsgs - Deletes all messages from a box")
    print("- ver - Displays the version of the program")
    print("- help | man - Displays this text")


def show_delmsg():
    box_name = ""
    while True:
        box_name = raw_input("Box Name>")
        if not box_name.strip() == "":
            break
    print("Deleting oldest message from \"" + box_name + "\"...")
    delete_message(box_name, tgt_server)


def show_delmsgs():
    box_name = ""
    while True:
        box_name = raw_input("Box Name>")
        if not box_name.strip() == "":
            break
    print("Deleting all messages from \"" + box_name + "\"...")
    delete_messages(box_name, tgt_server)


def show_putmsg():
    box_name = ""
    message = ""
    while True:
        box_name = raw_input("Box Name>")
        if not box_name.strip() == "":
            break
    while True:
        message = raw_input("Message>")
        if not message.strip() == "":
            break
    print("Sending message to \"" + box_name + "\"...")
    put_message(box_name, message, tgt_server)


def show_showallmsg():
    box_name = ""
    while True:
        box_name = raw_input("Box Name>")
        if not box_name.strip() == "":
            break
    print("Requesting all messages from \"" + box_name + "\"...")
    print("Messages:\n" + prettyfy(get_messages(box_name, tgt_server), "\n"))


def show_showmsg1():
    box_name = ""
    while True:
        box_name = raw_input("Box Name>")
        if not box_name.strip() == "":
            break
    print("Requesting oldest message from \"" + box_name + "\"...")
    print(get_message(box_name, tgt_server))


def show_create():
    box_name = ""
    while True:
        box_name = raw_input("Box Name>")
        if not box_name.strip() == "":
            break
    print("Creating new box \"" + box_name + "\"...")
    create_box(box_name, tgt_server)


def show_list():
    print("Getting information from the server...")
    box_list, box_names = set_list_and_names(tgt_server)
    print(BColors.BOLD + "Existing Boxes:\n" + BColors.ENDC + box_names + "\n")
    print(BColors.BOLD + "Number of Boxes: " + BColors.ENDC + str(get_box_number(box_list)))


# Other functions
def set_list_and_names(srv):
    box_list = get_box_list(srv)
    box_names = []
    for box in box_list[u"payload"]:
        box_names.append(box[u"name"])
    box_names = prettyfy(box_names, BColors.OKBLUE + ", " + BColors.ENDC)
    return box_list, box_names


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
        elif dic_reply[u"content"] == "Box not found" and dic_reply[u"code"] == "ERROR":
            if not called_from_gms:
                return BColors.FAIL + "There is no such box!" + BColors.ENDC
            return BColors.FAIL + "There is no such box!" + BColors.ENDC, 2  # Returns 2 as exit code

        else:
            print(BColors.FAIL + "Error requesting messages!" + BColors.ENDC)
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
        if len(message) == 2:  # If two values are returned, that means the message is empty or box not found
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
                print(BColors.OKGREEN + 'Created box "' + validate_string(box_name) + '" successfully!' + BColors.ENDC)
                return "OK"
            else:
                print(BColors.FAIL + "Error." + BColors.ENDC)
                sys.exit(-1)
        else:
            print(BColors.FAIL + "Unknown Error." + BColors.ENDC)
            sys.exit(-1)
    elif len(dic_reply) == 4:  # Checking content of error message
        if dic_reply[u"code"] == "ERROR":
            print(BColors.FAIL + "Error!")
            print(dic_reply[u"content"] + "!" + BColors.ENDC)
            if not dic_reply[u"content"] == "Box already exists":  # If the error is not the expected one, quit
                sys.exit(-1)
            else:
                return "ERR_EXISTS"
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