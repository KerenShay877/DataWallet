import socket
import client_files
import time
import os
import select

SERVER_IP = "127.0.0.1"
SERVER_PORT = 7239
SYSTEM_MSG = "50"
timeout = 3  # seconds


def main():
    try:  # connection errors could be at any moment, and that why the try is on all the code
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (SERVER_IP, SERVER_PORT)
        sock.connect(server_address)

        # start conversation with server
        msg_to_server = "500"
        sock.sendall(msg_to_server.encode())
        server_msg = sock.recv(1200).decode()

        # starting log in / sign up process
        if not (server_msg == "611"):
            print(server_msg)
            print("OPTIONS:\n")
            print('1 - Sign up Patient')
            print('2 - Sign up Doctor')
            print('3 - Log in Patient')
            print('4 - Log in Doctor')
            print('5 - Recreate the password')
            print('8 - Exit\nPlease type choice')
            m = "0"
            while m != "8":
                m = input("Enter option: ")
                while len(m) != 1 or not m.isdigit():  # check if m is valid
                    print("Option input is invalid")
                    m = input("Enter option: ")
                msg_to_server, c_id, key, is_dr = client_files.options_manager_client(SYSTEM_MSG + m, sock)
                sock.sendall(msg_to_server.encode())
                server_msg = sock.recv(1200).decode()
                if msg_to_server == "512":
                    if server_msg[0] != "6":
                        print(server_msg + "\n")
                    if m == "1" and server_msg == "User added successfully":
                        break
                    elif m == "1":
                        print("Try again" + "\n")  # do nothing
                    else:
                        break
                else:
                    if server_msg[0] != "6":
                        print(server_msg + "\n")
            if m != "8":
                # do later, if sign up / log in went well
                print("You are now logged in.")
                if not is_dr:
                    print("You're a patient, Yay!")
                    client_files.start_data_update_in_server(c_id, sock)
                    client_files.check_doctor_request(sock, c_id)
                    sock.recv(1200)

                    ready_sockets, _, _ = select.select([sock], [], [], timeout)  # cleaning out the receiver if needed
                    if ready_sockets:
                        sock.recv(1024)

                    files_in_server = client_files.get_list_of_files(c_id, sock)
                    print("The server has these files under your ID:")
                    for filename in files_in_server:
                        print("\t" + filename)
                    files_chosen = []
                    yes = input("Get all files? - type 'y' for yes, if you don't, you will be asked for each file.")
                    if yes.lower() == "y":
                        files_chosen = files_in_server
                    else:
                        print("Type 'y' for every file you want to get, everything else to do nothing with it:")
                        for file_name in files_in_server:
                            print(file_name)
                            yes = input("Get this file? ")
                            if yes.lower() == "y":
                                files_chosen += [file_name]
                    path = os.path.dirname(os.path.abspath(__file__))
                    path = path + "\\" + c_id
                    if not os.path.isdir(path):
                        os.mkdir(path)
                    for file_name in files_chosen:
                        response = client_files.get_and_save_file(key, sock, file_name, path, c_id)
                        if " error " in response or len(response) < 16:
                            if response.decode() == "SQL error - no results for that id and filename":
                                print("No files under your ID.")
                        else:
                            print("Files saved in ", response)

                else:
                    print("You're a doctor, yay!")
                    print("Option 1 - send new request to a patient.")
                    print("Option 2 - check status of previous patients and get files.")
                    m = input("Enter option: ")
                    while True:
                        if len(m) == 1 or m.isdigit():
                            if m == '1' or m == '2':
                                break
                        print("Option input is invalid.")
                        m = input("Enter option: ")
                    if m == "1":
                        client_files.new_data_request(key, c_id, sock)
                    else:
                        new_key, p_id = client_files.request_status(c_id, sock, key)
                        sock.recv(1200)
                        files_in_server = client_files.get_list_of_files(c_id, sock)
                        print("The server has these files for you:")
                        for filename in files_in_server:
                            print("\t" + filename)
                        files_chosen = []
                        yes = input("Get all files? - type 'y' for yes. If not, you'll be asked for each file.")
                        if yes.lower() == "y":
                            files_chosen = files_in_server
                        else:
                            print("Type 'y' for every file you want to get, for everything else to do nothing:")
                            for file_name in files_in_server:
                                print(file_name)
                                yes = input("Save this file?")
                                if yes.lower() == "y":
                                    files_chosen += [file_name]
                        path = os.path.dirname(os.path.abspath(__file__))
                        path = path + "\\" + c_id + p_id
                        if not os.path.isdir(path):
                            os.mkdir(path)
                        for file_name in files_chosen:
                            client_files.get_and_save_file_doctor(new_key, sock, "Doc" + file_name, path, c_id + p_id)
                            sock.recv(1200)

                    for i in range(0, 10):
                        sock.sendall("507".encode())
                        server_msg = sock.recv(1200).decode()
                        time.sleep(1)
        # close socket and exit
        sock.close()
    except Exception as e:
        print(e)
        sock.close()
        print("\n\nConnection Error!")


if __name__ == '__main__':
    main()
