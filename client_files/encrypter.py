from Crypto.PublicKey import ECC  # the ECC library
import hashlib  # for md5 hashing
from Crypto.Cipher import AES
from Crypto import Random
import random  # the random generator to pick a curve


possible_curves = ('P-256', 'P-384', 'P-521')  # possible curve IDs


def pad(plaintext):
    """
    Pads message so it can be used in a block cipher.
    :param plaintext: the plaintext to be encrypted.
    :return: padded plaintext.
    """
    # different padding methods for files and text
    if isinstance(plaintext, str):
        return (plaintext + "\0" * (AES.block_size - len(plaintext) % AES.block_size)).encode()
    elif isinstance(plaintext, bytes):
        return plaintext + b"\0" * (AES.block_size - len(plaintext) % AES.block_size)


class Encrypter:
    """
    The encrypter is the object responsible for setting key exchange parameters and for encrypting the files on the
    hospital side. It has a number of attributes;
    Attributes used for key exchange:
        >key(EccKey) - the ECC key used to find R.
    Attributes used for encryption:
        >secret_code(string) - the string md5 hash sum of R's x value.
    """

    def __init__(self, encryption_key="We will rock you"):
        """
            This function sets the key and initialises the other variables.
        :param encryption_key: a key. Must be at least 16 bytes!
        """
        if len(encryption_key) < 16:
            raise NameError('Length of key insufficient.')
        # initialising attributes
        self.secret_code = encryption_key[0:16]
        self.key = ECC.generate(curve=possible_curves[random.randrange(0, 2)])  # picks random curve and sets key

    def get_data_to_send_publicly(self):
        """
        Gets the public key.
        :return: the public data from key. All the information except the private number.
        """
        return self.key.public_key().export_key(format='PEM')  # get public data from private key, exporting as a string

    def set_r(self, key_data):
        """
        Calculating the shared point and then the shared key. Takes decrypter point and multiplies it by private number.
        :param key_data: key from the client containing their point.
        :return: nothing.
        """
        decrypter_key = ECC.import_key(key_data)  # making key_data into a usable object in the form of an ECC key
        point_r = decrypter_key.pointQ*self.key.d  # calculating r by multiplying decrypter's key by private number
        self.secret_code = hashlib.md5(str(point_r.x).encode('utf-8')).hexdigest()[0:16]  # hashing the x value

    def encrypt(self, message):
        """
        Takes the message and the secret_code and encrypts with a random initialising vector.
        :param message: the message to be encrypted. Can be bytes or str.
        :return: encrypted cipher text.
        """
        message = pad(message)  # padding message so that it's divisible into blocks.
        initialisation_vector = Random.new().read(AES.block_size)  # random iv for encryption. Needed for type of cipher
        cipher = AES.new(self.secret_code.encode(), AES.MODE_CBC, initialisation_vector)  # cipher with secret_code & iv
        return initialisation_vector + cipher.encrypt(message)

    def encrypt_file(self, file_path):
        """
        Reads file and sends it to encrypt().
        :param file_path: path to file.
        :return: encrypted file.
        """
        with open(file_path, 'rb') as source_file:
            plaintext = source_file.read()
        return self.encrypt(plaintext)

    def decrypt(self, message, string=False):
        """
        Takes message and decrypts it with secret_code.
        :param message: the encrypted message.
        :param string: whether or not it's a string.
        :return: plaintext in bytes.
        """
        initialisation_vector = message[:AES.block_size]  # random iv for encryption. Needed for type of cipher
        cipher = AES.new(self.secret_code.encode(), AES.MODE_CBC, initialisation_vector)  # new cipher
        plaintext = cipher.decrypt(message[AES.block_size:])
        result = plaintext.rstrip(b"\0")  # getting rid of padding
        if string:
            result = result.decode()
        return result

    def decrypt_file(self, file, file_path):
        """
        Decrypts a file and creates it in the specified path.
        :param file: the encrypted bytes.
        :param file_path: the path in which to create the file.
        :return: nothing.
        """
        plaintext = self.decrypt(file)
        with open(file_path, 'wb') as destination_file:
            destination_file.write(plaintext)