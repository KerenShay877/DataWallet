import socket
from _thread import *
import server_files
LISTEN_PORT = 7239


def main():
    num = 20
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('', LISTEN_PORT)
    listen_sock.bind(server_address)
    listen_sock.listen(num)
    print("Listening on port %d" % LISTEN_PORT + "...")
    while num > 0:
        client_soc, client_address = listen_sock.accept()
        num -= 1
        print("New client")
        start_new_thread(server_files.client_handler, (client_soc,))
    listen_sock.close()

if __name__ == '__main__':
    main()
