import sqlite3


class DoctorVariables:
    def __init__(self):
        self.medical_license = "license"
        self.institutions = "institutions"
        self.speciality = "speciality"
        self.encrypted_patients_keys = "patient_keys"


class DatabaseVariables:
    def __init__(self):
        self.name = "name"
        self.email_address = "email"
        self.emergency_contact = "contact"
        self.identification_number = "id"
        self.encrypted_encryption_key = "key"
        self.phone_number = "phone"
        self.login_check = "login_check"
        self.treating_doctors = "doctors_with_access"
        self.recreate_password_code = "forgot_password_verification"
        self.last_update = "data_last_changed"
        self.doctor_options = DoctorVariables()


class SqlErrors:
    def __init__(self):
        self.user_does_not_exist = "SQL error - user doesn't exist"
        self.user_exists = "SQL error - user already exists"
        self.invalid_input = "error - invalid input"
        self.filename_or_id_no_result = "SQL error - no results for that id and filename"
        self.file_exists = "SQL error - file already exists"
        self.injection_insecurity = "SQL error -  injection danger detected"
        self.is_already_doctor = "SQL error - user is already a doctor"
        self.permission_breach = "SQL error - user has no permission to access "
        self.unknown = "unknown error"


class SqlSuccess:
    def __init__(self):
        self.user_added = "User added successfully"
        self.file_added = "File added successfully"
        self.doctor_added = "Doctor added successfully"
        self.doctor_updated = "Doctor updated successfully"
        self.user_updated = "User updated successfully"

# declaring useful variables
sql_errors = SqlErrors()
sql_success_messages = SqlSuccess()
database_variables = DatabaseVariables()


def get_interactor_variables():
    """
    Get the possible return messages. sql_errors, sql_success_messages, db variables.
    :return: sql_errors, sql_success_messages, database_variables.
    """
    return sql_errors, sql_success_messages, database_variables


def is_text_safe_for_query(text):  # checking for possible command words to verify security against SQL injection
    """
    Checks if text is safe from injection.
    :param text: (string) text to check.
    :return: (bool) whether or not it's safe.
    """
    if isinstance(text, str):
        for command_word in ("drop", "where", "from", "select", "delete", "update", "insert", "set"):
            if command_word in text.lower():
                return False
    return True


