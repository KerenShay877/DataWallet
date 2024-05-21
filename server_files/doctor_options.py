import server_files
FILE_D_PATH = 'doctors.txt'


# this func is the sign up func for doctor
def doctor_signup(request, sock):
    request_split = request.lower().replace(" ", "").split(",")
    if len(request_split) == 5:
        m_license = request_split[1]
        institution = request_split[2]
        identification = request_split[3]
        speciality = request_split[4]

        db_interactor = server_files.ServerDbInteractor()

        result = db_interactor.add_doctor(identification, institution, m_license, speciality)
        sock.sendall(result.encode())
    else:
        return "613"


# this func is the log in func for doctor
def doctor_login(request, sock):
    """
    Sends user their key and the way to test it.
    :param request: 503,id number.
    :param sock: the socket through which to send it.
    :return: "either user logged in successfully" or "613".
    """
    request = request.lower().replace(" ", "").split(",")
    if len(request) == 2:
        errors, success_messages, variables = server_files.get_interactor_variables()
        db_interactor = server_files.ServerDbInteractor()  # creating an interactor
        key = db_interactor.get_user_data(request[1], variables.encrypted_encryption_key)  # retrieving user key
        if key != errors.user_does_not_exist:  # if the user exists
            sock.sendall(key)  # bytes, the encryption key, encrypted with the password
            sock.recv(1200)  # just punctuating the messages

            login_check = db_interactor.get_user_data(request[1], variables.login_check)  # send them the key test
            sock.sendall(login_check)
            sock.recv(1200).decode()
            if db_interactor.is_a_doctor(request[1]):
                sock.sendall("True".encode())
                try:
                    msg = sock.recv(1200).decode()
                    if msg == "42":
                        return "User logged in successfully"
                except Exception as e:
                    print(e)
                    return "error - user failed to login."
            else:
                sock.sendall("False".encode())
    return "613"  # invalid request message


def new_data_request(request, sock):
    patient_id, doctor_id = request.split(",")[1], request.split(",")[2]
    database_interactor = server_files.ServerDbInteractor()
    p_v = database_interactor.user_exists(patient_id)
    # if it pass login, he must be doctor
    if database_interactor.user_exists(patient_id):
        doctors = []
        sock.sendall("607".encode())
        server_files.exchange_keys_server(sock, doctor_id + patient_id)
        key = sock.recv(1200)
        update = [doctor_id, str(key), "0"]
        list_of_doctors = database_interactor.get_user_data(patient_id, server_files.database_variables.treating_doctors)
        if isinstance(list_of_doctors, type(None)):  # if this is the first doctor
            database_interactor.update_user(patient_id, {server_files.database_variables.treating_doctors: str([update])})
        elif list_of_doctors == "":
            database_interactor.update_user(patient_id, {server_files.database_variables.treating_doctors: str([update])})
        else:
            list_of_doctors = list_of_doctors[2:-2]
            list_of_doctors = list_of_doctors.split("], [")
            for i in range(len(list_of_doctors)):
                list_of_doctors[i] = list_of_doctors[i].split(", ")
                list_of_doctors[i][0] = list_of_doctors[i][0][1:-1]
                list_of_doctors[i][1] = list_of_doctors[i][1][1:-1]
                list_of_doctors[i][2] = list_of_doctors[i][2][1:-1]
            list_of_doctors += [update]
            database_interactor.update_user(patient_id, {server_files.database_variables.treating_doctors: str(list_of_doctors)})
        return "607"
    return "613"


def check_status(request, sock):
    patient_id, doctor_id = request.split(",")[1], request.split(",")[2]
    database_interactor = server_files.ServerDbInteractor()
    p_v = database_interactor.user_exists(patient_id)
    if database_interactor.user_exists(patient_id):
        doctors = []
        list_of_doctors = database_interactor.get_user_data(patient_id, server_files.database_variables.treating_doctors)
        if isinstance(list_of_doctors, type(None)): # if this is the first doctor
            sock.sendall("612".encode())
        elif list_of_doctors == "":
            sock.sendall("612".encode())
        else:
            list_of_doctors = list_of_doctors[2:-2]
            list_of_doctors = list_of_doctors.split("], [")
            for i in range(len(list_of_doctors)):
                list_of_doctors[i] = list_of_doctors[i].split(", ")
                list_of_doctors[i][0] = list_of_doctors[i][0][1:-1]
                list_of_doctors[i][1] = list_of_doctors[i][1][1:-1]
                list_of_doctors[i][2] = list_of_doctors[i][2][1:-1]
            for doctor in list_of_doctors:
                if doctor[0] == doctor_id and doctor[2] == "1":
                    sock.sendall("607".encode())
                    sock.recv(1200)
                    server_files.get_user_key(doctor_id + patient_id, sock)
                else:
                    sock.sendall("612".encode())
        return "607"
    else:
        sock.sendall("613".encode())
    return "613"
