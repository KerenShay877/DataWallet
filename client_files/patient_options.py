import client_files
import os


def start_data_update_in_server(identification, sock):
    """
    this func sends to the server request to start update the data in the hospitals.
    :param identification: id of the patient.
    :param sock: the socket that response to the communication with the server.
    :return: just confirmation number, the func isn't really important to the client side.
    """
    request = "520," + identification + ","
    print("Asking server to update...")  # why?
    sock.sendall(request.encode())
    sock.recv(1200)
    return "607"


def get_list_of_files(id_num, sock):
    """

    :param id_num:
    :param sock:
    :return:
    """
    msg = "list_files," + id_num
    sock.sendall(msg.encode())
    return sock.recv(1200).decode().split(",")


def get_and_save_file(key, sock, filename, file_dir, id_num):
    """
    Sends a request to server for a specific file, then decrypts and saves it.
    :param key: decryption key.
    :param sock: socket through which to communicate.
    :param filename: name of the file to request.
    :param file_dir: directory of file. Where to save it to.
    :param id_num: user identification.
    :return: either the error from the server, or the directory to the file.
    """

    if "," not in filename:
        path = file_dir + "\\" + filename  # path of the file
        sock.sendall(("513," + filename + "," + id_num).encode())  # sending request
        decrypter = client_files.Decrypter(key)  # while waiting, make a decrypter so it can read the file
        file = sock.recv(24000)  # getting the file
        if b"error" not in file and len(file) > 16:  # if the word error does not appear in the response
            try:
                decrypter.decrypt_file(file, path)  # decrypt and save
            except Exception as e:
                print("Client error", e)
                return "Unknown error occurred."
            return path
        return file.decode()  # else: return the error
    return "Input error - Invalid filename."


def send_key_to_new_hospital(sock, id_num):
    request = "551," + id_num
    sock.sendall(request.encode())
    client_files.send_old_key(sock)
    return "607"


def check_doctor_request(sock, patient_id):
    request = "521," + patient_id
    sock.sendall(request.encode())
    ans = sock.recv(1200).decode()
    print("Checking if any doctors have requested your data...")  #
    if ans == "Yes":
        sock.sendall("ok".encode())
        list_of_doctors = sock.recv(1200).decode()
        list_of_doctors = list_of_doctors[1:-1]
        list_of_doctors = list_of_doctors.split("], [")
        for i in range(len(list_of_doctors)):
            list_of_doctors[i] = list_of_doctors[i].split(", ")
            list_of_doctors[i][0] = list_of_doctors[i][0][1:-1]
            list_of_doctors[i][1] = list_of_doctors[i][1][1:-1]
            list_of_doctors[i][2] = list_of_doctors[i][2][1:-1]
        list_of_doctors[0][0] = list_of_doctors[0][0][1:]
        list_of_doctors[-1][-1] = list_of_doctors[-1][-1][:-1]
        aproved_doctors_list = []
        next_func_list = []
        for doctor_request in list_of_doctors:  # why not get their names instead?
            doctor_id = doctor_request[0]
            yes = input("Type 'y' if you want to approve " + doctor_id + "'s request:")
            if yes.lower() == 'y':
                print("Sending permission.")
                doctor_request[2] = "1"
                doctor_request[1] = doctor_request[1].replace("\\\\", "\\")
                doctor_request[1] = doctor_request[1].replace("\\\\", "\\")
                aproved_doctors_list += [doctor_request]
                next_func_list += [doctor_id]
        sock.sendall(str(aproved_doctors_list).encode())
        print(sock.recv(1200).decode())
        sock.sendall("507".encode())
        print(sock.recv(1200).decode())
        for doctor_id in next_func_list:
            client_files.approve_doctors_requests(sock, patient_id, doctor_id)
            sock.recv(1200)
        return "Was"
    else:
        print("No doctors requested the data.")
        return "No doc"


def approve_doctors_requests(sock, patient_id, doctor_id):
    """
    this func can run only after get_and_save_files() func run. it get the path of the client's directory
    ask from the hospital for the key that the doctor created for this request
    :param sock:
    :param patient_id:
    :param doctor_id:
    :return:
    """
    request = "522," + patient_id+ "," + doctor_id
    sock.sendall(request.encode())
    # TO DO: add func in server that get all files that conected to the client and send it client
    files_in_server = ["20.5.2019-meuhedet-yonatan dan-rentgen.jfif", "19.03.2020-meuhedet-sivan levi-baby.jfif", "er.txt", "26.03.2020-meuhedet-lusi mashehu-XR.txt", "21.5.2019-meuhedet-roni bar-child.txt"]
    files_chosen = []
    yes = input("Get them all file? - type 'y' for yes, if you wont type 'y' you will be asked for each files ")
    if yes.lower() == "y":
        files_chosen = files_in_server
    else:
        print("\n" + doctor_id + "\n")
        print("Type 'y' for every file you want the doctor to have, everything else to do nothing with it:")
        for file_name in files_in_server:
            print(file_name)
            yes = input("Save this file? ")
            if yes.lower() == "y":
                files_chosen += [file_name]
    path = os.getcwd()
    path = path + "\\" + patient_id + "\\"
    if not os.path.isdir(path):
        os.mkdir(path)
    sock.sendall("ok".encode())
    sock.recv(1200).decode()
    key = client_files.get_old_key(sock).decode()
    print(key)
    encrypter_object = client_files.Encrypter(key)
    for file_name in files_chosen:
        file_path = path + file_name
        sock.sendall(file_name.encode())
        sock.recv(1200).decode()
        sock.sendall(encrypter_object.encrypt_file(file_path))
        sock.recv(1200).decode()
    sock.sendall("Done".encode())

    return "stuff"
