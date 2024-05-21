import server_files
database_variables = server_files.get_interactor_variables()[2]  # get variables
interactor = server_files.ServerDbInteractor()  # create interactor
user_info = {database_variables.identification_number: "212850424",
             database_variables.email_address: "shraga.aryeh@gmail.com",
             database_variables.name: "Shraga Mildiner",
             database_variables.encrypted_encryption_key: b"0800fc577294c34e0b28ad2839435945",
             database_variables.login_check:
                 b'\xe7\xc6r:\x8f\x1d\xa6d2\x9d^a\xfa\xb5\xc7\x9c\xaa\x94\xa8\x99\xca\x0e*\r\x14\xa3\x8eMT\xf1\xee#',
             database_variables.phone_number: "0587885331",
             database_variables.emergency_contact: "482629017"}
print(interactor.add_user(user_info))
print(interactor.get_user_data(user_info[database_variables.identification_number],
                               database_variables.recreate_password_code))
print(interactor.update_user(user_info[database_variables.identification_number],
                             {database_variables.recreate_password_code: b"test successful 5"}))
print(interactor.get_user_data(user_info[database_variables.identification_number],
                               database_variables.recreate_password_code))
interactor.user_exists(user_info[database_variables.identification_number])
