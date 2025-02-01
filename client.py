import socket

SERVER_PORT = 7715  # Chosen port number

def connect_to_server ():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("local host", SERVER_PORT))
    print("Attempting to connect server port", SERVER_PORT)

    if socket.error:
        print("Unable to connect to server")
        exit(-1)

    handle_interaction(client_socket)
    client_socket.close()
    print()


def handle_interaction (client):
    while True:
        client_input = input ("Enter Input")
        if client_input == 1:
            break

    """
    Handles interations with the server
    TODO: Add proper interaction between server and client
    :return:
    """
