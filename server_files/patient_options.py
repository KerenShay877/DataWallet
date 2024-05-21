import server_files
import smtplib
import ssl
import random
import socket
SERVER_IP = "127.0.0.1"
SERVER_PORT = 8543

# this func is the sign up func for patient


def patient_signup(request, sock):
    """
    Sign up for patient.
    :param request: request_number, first_name, last_name, id, id_emergency, email, phone_number
    :param sock: the socket to communicate with.
    :return:
    """
    request = request.lower().replace(" ", "").split(",")  # parsing the string
    if len(request) == 7:  # validity check
        server_files.exchange_keys_server(sock, request[3])  # getting ECC encryption set up

        encrypted_key, login_check = server_files.get_encrypted_key(sock)
        # add patient to database
        db_vars = server_files.get_interactor_variables()[2]
        db_interactor = server_files.ServerDbInteractor()  # creating an interactor
        result = db_interactor.add_user(
            {db_vars.identification_number: request[3],
                db_vars.name: request[1] + " " + request[2],
                db_vars.email_address: request[5],
                db_vars.emergency_contact: request[4],
                db_vars.phone_number: request[6],
                db_vars.encrypted_encryption_key: encrypted_key,
                db_vars.login_check: login_check}
                    )  # adding user to database with data in request
        sock.sendall(result.encode())  # the result from trying to add the user.
        return "607"  # success message
    else:
        return "613"  # invalid request message


# this function is the login function for a patient
def patient_login(request, sock):
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

            try:
                msg = sock.recv(1200).decode()
                if msg == "42":
                    return "User logged in successfully"
            except Exception as e:
                print(e)
                return "error - user failed to login."
    return "613"  # invalid request message


def forgot_password_a(request, sock):  # what's the socket for?
    """

    :param request: 510, id
    :param sock:
    :return:
    """
    identification = request.split(",")[1]
    smtp_server = "smtp.gmail.com"
    port = 587  # For star ttls
    sender_email = "datawallet604@gmail.com"
    password = "dataw604!"
    code = str(random.randrange(10000, 100000))
    database_interactor = server_files.ServerDbInteractor()
    receiver_email = database_interactor.get_user_data(identification, server_files.database_variables.email_address)
    print(receiver_email)
    message = """\
Subject: Recreate DataWallet Password

Your code is: < """ + code + """ > . This is an automatic massage. Do not reply."""
    # Create a secure SSL context
    context = ssl.create_default_context()
    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # Can be omitted
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
        database_interactor.update_user(identification, {server_files.database_variables.recreate_password_code: code})
    except Exception as e:
        # Print any error messages to stdout
        print(e)
        server.quit()
        return "611"
    server.quit()
    return "605"


def forgot_password_b(request, sock):
    """
    Updates the database and replaces the password
    :param request: 511, id, recreate password code
    :param sock: the socket through which to communicate.
    :return:
    """
    identification = request.split(",")[1]
    code = request.split(",")[2]
    # Recreate password code
    database_interactor = server_files.ServerDbInteractor()
    db_code = database_interactor.get_user_data(identification, server_files.database_variables.recreate_password_code)
    if str(db_code) == code:
        sock.sendall("605".encode())
        server_files.get_user_key(identification, sock)
        new_enc_key = sock.recv(1024)
        database_interactor.update_user(identification, {server_files.database_variables.recreate_password_code: "0"})
        database_interactor.update_user(identification,
                                        {server_files.database_variables.encrypted_encryption_key:
                                         new_enc_key})
        return "605"
    else:
        return "611"


def update_files(request):
    identification = request.split(",")[1]
    # connect to hospital server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hospital_address = (SERVER_IP, SERVER_PORT)
    sock.connect(hospital_address)
    database_interactor = server_files.ServerDbInteractor()
    last_time = database_interactor.get_user_data(identification, server_files.database_variables.last_update)
    if isinstance(last_time, type(None)):
        last_time = "0"
    msg = "655," + identification + "," + last_time
    sock.sendall(msg.encode())
    msg = sock.recv(1200)
    sock.sendall("ok".encode())
    file_name = sock.recv(1200).decode()
    sock.sendall("ok".encode())
    while file_name[:4] != "Done":
        enc_file = sock.recv(24000)
        sock.sendall("ok".encode())
        database_interactor.add_file(identification, file_name, enc_file)
        file_name = sock.recv(1200).decode()
        sock.sendall("ok".encode())
    msg = file_name.split(",")[1]
    database_interactor.update_user(identification, {server_files.database_variables.last_update: msg})
    return "607"


def get_patient_file(request, sock):
    """
    Asks the database for the file, returns the result.
    :param request: string in the form of "file_request,blood tests.pdf,212850424"
    :param sock: the socket to send through.
    :return: either the file, or the error message.
    """
    requests = request.split(",")
    interactor = server_files.ServerDbInteractor()
    print(requests[2])
    print(requests[1])
    return interactor.get_file(requests[2], requests[1])


def check_doctor_request(request, sock):
    database_interactor = server_files.ServerDbInteractor()
    patient_id = request.split(",")[1]
    list_of_requests = database_interactor.get_user_data(patient_id, server_files.database_variables.treating_doctors)
    if not isinstance(list_of_requests, type(None)):  # if there are requests
        if list_of_requests != "":
            print(list_of_requests)
            sock.sendall("Yes".encode())
            sock.recv(1200).decode()
            sock.sendall(list_of_requests.encode())
            approved_doctors_list = sock.recv(1200).decode()
            database_interactor.update_user(patient_id, {server_files.database_variables.treating_doctors: approved_doctors_list})
        else:
            sock.sendall("No".encode())
    else:
        sock.sendall("No".encode())
    return "607"


def save_files_for_doctor(request, sock):
    database_interactor = server_files.ServerDbInteractor()
    patient_id, doctor_id = request.split(",")[1], request.split(",")[2]
    sock.sendall("okhere".encode())
    sock.recv(1200)
    server_files.get_user_key(doctor_id + patient_id, sock)
    file_name = sock.recv(1200).decode()
    sock.sendall("ok".encode())
    while file_name[:4] != "Done":
        enc_file = sock.recv(24000)
        sock.sendall("ok".encode())
        try:
            database_interactor.add_file(doctor_id + patient_id, "Doc:" + file_name, enc_file)
        except Exception as e:
            print(e)
        file_name = sock.recv(1200).decode()
        sock.sendall("ok".encode())
        print()
    msg = file_name.split(",")[1]
    return "607"


def list_files(request):
    """

    :param request:
    :return:
    """
    interactor = server_files.ServerDbInteractor()
    files = interactor.get_all_files(request.split(",")[1])
    result = ""
    for file_name in files:
        result += file_name + ","
    return result[:-1]
