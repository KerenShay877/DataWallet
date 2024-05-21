import hospital_files


def exchanging_keys(request, sock):
    """
        Function exchanges keys with user, then saves them to database.
    :param request: the id of the user we're talking to.
    :param sock: the socket we're using to communicate.
    :return: success or failure message.
    """
    encrypter_object = hospital_files.Encrypter()  # object for encrypting and exchanging
    # key exchange:
    msg = encrypter_object.get_data_to_send_publicly()
    sock.sendall(msg.encode())
    client_msg = sock.recv(1200).decode()
    encrypter_object.set_r(client_msg)
    msg = encrypter_object.encrypt("YELLOWSUBMARINES")  # just a testing easter egg
    sock.sendall(msg)

    # adding to database
    sql_errors, sql_success_messages = hospital_files.get_sql_errors_and_success_messages()
    interactor = hospital_files.HospitalDbInteractor()
    result = interactor.add_user(request.split(",")[1], encrypter_object.secret_code)
    if result == sql_success_messages.user_added:
        return "750"
    elif result == sql_errors.user_exists:
        return "712"
    elif result == sql_errors.injection_insecurity:
        return "713"
    return "711"


def get_new_client_with_key(sock):
    """
    this func is get new client that already have key because he logged by contacting different hospital


    #### NOT FINISHED
    :param sock:
    :return:
    """
    sock.sendall("ok".encode())
    sock.recv(1200).decode()
    encrypter_object = hospital_files.Encrypter()  # object for encrypting and exchanging
    # key exchange:
    msg = encrypter_object.get_data_to_send_publicly()
    sock.sendall(msg.encode())
    client_msg = sock.recv(1200).decode()
    encrypter_object.set_r(client_msg)
    msg = encrypter_object.encrypt("YELLOWSUBMARINES")  # just a testing easter egg
    sock.sendall(msg)
    enc_key = sock.recv(1200)
    key = encrypter_object.decrypt(enc_key, string=True)
    db_interactor = hospital_files.HospitalDbInteractor()  # creating an interactor
    key = db_interactor.add_user(id, key)  # retrieving user key
    return request


def forget_password(request, sock):
    """

    :param request: 651,id
    :param sock: socket that communicate with the server
    :return:
    """
    sock.sendall("ok".encode())
    print(sock.recv(1200).decode())
    db_interactor = hospital_files.HospitalDbInteractor()  # creating an interactor
    key = db_interactor.get_user_key(request.split(",")[1])  # retrieving user key
    encrypter_object = hospital_files.Encrypter()  # object for encrypting and exchanging
    # key exchange:
    msg = encrypter_object.get_data_to_send_publicly()
    sock.sendall(msg.encode())
    client_msg = sock.recv(1200).decode()
    encrypter_object.set_r(client_msg)
    msg = encrypter_object.encrypt(key.encode())  # just a testing easter egg
    sock.sendall(msg)
    return request
