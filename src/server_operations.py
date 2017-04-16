# Module to handle communication with the server
import net_funcs


def list_boxes(hostname, port):
    get_box_info(hostname, port, "names")