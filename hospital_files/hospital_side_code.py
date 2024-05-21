from _thread import *
import hospital_files
import socket

LISTEN_PORT = 8543


def main():
    num = 20
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hospital_address = ('', LISTEN_PORT)
    listen_sock.bind(hospital_address)
    listen_sock.listen(num)
    print("Listening on port %d" % LISTEN_PORT + "...")
    while num > 0:
        req_soc, client_address = listen_sock.accept()
        num -= 1
        print("New client")
        start_new_thread(hospital_files.request_handler, (req_soc,))
    listen_sock.close()

if __name__ == '__main__':
    main()
