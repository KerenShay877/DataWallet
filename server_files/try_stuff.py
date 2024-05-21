import server_files
import sqlite3
import smtplib, ssl
import random

try:
    errors, successes, variables = server_files.get_interactor_variables()
    example_file = b"""let's just pretend this is a file the hospital sent"""
    database_interactor = server_files.ServerDbInteractor()  # create interactor
    user_id = "325002426"
    try:
        database_interactor.add_file(user_id, "example.txt", example_file)  # add the file
    except Exception as e:
        print(e)  # the errors should all be errors I wrote in the get_interactor_variables() function
    file = database_interactor.get_file(user_id, "example.txt")  # just read the file
    # send to client

    print(database_interactor.get_user_data(user_id, variables.encrypted_encryption_key))
    print(database_interactor.update_user(user_id,
                                    {variables.encrypted_encryption_key:
                                         b"whatever, but longer than 16"}))  # has to be sqlite3.Binary
    print(database_interactor.get_user_data(user_id, variables.encrypted_encryption_key))
except Exception as e:
    errors, successes, variables = server_files.get_interactor_variables()
    print(e)
    if str(e) == errors.user_does_not_exist:
        # you get the point
        pass