class ServerDbInteractor:
    def __init__(self):
        """
        Creating the database and tables, initiating variables.
        """
        self.database = sqlite3.connect('server database')  # creating and connecting to database
        self.cursor = self.database.cursor()  # creating a cursor to allow us to interact with said database

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY NOT NULL, name TEXT NOT NULL,
         email TEXT NOT NULL, contact TEXT NOT NULL, key BLOB NOT NULL, phone TEXT NOT 
         NULL, license TEXT, institutions TEXT, speciality TEXT, login_check BLOB NOT NULL, 
         doctors_with_access TEXT, forgot_password_verification BLOB, patient_keys TEXT, data_last_changed TEXT);''')
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS files (id TEXT NOT NULL, file BLOB, file_name TEXT UNIQUE);''')
        self.database.commit()  # saving the data to the database long term

    def add_user(self, data):
        """
        Adding a normal user to the SQL database.
        :param data: (dict) "column": value.
        :return: (string) success or failure.
        """
        if isinstance(data, dict):  # if the data is the right type
            if not self.user_exists(data[database_variables.identification_number]):  # if the user does not exist

                user_variables = list(database_variables.__dict__.values())[:-1]
                for column in data.keys():  # checking if the keys in data are correct
                    if column not in user_variables:  # meaning that if the column is not in the db
                        return sql_errors.invalid_input
                    if not is_text_safe_for_query(data[column]):  # if the value is unsafe
                        return sql_errors.injection_insecurity

                # now it converts things to the right type if they're wrong, and if they can't be converted, error
                # first the key
                if isinstance(data[database_variables.encrypted_encryption_key], bytes):  # if the key is binary
                    data[database_variables.encrypted_encryption_key] = \
                        sqlite3.Binary(data[database_variables.encrypted_encryption_key])  # convert to memoryview
                elif not isinstance(data[database_variables.encrypted_encryption_key], memoryview):  # if neither
                    return sql_errors.invalid_input
                # now the login check
                if isinstance(data[database_variables.login_check], bytes):  # if the login check is binary
                    data[database_variables.login_check] = \
                        sqlite3.Binary(data[database_variables.login_check])  # convert to memoryview
                elif not isinstance(data[database_variables.login_check], memoryview):  # if neither
                    return sql_errors.invalid_input

                # add the user to database
                try:
                    self.cursor.execute('''INSERT INTO users(name, email, contact, id, key, phone, login_check) 
                    VALUES (:name, :email, :contact, :id, :key, :phone, :login_check);''', data)
                    self.database.commit()  # save to long term memory
                    return sql_success_messages.user_added  # return success
                except Exception as e:
                    self.database.rollback()  # roll back any change if something goes wrong
                    return sql_errors.unknown + ": " + str(e)
            return sql_errors.user_exists
        return sql_errors.invalid_input

    def user_exists(self, id_number):
        return isinstance(id_number, str) and \
               is_text_safe_for_query(id_number) and \
               self.get_user_data(id_number, database_variables.email_address) != sql_errors.user_does_not_exist

    def get_user_data(self, id_number, request):
        """
        Gets whatever you request.
        :param request: (string) a value from database_variables.
        :param id_number: (string) user id.
        :return: (string) result of query or appropriate error message.
        """
        requests = list(database_variables.__dict__.values())[:-1] + \
            list(database_variables.doctor_options.__dict__.values())  # minus the doctor variables object
        if isinstance(id_number, str) and is_text_safe_for_query(id_number) and request in requests:  # validity check
            try:
                self.cursor.execute('''SELECT ''' + request + ''' FROM users WHERE id = ''' + id_number)
                # sending the query
                result = self.cursor.fetchall()  # getting the response
                if result:  # validity check
                    return result[0][0]  # out of all the results in all the rows
                else:
                    return sql_errors.user_does_not_exist
            except Exception as e:
                self.database.rollback()  # Roll back any change if something goes wrong
                return sql_errors.unknown + ": " + str(e)
        return sql_errors.invalid_input

    def add_file(self, id_number, filename, file):
        """
        Adds file to the database.
        :param id_number: (string) id of the user whose file is being added.
        :param filename: (string) the name (with ending) of the file in question.
        :param file: (bytes) the bits of the file that are there.
        :return: (string) success or error message.
        """
        if isinstance(id_number, str) and is_text_safe_for_query(filename) and is_text_safe_for_query(file):
            # validity check
            try:
                if self.get_file(filename, id_number) == sql_errors.filename_or_id_no_result:
                    # the file doesn't already exist
                    if self.get_user_data(database_variables.email_address, id_number):  # if user exists
                        self.cursor.execute('''INSERT INTO files(id, file, file_name) 
                                            VALUES(:id, :file, :file_name);'''
                                            , {"id": id_number, "file": sqlite3.Binary(file),
                                               "file_name": filename})
                        # add file
                        self.database.commit()  # commit the database
                        return sql_success_messages.file_added
                    else:
                        raise NameError(sql_errors.user_does_not_exist)
                else:
                    raise NameError(sql_errors.file_exists)
            except Exception as e:
                self.database.rollback()  # Roll back any change if something goes wrong
                if str(e) == "UNIQUE constraint failed: files.file_name":
                    raise NameError(sql_errors.file_exists)
                raise NameError(str(e))
        else:
            return sql_errors.invalid_input

    def get_file(self, id_number, filename):
            """
            Gets files you request. They should be entirely encrypted.
            :param filename: the name of the file you're looking for.
            :param id_number: user id.
            :return: result of query or appropriate error message.
            """
            if isinstance(id_number, str) and is_text_safe_for_query(filename):  # validity check
                try:
                    self.cursor.execute('''SELECT file FROM files WHERE id = :identification AND file_name =
                         :filename;''', {"identification": id_number, "filename": filename})  # sending the query
                    result = self.cursor.fetchall()
                    if result:  # validity check
                        return result[0][0]  # out of all the results in all the rows I want the first (the only)
                    else:
                        return sql_errors.filename_or_id_no_result  # the error saying there's no results
                except Exception as e:
                    self.database.rollback()  # Roll back any change if something goes wrong
                    return sql_errors.unknown + ": " + str(e)
            else:
                return sql_errors.invalid_input  # invalid input error

    def add_doctor(self, id_number, institutions, med_license, speciality):
        """
        promotes normal user to doctor.
        :param id_number: (str) id of existing user.
        :param institutions: (string) place of work.
        :param med_license: (str) medical license number.
        :param speciality: (string) medical speciality.
        :return: success or failure messages.
        """
        if isinstance(id_number, str) and isinstance(med_license, str) and isinstance(institutions, str) and \
                isinstance(speciality, str):  # security check
            if is_text_safe_for_query(institutions) and is_text_safe_for_query(speciality):  # security check
                if not self.is_a_doctor(id_number):  # checking if the user is already a doctor
                    try:
                        self.cursor.execute("UPDATE users SET license = :li, speciality = :spec, institutions = :ins "
                                            "WHERE id = :id;", {"li": med_license,
                                                                "spec": speciality,
                                                                "ins": institutions,
                                                                "id": id_number})
                        self.database.commit()  # saving to long term database
                        return sql_success_messages.doctor_added
                    except Exception as e:
                        self.database.rollback()  # Roll back any change if something goes wrong
                        return sql_errors.unknown + ": " + str(e)
                else:
                    return sql_errors.is_already_doctor
            else:
                return sql_errors.injection_insecurity
        else:
            return sql_errors.invalid_input

    def is_a_doctor(self, id_number):
        """
        Checks if id belongs to a doctor.
        :param id_number: (string) the id of the user in question.
        :return: (bool) if the user in question is a doctor.
        """
        if isinstance(id_number, str):  # validity check
            if self.get_user_data(id_number, database_variables.doctor_options.medical_license):
                return True
            return False
        return sql_errors.invalid_input

    def get_all_files(self, id_number):
        """
        Gets names of all the files under user ID.
        :param id_number: ID of user we're looking at.
        :return: ['file A.pdf', 'file B.jpeg']
        """
        if is_text_safe_for_query(id_number):  # security
            if self.user_exists(id_number):
                try:
                    self.cursor.execute('''SELECT file_name FROM files WHERE id = ''' + id_number + ';')  # send query
                    response = self.cursor.fetchall()
                    result = []
                    for list_result in response:  # response is an array of lists of strings
                        result.append(list_result[0])  # only the string
                    return result
                except Exception as e:
                    self.database.rollback()  # Roll back any change if something goes wrong
                    return sql_errors.unknown + str(e)
            return sql_errors.user_does_not_exist
        return sql_errors.injection_insecurity

    def update_user(self, id_number, data):
        """
        Updates user data. ID is string, data is dict of syntax "db_variable": new value
        :param id_number: string of id number
        :param data: dict of syntax "db_variable": new value
        :return: success/error message accordingly
        """
        if self.user_exists(id_number):
            # if user exists
            if isinstance(data, dict):  # type validity check
                # making lists of the variables for validation checks
                db_variables = list(database_variables.__dict__.values())[:-1]  # minus the doctor variables object
                doctor_variables = list(database_variables.doctor_options.__dict__.values())
                for variable in data.keys():  # iterate over the data they want to change
                    if is_text_safe_for_query(variable) and \
                            is_text_safe_for_query(data[variable]) and \
                            variable != database_variables.identification_number and \
                            variable in db_variables + doctor_variables:  # validity check
                        if not(variable in doctor_variables and not self.is_a_doctor(id_number)):
                            # meaning if the user isn't trying to breach permissions
                            if variable == database_variables.encrypted_encryption_key:  # if they want to change key
                                if isinstance(data[variable], bytes):  # if it's bytes, it needs to be memoryview
                                    data[variable] = sqlite3.Binary(data[variable])
                                elif isinstance(data[variable], memoryview):  # if it's not memoryview, error
                                    self.database.rollback()
                                    return sql_errors.invalid_input
                            try:
                                # updating the data
                                self.cursor.execute("UPDATE users SET " + variable + " = :new WHERE id = "
                                                    + id_number + ";",
                                                    {"new": data[variable]})
                            except Exception as e:
                                self.database.rollback()  # Roll back any change if something goes wrong
                                return sql_errors.unknown + ": " + str(e)
                        else:
                            # if they're trying to access things they shouldn't
                            return sql_errors.permission_breach + variable
                    else:  # if the text is unsafe
                        return sql_errors.invalid_input
                # if everything went well
                self.database.commit()  # saving to long term database
                return sql_success_messages.user_updated  # return success
            else:  # if the input was of wrong type
                return sql_errors.invalid_input
        else:
            return sql_errors.user_does_not_exist

    def __del__(self):
        self.database.close()  # closing the database behind us


