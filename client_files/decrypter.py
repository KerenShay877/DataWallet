from Crypto.PublicKey import ECC  # the ECC library
import hashlib  # for md5 hashing
from Crypto.Cipher import AES
from Crypto import Random


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


class Decrypter:
    """
    The Decrypter is the object responsible for the decrypting and for creating its own point in the key exchange.
    Attributes used for key exchange:
        >key(EccKey) - the ECC key used to find R.
    Attributes used for decryption:
        >secret_code(string) - the string md5 hash sum of R's x value.
    """
    def __init__(self, encryption_key="We will rock you"):
        """
        This function does nothing significant except allow it to make a decrypter with a key.
        :return: nothing.
        """
        # initialising attributes
        if len(encryption_key) < 16:
            raise NameError('Length of key insufficient.')
        self.secret_code = encryption_key[:16]
        self.key = 0  # just initialising it with a blank value

    def set_public_data_from_encrypter_and_get_own_point(self, key_data):
        """
        This function receives the data from the Encrypter and uses it to find its own key and then point R. It then
        takes R's x value, hashes it, and makes a twofish key out of it.
        :param key_data: the public key provided by the encrypter containing the curve and the encrypter's point.
        :return: the point which will allow the Encrypter to calculate R.
        """
        public_key = ECC.import_key(key_data)  # making key_data into a usable object in the form of an ECCkey
        self.key = ECC.generate(curve=public_key.curve)  # generating private key
        point_r = public_key.pointQ*self.key.d  # calculating R by multiplying Encrypter's point by private number
        self.secret_code = hashlib.md5(str(point_r.x).encode('utf-8')).hexdigest()[0:16]  # hashing the x value of R
        return self.key.public_key().export_key(format='PEM')  # exporting the public data from decrypter's point

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
        return
