import socket
import csv
import locale

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

SERVER_PORT = 7715  # Chosen port number
STOCK_RECORDS_FILE = "stocks.csv"
USER_RECORDS_FILE = "users.csv"

stock_records = []
user_records = []


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
        print("Command: " + command)
        match (command):
            case "MSGGET":
                handle_msgget(client_socket)
            case "MSGSTORE":
                handle_msgstore(client_socket)
            case "BALANCE":
                handle_balance(client_socket)
            case "LIST":
                handle_list(client_socket)
            case "BUY":
                handle_buy(client_socket)
            case "SELL":
                handle_sell(client_socket)
            case _:
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

def handle_balance(client_socket):
    """
    Responsible for displaying the balance in USD for the user.
    :param client_socket:
    :return:
    """
    print("Received: BALANCE")
    client_socket.send("200 OK\n".encode())

    fullName = user_records[0]["first_name"] + " " + user_records[0]["last_name"]
    formatted_balance = locale.currency(user_records[0]["usd_balance"], grouping=True)
    bal = str(formatted_balance)
    client_socket.send(f"Balance for user {fullName}: ${bal}\n".encode())

def handle_list(client_socket):
    """
    Responsible for displaying the list of stocks the user owns.
    :param client_socket:
    :return:
    """
    print("Received: LIST")
    client_socket.send("200 OK\n".encode())

    toSend = "The list of records in the Stocks database for user 1:\n"
    count = 0
    for record in stock_records:
        if (record["user_id"] == 1):
            count += 1
            cost = locale.currency(record["stock_balance"], grouping=True)
            toSend += str(count) + "  " + record["stock_symbol"] + " " + record["shares"] + " @ $" +\
                      str(cost) + " " + str(record["user_id"]) + "\n"
    client_socket.send(toSend.encode())

def handle_buy(client_socket):
    pass

def handle_sell(client_socket):
    pass


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
            "shares": 1,
            "stock_balance": 3.70,
            "user_id": 1}]
    print(data[1]["ID"])
    return data

run_server()
