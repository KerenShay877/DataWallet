import server_files


# this func get an option number (+parameter) and return answer
def options_manager(request, sock):
    print(request)
    if "list_files" in request:
        return server_files.list_files(request)
    elif int(request[:3]) == 506:
        return "612"
    elif int(request[:3]) == 513:
        print("At the right place, at least.")  # this does not print whe I request a file on the client side.
        return server_files.get_patient_file(request, sock)
    elif int(request[:3]) == 531:
        return server_files.check_status(request, sock)
    elif int(request[:3]) == 521:
        return server_files.check_doctor_request(request, sock)
    elif int(request[:3]) == 522:
        return server_files.save_files_for_doctor(request, sock)
    elif int(request[:3]) == 530:
        return server_files.new_data_request(request, sock)
    elif int(request[:3]) == 501:
        return server_files.patient_signup(request, sock)
    elif int(request[:3]) == 502:
        return server_files.doctor_signup(request, sock)
    elif int(request[:3]) == 503:
        return server_files.patient_login(request, sock)
    elif int(request[:3]) == 504:
        return server_files.doctor_login(request, sock)
    elif int(request[:3]) == 512 and int(request[3:6]) == 520:
        return server_files.update_files(request[3:])
    elif int(request[:3]) == 507 or int(request[:3]) == 512:
        return "607"
    elif int(request[:3]) == 510:
        return server_files.forgot_password_a(request, sock)
    elif int(request[:3]) == 511:
        return server_files.forgot_password_b(request, sock)
    elif int(request[:3]) == 520:
        return server_files.update_files(request)
    elif int(request[:3]) == 551:
        return server_files.send_key_to_hospital(request, sock)
    else:
        return "608"

