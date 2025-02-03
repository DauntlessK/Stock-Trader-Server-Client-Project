import socket

SERVER_ADDRESS = "" # IP of server
SERVER_PORT = 7715  # Chosen port number

def connect_to_server ():
    #Creates a socket that attempts to connect to server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", SERVER_PORT))
    print("Attempting to connect server port", SERVER_PORT)

    #if socket.error:
    #   print("Unable to connect to server")
    #   exit(-1)

    #Calls to handle interactions to server, once done, socket closes
    handle_interaction(client_socket)
    client_socket.close()
    print("Disconnected from the server port", SERVER_PORT)


def handle_interaction (client):
    #Determines what the client input is and sends messages and info according to the input
    while True:
        client_input = input ("Enter Input: ")
        if client_input == "MSGGET":
            #The message is sent then it receives a message from server
            client.send(client_input.encode())
            message_received = client.recv(1024).decode().strip()
            print(message_received)
        elif client_input == "MSGSTORE":
            #The message is sent then it receives message and sends another message to store
            client.send(client_input.encode())
            message_received = client.recv(1024).decode().strip()
            print(message_received)
            new_msg = input ("Enter message to store: ")
            client.send(new_msg.encode())
        else:
            break

    """
    Handles interations with the server
    TODO: Add proper interaction between server and client
    :return:
    """
connect_to_server()