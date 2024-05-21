import hospital_files


# this function handles one DataWalletServer request.
# for each DataWalletServer request the hospital server create this func by thread
def request_handler(dw_server_soc):
    try:
        # the hospital handles only one request and then closes the communication
        dw_server_msg = dw_server_soc.recv(1200).decode()
        try:
            msg = hospital_files.options_manager(dw_server_msg, dw_server_soc)
        except Exception as e:
            print(e)
            msg = "711"
        dw_server_soc.sendall(msg.encode())
        # end of exit process
        dw_server_soc.close()
    except Exception as e:
        print("Server Error - " + str(e))
