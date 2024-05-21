import client_files
import math


def new_data_request(doctor_key, doctor_id, sock):
    patient_id = "0"
    while True:
        check_var = input('Enter id: ')
        if(len(check_var) != 9) or not check_var.isdigit():
            print("Invalid id syntax")
            continue
        sum = 0
        help_var = 0
        for i in range(8):
            if i % 2 == 0:
                sum += int(check_var[i])
            else:
                help_var = str(int(check_var[i]) * 2)
                for x in help_var:
                    sum += int(x)
        help_var = int(math.ceil(sum / 10.0)) * 10
        if help_var - sum == int(check_var[8]):
            patient_id = check_var
            break
        print("Invalid id")
    req = "530," + patient_id + "," + doctor_id
    sock.sendall(req.encode())
    if sock.recv(1200).decode() == "607":
        try:
            decrypter_object = client_files.get_new_key(sock)
            key = decrypter_object.secret_code
            encrypter_object = client_files.Encrypter(doctor_key)
            enc_key = encrypter_object.encrypt(key)
            sock.sendall(enc_key)
            return "507"
        except:
            return "516"
    return "516"


def request_status(doctor_id, sock, key):
    patient_id = "0"
    while True:
        check_var = input('Enter id: ')
        if(len(check_var) != 9) or not check_var.isdigit():
            print("Invalid id syntax")
            continue
        sum = 0
        help_var = 0
        for i in range(8):
            if i % 2 == 0:
                sum += int(check_var[i])
            else:
                help_var = str(int(check_var[i]) * 2)
                for x in help_var:
                    sum += int(x)
        help_var = int(math.ceil(sum / 10.0)) * 10
        if help_var - sum == int(check_var[8]):
            patient_id = check_var
            break
        print("Invalid id")
    req = "531," + patient_id + "," + doctor_id
    sock.sendall(req.encode())
    ans = sock.recv(1200).decode()
    if ans == "607":
        sock.sendall("507".encode())
        new_key = client_files.get_old_key(sock).decode()
        return new_key, patient_id
    elif ans == "613":
        print("There is no patient with this id")
    else:
        print("Probably refused to your request")
    return "506", "0"


def get_and_save_file_doctor(key, sock, filename, file_dir, id_num):
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
        print(path)
        sock.sendall(("513," + filename + "," + id_num).encode())  # sending request
        decrypter = client_files.Decrypter(key)  # while waiting, make a decrypter so it can read the file
        file = sock.recv(24000)
        while file == b"607":
            file = sock.recv(24000)
        print(file)
        if b"error" not in file:  # if the word error does not appear in the response
            decrypter.decrypt_file(file, path)  # decrypt and save
            return path
        return file  # else: return the error
    return "Input error - Invalid filename."

