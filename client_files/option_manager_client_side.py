import client_files


# this func gets an option number that the client chose and return answer
def options_manager_client(request, sock):
    if int(request) == 501:
        msg, id_number, key, is_dr = client_files.patient_signup(request, sock)
        return msg, id_number, key, is_dr
    elif int(request) == 502:
        msg, id_number, key, is_dr = client_files.doctor_signup(request, sock)
        return msg, id_number, key, is_dr
    elif int(request) == 503:
        msg, id_number, key, is_dr = client_files.patient_login(request, sock)
        return msg, id_number, key, is_dr
    elif int(request) == 504:
        msg, id_number, key, is_dr = client_files.doctor_login(request, sock)
        return msg, id_number, key, is_dr
    elif int(request) == 505:
        msg, id_number, key, is_dr = client_files.recreate_password(request, sock)
        return msg, id_number, key, is_dr
    else:
        return "508", "0", "0", False
