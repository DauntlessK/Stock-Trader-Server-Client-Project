import socket

SERVER_ADDRESS = "" # IP of server
SERVER_PORT = 7715  # Chosen port number
index = 0

def connect_to_server ():
    """
    Creates a socket that attempts to connect to server
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", SERVER_PORT))
    print("Attempting to connect server port", SERVER_PORT)

    #Calls to handle interactions to server, once done, socket closes
    handle_interaction(client_socket)
    client_socket.close()
    print("Disconnected from the server port", SERVER_PORT)


def handle_messages(client_input, client):
    """
    Handles commands with two message interactions
    :param client_input: string
    :param client:
    :return:
    """
    client.send(client_input.encode())
    information = client.recv(1024).decode().strip()
    print(information, '\n')
    information = client.recv(1024).decode().strip()
    print(information, '\n')



def handle_buy(client_input, client):
    """
    Sends info to server to buy
    :param client_input: string
    :param client:
    """
    client.send(client_input.encode())
    information = client.recv(1024).decode().strip()
    print(information, '\n')

def handle_sell(client_input, client):
    """
    Sends info to server to sell
    :param client_input: string
    :param client:
    """
    client.send(client_input.encode())
    information = client.recv(1024).decode().strip()
    print(information, '\n')

def handle_shutdown(client_input, client):
    """
    Handles the shutdown which lets server know it wants to disconnect
    :param client_input: string
    :param client:
    """
    global index
    index = 1
    client.send(client_input.encode())
    new_message = client.recv(1024).decode().strip()
    print(new_message)

def handle_interaction (client):
    """
    Determines what the client input is and sends messages and info according to the input
    :param client:
    """
    global index
    while True:
        print("Please enter input, commands available: BALANCE, LIST, MARKET, BUY, SELL, SHUTDOWN, QUIT")
        print("Buy and sell structure: BUY/SELL StockSymbol Shares UserID", '\n')
        client_input = input ("Enter Input: ")
        first_command = client_input.split()

        match (first_command[0]):
            case "BALANCE" | "LIST" | "MARKET":
                handle_messages(client_input, client)
            case "BUY":
                handle_buy(client_input, client)
            case "SELL":
                handle_sell(client_input, client)
            case "SHUTDOWN":
                handle_shutdown(client_input, client)
            case "QUIT": #Breaks once user has inputted and already has inputed SHUTDOWN
                if index == 1:
                    break
                else:
                    print("Need to SHUTDOWN first")
            case _:
                print("Invalid Command", '\n')

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


connect_to_server()