# server_database_interactor = ServerDbInteractor()

# testing

# print(server_database_interactor.add_doctor(212850424, "Kaplan", 324542, "internal medicine"))
# print(server_database_interactor.get_user_data(212850424, database_variables.doctor_options.institutions))
# print(server_database_interactor.is_a_doctor(212850424))
# print(server_database_interactor.add_file(212850424, sql_errors, "errors"))
"""
database_interactor = server_files.ServerDbInteractor()
    errors, successes, variables = server_files.get_interactor_variables()
    user_info = {variables.identification_number: "212850424",
                 variables.email_address: "shraga.aryeh@gmail.com",
                 variables.name: "Shraga Mildiner",
                 variables.encrypted_encryption_key: b"0800fc577294c34e0b28ad2839435945",
                 variables.login_check:
                     b'\xe7\xc6r:\x8f\x1d\xa6d2\x9d^a\xfa\xb5\xc7\x9c\xaa\x94\xa8\x99\xca\x0e*\r\x14\xa3\x8eMT\xf1\xee#',
                 variables.phone_number: "0587885331",
                 variables.emergency_contact: "482629017"}
    result = database_interactor.add_user(user_info)
    if result != successes.user_added:
        # failure
        print(result)
    print(database_interactor.get_user_data(user_info[variables.identification_number], variables.phone_number))

"""
