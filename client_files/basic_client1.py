import socket
import client_files

SERVER_IP = "127.0.0.1"
SERVER_PORT = 7239


def main():
    try:  # connection errors could be at any moment, and that why the try is on all the code
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (SERVER_IP, SERVER_PORT)
        sock.connect(server_address)
        m = "HELLO"
        sock.sendall(m.encode())
        # decrypter_object = code.Decrypter()

        # start exchanging keys
        # server_msg = sock.recv(1200)
        # server_msg_json = json.loads(server_msg.decode())
        # print(server_msg_json)
        # p = decrypter_object.set_public_data_from_encrypter_and_get_own_point(server_msg_json)

        server_msg = sock.recv(1200)
        server_msg = server_msg.decode()
        if not (server_msg == "Problem"):
            print(server_msg)
            print("OPTIONS:\n")
            print('1 - Sign up Patient (type: 1)\n')
            print('2 - Sign up Doctor (type: 2)\n')
            print('3 - Log in Patient (type: 3)\n')
            print('4 - Log in Doctor (type: 4)\n')
            print('8 - Exit (type: 8)\n')
            m = input("Enter option: ")
            while m != "8":
                m = client_files.options_manager_client(m, sock)
                sock.sendall(m.encode())
                server_msg = sock.recv(1200)
                server_msg = server_msg.decode()
                print(server_msg)
                if server_msg == "EXIT":
                    m = 8
                m = input("Enter option: ")
            sock.sendall(m.encode())
            server_msg = sock.recv(1200)
            server_msg = server_msg.decode()
        print(server_msg)
        sock.close()
    except Exception as e:
        print(e)
        sock.close()
        print("\n\nConnection Error!")


if __name__ == '__main__':
    main()
