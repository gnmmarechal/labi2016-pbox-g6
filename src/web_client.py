#!/usr/bin/env python
import cherrypy
import client
import re

web_app_version = "0.1.0"
index = open("resources/index.html", "r").read()


def escape_ansi(lines):
    i = 0
    while i < len(lines):
        ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
        lines[i] = ansi_escape.sub('', lines[i])
        i += 1
    return lines


# CherryPy Part of PBoxClient
class PBoxClientWeb(object):
    @cherrypy.expose
    def index(self):
        return index

    @cherrypy.expose
    def list_boxes(self):
        box_list, box_names = client.set_list_and_names_nocolor(client.tgt_server)
        retval = index + "<H1>Box List</H1><B>" + "Number of Boxes: </B><P>" + str(client.get_box_number(box_list)) + '</P><BR><textarea name="Box List" cols="200" rows="30" readonly>' + box_names + '</textarea>'
        return retval

    @cherrypy.expose()
    def create_box(self):
        retval = index + '<H1>Create Box</H1><form action="create_box_really" method="post"> Box Name: <input type="text" name="box_name" value=""> <p><input type="submit" value="Create Box"/></p> </form>'
        return retval

    @cherrypy.expose()
    def delete_msg(self):
        retval = index + '<H1>Delete Oldest Message</H1><form action="delete_one" method="post"> Box Name: <input type="text" name="box_name" value=""> <p><input type="submit" value="Delete"/></p> </form> </BODY></HTML>'
        return retval

    @cherrypy.expose()
    def delete_msgs(self):
        retval = index + '<H1>Delete All Messages</H1><form action="delete_all" method="post"> Box Name: <input type="text" name="box_name" value=""> <p><input type="submit" value="Delete"/></p> </form> </BODY> </HTML>'
        return retval

    @cherrypy.expose()
    def read_msgs(self):
        retval = index + '<H1>Read Messages</H1><form action="read_all" method="post"> Box Name: <input type="text" name="box_name" value=""> <p><input type="submit" value="Read"/></p> </form> </BODY> </HTML>'
        return retval

    @cherrypy.expose()
    def put_msg(selfs):
        retval = index + '<H1>Send Message</H1><form action="send" method="post"> Box Name: <input type="text" name="box_name" value=""> <BR><BR>Message: <input type="text" name="message" maxlength="65536" value=""> <p><input type="submit" value="Send"/></p> </form> </BODY> </HTML>'
        return retval

    # Called by Input
    @cherrypy.expose()
    def send(self, box_name="", message=""):
        if box_name.strip() == "" or message.strip() == "":
            return '<meta http-equiv="refresh" content="0; url=http://127.0.0.1:8080/put_msg" />'
        else:
            retval = index + "<H1>Message Sending</H1>"
            retcode = client.put_message(box_name.strip(), message.strip(), client.tgt_server)
            if retcode == 0:
                retval += '<P>Message sent successfully!</P>'
            else:
                retval += '<P>Message sending failure!</P>'
            return retval

    @cherrypy.expose()
    def read_all(self, box_name=""):
        if box_name.strip() == "":
            return '<meta http-equiv="refresh" content="0; url=http://127.0.0.1:8080/delete_msgs" />'
        else:
            retval = index + "<H1>Messages</H1>"
            retcode = client.get_messages(box_name.strip(), client.tgt_server)
            retcode = escape_ansi(retcode)
            retval += "<textarea name=\"Message List\" cols=\"200\" rows=\"30\" readonly>" + client.prettyfy(retcode, "\n") + "</textarea> </BODY> </HTML>"
            return retval

    @cherrypy.expose()
    def delete_all(self, box_name=""):
        if box_name.strip() == "":
            return '<meta http-equiv="refresh" content="0; url=http://127.0.0.1:8080/delete_msgs" />'
        else:
            retval = index + "<H1>Message Deletion</H1>"
            retcode = client.delete_messages(box_name.strip(), client.tgt_server)
            if len(retcode) == 2:
                retcode = retcode[0]
            if retcode == (client.BColors.FAIL + "There is no such box!" + client.BColors.ENDC):
                retval += "<P>The box\"" + box_name.strip() + "\"doesn't exist!</P> </BODY> </HTML>"
            else:
                retval += "<P>Deletion successful!</P> </BODY> </HTML>"
            return retval

    @cherrypy.expose()
    def delete_one(self, box_name=""):
        if box_name.strip() == "":
            return '<meta http-equiv="refresh" content="0; url=http://127.0.0.1:8080/delete_msg" />'
        else:
            retval = index + "<H1>Message Deletion</H1>"
            retcode = client.delete_message(box_name.strip(), client.tgt_server)
            if len(retcode) == 2:
                retcode = retcode[0]
            if retcode == (client.BColors.FAIL + "There is no such box!" + client.BColors.ENDC):
                retval += "<P>The box\"" + box_name.strip() + "\"doesn't exist!</P> </BODY> </HTML>"
            else:
                retval += "<P>Deletion successful!</P> </BODY> </HTML>"
            return retval

    @cherrypy.expose()
    def create_box_really(self, box_name=""):
        if box_name.strip() == "":
            return '<meta http-equiv="refresh" content="0; url=http://127.0.0.1:8080/create_box" />'
        else:
            retval = index + "<H1>Box Creation</H1>"
            retcode = client.create_box(box_name.strip(), client.tgt_server)
            if retcode == "OK":
                retval += '<P>Creation of box "' + box_name.strip() + '" successful!</P>'
            elif retcode == "ERR_EXISTS":
                retval += '<P>Creation of box "' + box_name.strip() + '" unsuccessful! Box already exists!</P>'
            else:
                retval += '<P>Creation of box "' + box_name.strip() + '" unsuccessful!</P>'
            return retval


cherrypy.quickstart(PBoxClientWeb())
