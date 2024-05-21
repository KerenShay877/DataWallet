import client_files

# example_file = b"""let's just pretend this is an encrypted file the server sent\0\0\0\0"""  # (len = 64), (64%16 = 0)
file_name = "pasted example file.txt"  # also pretend
directory_for_file_saves = "C:\\Users\\user\\Documents\\"  # directory to save the files
decrypter_object = client_files.Decrypter("984f32d1859dc23b")  # creating a decrypter
example_file = decrypter_object.encrypt_file("C:\\Users\\user\\Documents\\example file.txt")
print(example_file)
a = input("Decrypt? ")
decrypter_object.decrypt_file(example_file, directory_for_file_saves + file_name)  # now it's saved
