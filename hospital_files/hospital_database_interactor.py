import sqlite3


class SqlErrors:
    def __init__(self):
        self.user_does_not_exist = "SQL error - user doesn't exist"
        self.user_exists = "SQL error - user already exists"
        self.injection_insecurity = "SQL injection danger detected"
        self.unknown = "unknown error"


class SqlSuccess:
    def __init__(self):
        self.user_added = "User added successfully"

# declaring useful variables
sql_errors = SqlErrors()
sql_success_messages = SqlSuccess()


def get_sql_errors_and_success_messages():
    """
        Get the possible return messages. sql_errors, sql_success_messages
    :return: sql_errors, sql_success_messages
    """
    return sql_errors, sql_success_messages


def is_text_safe_for_query(text):  # checking for possible command words to verify security against SQL injection
    """
        Checks if text is safe from injection.
    :param text: text to check.
    :return: whether or not it's safe.
    """
    for command_word in ("drop", "where", "from", "select", "delete", "update", "insert"):
        if command_word in text.lower():
            return False
    return True


class HospitalDbInteractor:
    """
        Object used for connecting to database.
        >database(sqlite3.Connection) - a connection to the database with which we're working.
        >Cursor(sqlite3.Cursor) - the cursor with which we interact with the database
    """

    def __init__(self):
        self.database = sqlite3.connect('hospital database')  # creating and connecting to database.
        self.cursor = self.database.cursor()  # creating a cursor to allow us to interact with said database
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY NOT NULL, 
        encryption_key TEXT NOT NULL);''')
        self.database.commit()  # saving the data to the database long term.

    def add_user(self, id_number, encrypter_key):
        """
            This function checks that there's no user with that ID and then adds a new user.
        :param id_number: id of the user we're adding. Must be unique.
        :param encrypter_key: key of the user we're adding
        :return: Whether it succeeded or not
        """
        if isinstance(id_number, str) and isinstance(encrypter_key, str) and is_text_safe_for_query(encrypter_key):
            # validity and security check
            try:
                if self.get_user_key(id_number) == sql_errors.user_does_not_exist:  # if the user doesn't exist already
                    self.cursor.execute('''INSERT INTO users(id, encryption_key) VALUES(?,?);''',
                                        (id_number, encrypter_key))  # add the user to the database
                    self.database.commit()
                    return sql_success_messages.user_added  # the result saying user added successfully
                else:
                    return sql_errors.user_exists  # the error claiming that the user already exists
            except Exception as e:
                self.database.rollback()  # Roll back any change if something goes wrong
                return str(e)
        else:
            return sql_errors.injection_insecurity

    def get_user_key(self, id_number):
        """
            Gets the encryption key of a user based on id number.
        :param id_number: id of user whose key we're searching for.
        :return: the key or an error
        """
        if isinstance(id_number, str):  # validity check
            try:
                self.cursor.execute('''SELECT encryption_key FROM users WHERE id = :identification;''',
                                    {"identification": id_number})
                result = self.cursor.fetchall()
                if result:  # validity check
                    return result[0][0]  # out of all the results in all the rows
                else:
                    return sql_errors.user_does_not_exist
            except Exception as e:
                self.database.rollback()  # Roll back any change if something goes wrong
                return str(e)
        else:
            return sql_errors.injection_insecurity

    def __del__(self):
        self.database.close()  # closing the database behind us
