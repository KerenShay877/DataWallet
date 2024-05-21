import client_files
import math


def recreate_password(request, sock):
    print("1 - Get new code to recreate password")
    print("2 - Recreate password with code")

    m = input("Enter option: ")
    while True:
        if len(m) == 1 or m.isdigit():
            if m == '1' or m == '2':
                break
        print("Option input is invalid")
        m = input("Enter option: ")

    id_num = "0"
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
            id_num = check_var
            break
        print("Invalid id.")

    if m == "1":
        request = "510," + id_num
        sock.sendall(request.encode())
        if sock.recv(1024).decode() == "605":
            print("The code to recreate your password was sent to your email.")
        else:
            print("Error, you can't recreate password of this id's account.")
    elif m == "2":
        code = input("Enter the code you received in your email: ")
        request = "511," + id_num + "," + code
        sock.sendall(request.encode())
        if sock.recv(1200).decode() == "605":
            key = client_files.get_old_key(sock).decode()
            password = ""
            while True:
                check_var = input('Enter new password: ')
                if len(check_var) > 40 or len(check_var) < 6:
                    print("Password must have both letters and digits, and be between 6 and 40 characters.")
                    continue
                if any(x.isalpha()for x in check_var) and any(x.isdigit()for x in check_var):
                    password = check_var
                    check_var = input('Confirm password: ')
                    if check_var == password:
                        break
                    else:
                        print("Password and confirmation are not identical.")
                else:
                    print("Password must have both letters and digits, and be between 6 and 40 characters.")
            while len(password) < 16:
                password += "0"
            encrypter_object = client_files.Encrypter(password)
            enc_key = encrypter_object.encrypt(key)
            sock.sendall(enc_key)
            print("Password changed successfully.")
            return "512", id_num, key, False
        else:
            print("Request is invalid")
    return "506", "0", "0", False


def patient_signup(request, sock):
    ans = "501,"
    print("\nFor sign up fill ALL subsections below")
    # get and check validation of first name syntax
    while True:
        check_var = input('Enter first name: ')
        if all(x.isalpha() or x.isspace() or x == '-' or x == '־' for x in check_var):
            ans += check_var + ","
            break
        print("Invalid syntax of name")

    # get and check validation of last name syntax
    while True:
        check_var = input('Enter last name: ')
        if all(x.isalpha() or x.isspace() or x == '-' or x == '־' for x in check_var):
            ans += check_var + ","
            break
        print("Invalid syntax of name")

    # get and check validation of id syntax
    id_num = ""
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
            ans += check_var + ","
            id_num = check_var
            break
        print("Invalid id")

    # get and check validation of password syntax and then encrypt it
    password = ""
    while True:
        check_var = input('Enter password: ')
        if len(check_var) > 40 or len(check_var) < 6:
            print("Password most have letters and digits, and length bigger than 6 and smaller than 40")
            continue
        if any(x.isalpha()for x in check_var) and any(x.isdigit()for x in check_var):
            password = check_var
            check_var = input('Confirm password: ')
            if check_var == password:
                break
            else:
                print("Password and confirmation are not identical")
        else:
            print("Password most have letters and digits, and length bigger than 6 and smaller than 40")

    # get and check validation of emergency contact
    while True:
        check_var = input('Enter id of emergency contact: ')
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
            ans += check_var + ","
            break
        print("Invalid id")

    # get and check validation of email synatx
    while True:
        check_var = input('Enter email: ')
        if not any(x.isspace() for x in check_var) and check_var.count("@") == 1:
            if check_var.split("@")[1].count(".") == 1:
                ans += check_var + ","
                break
        print("Invalid email")

    # get and check validation of phone number
    while True:
        check_var = input('Enter phone number (only numbers): ')
        if (len(check_var) == 9 or len(check_var) == 10) and check_var.isdigit():
            ans += check_var
            break
        print("Invalid phone number syntax")

    # sending string with request
    sock.sendall(ans.encode())
    while len(password) < 16:
        password += "0"
    # sending the details and check if its ok and account could be created
    # start exchanging keys
    decrypter_object = client_files.get_new_key(sock)
    key = decrypter_object.secret_code
    encrypter_object = client_files.Encrypter(password)
    enc_key = encrypter_object.encrypt(key)
    sock.sendall(enc_key)
    sock.recv(1200)
    encrypter_object_key = client_files.Encrypter(key)
    login_check = encrypter_object_key.encrypt("Hello")
    sock.sendall(login_check)
    return "512", id_num, key, False


