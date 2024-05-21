import hospital_files


# this function gets an option number (+parameter) and returns answer
def options_manager(request, sock):
    print(request)
    if request[:3] == "650":
        return hospital_files.exchanging_keys(request, sock)  # if all goes well, should be "750"
    if request[:3] == "651":
        return hospital_files.forget_password(request, sock)  # if all goes well, should be "750"
    if request[:3] == "655":
        return hospital_files.get_files(request, sock)
    else:
        return "711"
