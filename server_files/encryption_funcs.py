import server_files
import socket
import binascii
SERVER_IP = "127.0.0.1"
SERVER_PORT = 8543


# now it actually creates keys and everything... in the future she will only move data abaout exchanging from the hospitals to patient and backwards.
def exchange_keys_server(sock_of_client, client_id):
    # connect to hospital server
    sock_of_hospital = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hospital_address = (SERVER_IP, SERVER_PORT)
    sock_of_hospital.connect(hospital_address)
    msg = "650," + client_id
    sock_of_hospital.sendall(msg.encode())
    # key exchange
    hospital_msg = sock_of_hospital.recv(1200)
    sock_of_client.sendall(hospital_msg)
    client_msg = sock_of_client.recv(1200)
    sock_of_hospital.sendall(client_msg)
    hospital_msg = sock_of_hospital.recv(1200)
    sock_of_client.sendall(hospital_msg)
    return "607"


def get_encrypted_key(sock):
    """
        Return ("encrypted key", "encrypted login check")
    :param sock:
    :return:
    """

    encrypted_key = sock.recv(1200)  # bytes
    sock.sendall("Ok".encode())  # bytes
    login_check = sock.recv(1200)  # bytes
    return encrypted_key, login_check  # <encrypted key>, <encrypted login check>


def get_user_key(client_id, sock_of_client):
    # connect to hospital server
    sock_of_hospital = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hospital_address = (SERVER_IP, SERVER_PORT)
    sock_of_hospital.connect(hospital_address)
    msg = "651," + client_id + ", Yay"
    sock_of_hospital.sendall(msg.encode())
    # key exchange
    print(sock_of_hospital.recv(1200).decode())
    sock_of_hospital.sendall("HOSPITAL_START_HERE".encode())
    sock_of_client.sendall("CLIENT_START_HERE".encode())
    hospital_msg = sock_of_hospital.recv(1200)
    sock_of_client.sendall(hospital_msg)
    client_msg = sock_of_client.recv(1200)
    sock_of_hospital.sendall(client_msg)
    hospital_msg = sock_of_hospital.recv(1200)
    sock_of_client.sendall(hospital_msg)
    return "607"


def send_key_to_hospital(request, sock_of_client):
    client_id = request.split(",")[1]
    # connect to hospital server
    sock_of_hospital = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hospital_address = (SERVER_IP, SERVER_PORT)
    sock_of_hospital.connect(hospital_address)
    msg = "652," + client_id
    sock_of_hospital.sendall(msg.encode())
    sock_of_hospital.recv(1200)
    sock_of_hospital.sendall("HOSPITAL_START_HERE".encode())
    sock_of_client.sendall("CLIENT_START_HERE".encode())
    # key exchange
    hospital_msg = sock_of_hospital.recv(1200)
    sock_of_client.sendall(hospital_msg)
    client_msg = sock_of_client.recv(1200)
    sock_of_hospital.sendall(client_msg)
    hospital_msg = sock_of_hospital.recv(1200)
    sock_of_client.sendall(hospital_msg)
    return "607"


def text_to_binary(string):
    d = b""
    string = string[2:-1]
    string = string.encode()
    string = str(string)
    string = string[2:-1]
    string = string.replace("\\\\x", "\\x")
    string = string.replace("\\\\x", "\\x")
    string = string.replace("\\\\x", "\\x")
    string = string.replace("\\\\x", "\\x")
    string_list = string.split("\\x")
    if string_list[0] != "" :
        d += string_list[0].encode()
    string_list = string_list[1:]
    list_a = []
    a = ""
    for x in string_list:
        y = x[:2]
        x = x[2:]
        list_a += [[y, x]]
        a += y
    b = binascii.unhexlify(a)
    for i in list_a:
        c = binascii.unhexlify(i[0])
        d += c + i[1].encode()
    return d