def doctor_signup(request, sock):
    ans = "502,"
    print("\nFor sign up fill ALL subsections below")

    ans += input('Enter licence number: ') + ","

    # get doctor's institution name
    while True:
        check_var = input('Enter instatution name: ')
        if all(x.isspace() or x.isalpha() for x in check_var):
            ans += check_var + ","
            break
        print("Invalid syntax")

    # get and check validation of id syntax
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
            ans += check_var + ","
            break
        print("Invalid id")

    # get doctor's specialty
    while True:
        check_var = input('Enter your specialty: ')
        if all(x.isspace() or x.isalpha() for x in check_var):
            ans += check_var
            break
        print("Invalid syntax")

    # sending the details and checking if user can be created
    sock.sendall(ans.encode())
    server_msg = sock.recv(1200).decode()
    if server_msg == "607":
        return "507", "0", "0", False
    print(server_msg)
    return "506", "0", "0", False


def patient_login(request, sock):
    """
    Deals with the login of patients.
    :param request: the request of the user.
    :param sock:
    :return:
    """
    decrypter_object = client_files.Decrypter()
    ans = "503,"
    print("\nFor sign in fill ALL subsections below.")
    id_num = ""
    while True:
        check_var = input('Enter id: ')
        if(len(check_var) != 9) or not check_var.isdigit():
            print("Invalid id. ID does not exist.")
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
            ans += check_var
            id_num = check_var
            break
        print("Invalid id")
    password = input('Enter password: ')
    while len(password) < 16:
        password += "0"
    try:
        encrypter_object = client_files.Encrypter(password)
        sock.sendall(ans.encode())
        encrypted_key = sock.recv(1200)
        sock.sendall(b'received')
        login_check = sock.recv(1200)
        key = encrypter_object.decrypt(encrypted_key, string=True)
        encrypter_object_b = client_files.Encrypter(key)
        login_check = encrypter_object_b.decrypt(login_check, string=True)
        if login_check == "Hello":
            return "512", id_num, key, False
    except Exception as e:
        print(e)
        print("Password is invalid" + "\n")
    return "506", "0", "0", False


def doctor_login(request, sock):
    decrypter_object = client_files.Decrypter()
    ans = "504,"
    print("\nTo sign in fill ALL the sections below.")
    id_num = ""
    while True:
        check_var = input('Enter id: ')
        if(len(check_var) != 9) or not check_var.isdigit():
            print("Invalid id syntax.")
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
            ans += check_var
            id_num = check_var
            break
        print("Invalid id")
    password = input('Enter password: ')
    while len(password) < 16:
        password += "0"
    # encrypter_object = client_files.Encrypter(password)
    # enc_key = encrypter_object.encrypt(key)
    # encrypter_object_key = client_files.Encrypter(key)
    # login_check = encrypter_object_key.encrypt("Hello")
    encrypter_object = client_files.Encrypter(password)
    sock.sendall(ans.encode())
    encrypted_key = sock.recv(1200)
    sock.sendall(b'received')
    login_check = sock.recv(1200)
    key = encrypter_object.decrypt(encrypted_key, string=True)
    sock.sendall(b'received')
    encrypter_object_b = client_files.Encrypter(key)
    login_check = encrypter_object_b.decrypt(login_check, string=True)
    bool = sock.recv(1200).decode()
    if bool == "True":
        if login_check == "Hello":
            return "512", id_num, key, True
    return "506", "0", "0", False
