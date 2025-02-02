import socket

SERVER_PORT = 7715  # Chosen port number

def run_server():
    """
    Creates a loop that runs endlessly, waiting for connections.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", SERVER_PORT))
    server_socket.listen(1)
    print("Server is running on port", SERVER_PORT)

    while True:
        client_socket, client_address = server_socket.accept()
        print("Accepted connection from:", client_address)
        handle_client(client_socket)
        client_socket.close()

def handle_client(client_socket):
    """
    Called when a client connection is accepted.
    It receives the command from the client and checks if it is MSGGET or MSGSTORE.
    Depending on the command, it calls the corresponding handler function.
    :param client_socket:
    :return:
    """
    while True:
        command = client_socket.recv(1024).decode().strip()
        if command == "MSGGET":
            handle_msgget(client_socket)
        elif command == "MSGSTORE":
            handle_msgstore(client_socket)
        else:
            break

def handle_msgget(client_socket):
    """
    Responsible for handling the MSGGET command from the client.
    Sends response "200 OK"
    :param client_socket:
    :return:
    """
    response = "200 OK\n"
    client_socket.send(response.encode())

def handle_msgstore(client_socket):
    """
    Responsible for handling the MSGSTORE command from the client.
    Sends the response "200 OK" to the client to signal message can be sent.
    Then, the message is received from the client using the client socket and prints the message.
    :param client_socket:
    :return:
    """
    client_socket.send("200 OK\n".encode())
    new_message = client_socket.recv(1024).decode().strip()
    print("Received new message:", new_message)

run_server()
