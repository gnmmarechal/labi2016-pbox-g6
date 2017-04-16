# Module to handle network-related functions
import time


def recvall(sock):  # Receives all of the data (until it stops on a timeout)
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