#!/usr/bin/env python
import cherrypy
import client

web_app_version = "0.1.0"
index = open("resources/index.html", "r").read()


# CherryPy Part of PBoxClient
class PBoxClientWeb(object):
    @cherrypy.expose
    def index(self):
        return index

    @cherrypy.expose
    def list_boxes(self):
        box_list, box_names = client.set_list_and_names_nocolor(client.tgt_server)
        retval = index + "<H1>Box List</H1><BR><B>" + "Number of Boxes: </B><P>" + str(client.get_box_number(box_list)) + '</P><BR><textarea name="Box List" cols="200" rows="30" readonly>' + box_names + '</textarea>'
        return retval

    @cherrypy.expose()
    def create_box(self):
        retval = index + '<H1>Create Box</H1><form action="create_box_really" method="post"> Name: <input type="text" name="box_name" value=""> <p><input type="submit" value="Create Box"/></p> </form>'
        return retval

    @cherrypy.expose()
    def create_box_really(self, box_name=""):
        if box_name.strip() == "":
            return '<meta http-equiv="refresh" content="0; url=http://127.0.0.1:8080/create_box" />'
        else:
            retval = index + "<H1>Box Creation</H1><BR>"
            retcode = client.create_box(box_name.strip(), client.tgt_server)
            if retcode == "OK":
                retval += '<P>Creation of box "' + box_name.strip() + '" successful!</P>'
            elif retcode == "ERR_EXISTS":
                retval += '<P>Creation of box "' + box_name.strip() + '" unsuccessful! Box already exists!</P>'
            else:
                retval += '<P>Creation of box "' + box_name.strip() + '" unsuccessful!</P>'
            return retval


cherrypy.quickstart(PBoxClientWeb())
