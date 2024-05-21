import client_files


def get_new_key(sock):
    # start exchanging keys
    decrypter_object = client_files.Decrypter()
    server_msg = sock.recv(1200).decode()
    p = decrypter_object.set_public_data_from_encrypter_and_get_own_point(server_msg)
    sock.sendall(p.encode())
    server_msg = sock.recv(1200)
    server_msg = decrypter_object.decrypt(server_msg)
    return decrypter_object


def get_old_key(sock):
    # start exchanging keys
    print(sock.recv(1200).decode())
    decrypter_object = client_files.Decrypter()
    server_msg = sock.recv(1200).decode()
    p = decrypter_object.set_public_data_from_encrypter_and_get_own_point(server_msg)
    sock.sendall(p.encode())
    server_msg = sock.recv(1200)
    server_msg = decrypter_object.decrypt(server_msg)
    return server_msg


def send_old_key(sock):
    sock.recv(1200).decode()
    # start exchanging keys
    decrypter_object = client_files.Decrypter("")  # need to put something in here
    server_msg = sock.recv(1200).decode()
    p = decrypter_object.set_public_data_from_encrypter_and_get_own_point(server_msg)
    sock.sendall(p.encode())
    server_msg = sock.recv(1200)
    server_msg = decrypter_object.decrypt(server_msg)
    print(server_msg)
    encrypter_object = client_files.Encrypter(decrypter_object.secret_code)
    enc_key = encrypter_object.encrypt(key)  # what key?
    sock.sendall(enc_key)
    return server_msg

