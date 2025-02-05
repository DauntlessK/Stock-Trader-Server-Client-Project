import socket
import csv

SERVER_PORT = 7715  # Chosen port number
STOCK_RECORDS_FILE = "stocks.csv"
USER_RECORDS_FILE = "users.csv"


def run_server():
    """
    Creates a loop that runs endlessly, waiting for connections.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", SERVER_PORT))
    server_socket.listen(1)
    print("Server is running on port", SERVER_PORT)
    stock_records = loadRecords(STOCK_RECORDS_FILE)
    user_records = loadRecords(USER_RECORDS_FILE)

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

def loadRecords(f):
    """
    Loads records from file into a list of dictionaries.
    (Each element of the list created is 1 dictionary record)
    :return: List of Dictionaries
    """
    with open(f, 'r') as file:
        csv_reader = csv.DictReader(file)
        recordCount = 1
        data = []
        for row in csv_reader:
            row["ID"] = recordCount
            recordCount += 1
            if (f == USER_RECORDS_FILE):
                row["usd_balance"] = int(row["usd_balance"])
            elif (f == STOCK_RECORDS_FILE):
                row["stock_balance"] = float(row["stock_balance"])
                row["user_id"] = int(row["user_id"])
            data.append(row)

    #check if blank - if blank and creating user list then add default user
    if len(data) == 0 and f == USER_RECORDS_FILE:
        data = [{
            "ID" : 1,
            "first_name" : "fname",
            "last_name" : "lname",
            "user_name": "username",
            "password" : "admin",
            "usd_balance" : 100}]
    #check if blank - if blank and creating stock list then add default stock
    elif len(data) == 0 and f == STOCK_RECORDS_FILE:
        data = [{
            "ID": 1,
            "stock_symbol": "DEF",
            "stock_name": "Default",
            "stock_balance": 3.70,
            "user_id": 1}]
    return data

def createRecord():
    pass

run_server()
