import server_files

# this func is handling every client that connecting the server.
# for each client the server  create this func by thread


def client_handler(client_soc):
    try:
        client_msg = ""
        # while client hasn't start the conversation
        while client_msg != "500":
            client_msg = client_soc.recv(1200)
            client_msg = client_msg.decode()

        # starting the conversation
        msg = "\n\nHello!\nWelcome to DATAWALLET!\n\n"
        client_soc.sendall(msg.encode())

        # starting getting requests from client and handling them
        client_msg = "0"
        while client_msg[:3] != "508":
            client_msg = client_soc.recv(1200).decode()
            try:
                msg = server_files.options_manager(client_msg, client_soc)
            except Exception as e:
                print(e)
                msg = "611"
            if isinstance(msg, bytes):
                client_soc.sendall(msg)
            else:
                client_soc.sendall(msg.encode())
        # end of exit process
        client_soc.close()
    except Exception as e:
        print(e)
        print("Server Error")
