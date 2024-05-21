import os
import hospital_files
import time


DIRECTORY_PATH = os.path.dirname(os.path.abspath(__file__)) + "\\patient_md_files"


def get_files(request, sock):
    """

    :param request: 760,id: for example: 325002426,last_time_updated (if never then 0): for example: 1585226467.8931706
    :param sock: socket that response to the communication with the server
    :return: nothing
    """
    files_to_add = []
    time_old = request.split(",")[2]
    """
    path = os.path.dirname(os.path.abspath(__file__))
    path = path + "\\" + c_id
    if not os.path.isdir(path):
        os.mkdir(path)
    """
    files = os.listdir(DIRECTORY_PATH + "\\" + request.split(",")[1])

    for file in files:
        file_time = os.path.getctime(DIRECTORY_PATH + "\\" + request.split(",")[1] + "\\" + file)
        if float(file_time) > float(time_old):
            files_to_add += [file]
    enc_files_list = hospital_files.encrypt_files(files_to_add, request.split(",")[1], sock)
    sock.sendall("Start here".encode())
    sock.recv(1200)
    for file_data in enc_files_list:
        sock.sendall(file_data[0].encode())
        sock.recv(1200)  # sending name and file with buffer in the middle
        sock.sendall(file_data[1])
        sock.recv(1200)  # so we're sure there get to the server one file at a time
    print("done")
    sock.sendall("Done,".encode() + str(time.time()).encode())
    print(str(time.time()))
    return "707"


def encrypt_files(path_list, patient_id, sock):
    enc_files_list = []
    try:
        db_interactor = hospital_files.HospitalDbInteractor()  # creating the object
        encrypter_object = hospital_files.Encrypter(db_interactor.get_user_key(patient_id))  # making an encrypter using key
        for file_name in path_list:
            file_path = DIRECTORY_PATH + "\\" + patient_id + "\\" + file_name
            enc_files_list += [[file_name, encrypter_object.encrypt_file(file_path)]]  # read and encrypt the file
    except Exception as e:
        print(e)
    return enc_files_list
