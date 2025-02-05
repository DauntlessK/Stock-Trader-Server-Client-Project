import socket
import csv
import locale
from pickle import GLOBAL

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

SERVER_PORT = 7715  # Chosen port number
STOCK_RECORDS_FILE = "stocks.csv"
USER_RECORDS_FILE = "users.csv"
MARKET_RECORDS_FILE = "market.csv"

stock_records = []          #List of stocks owned by users
user_records = []           #List of users
market_records = []         #List of stocks available to buy


def run_server():
    """
    Creates a loop that runs endlessly, waiting for connections.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", SERVER_PORT))
    server_socket.listen(1)
    print("Server is running on port", SERVER_PORT)
    global stock_records
    global user_records
    global market_records
    stock_records = loadRecords(STOCK_RECORDS_FILE)
    user_records = loadRecords(USER_RECORDS_FILE)
    market_records = loadRecords(MARKET_RECORDS_FILE)

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

        #Split sent command into array of words and make command variable the first word
        fullCommand = command.split()
        command = fullCommand[0]

        # Ensure BUY and SELL is formatted correctly - ensure 4 parameters
        if command == "BUY" or command == "SELL":
            valid = validateCommand(client_socket, command, fullCommand)
            if valid == False:
                break

        match (command):
            case "MSGGET":
                handle_msgget(client_socket)
            case "MSGSTORE":
                handle_msgstore(client_socket)
            case "BALANCE":
                handle_balance(client_socket)
            case "LIST":
                handle_list(client_socket)
            case "MARKET":
                handle_market(client_socket)
            case "BUY":
                handle_buy(client_socket, fullCommand)
            case "SELL":
                handle_sell(client_socket, fullCommand)
            case _:
                handle_unknownCommand(client_socket, command)
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

    #Create string of all records of owned stocks in database
    toSend = "The list of records in the Stocks database for user 1:\n"
    count = 0
    for record in stock_records:
        if (record["user_id"] == 1):
            count += 1
            cost = locale.currency(record["stock_balance"], grouping=True)
            toSend += str(count) + "  " + record["stock_symbol"] + " " + record["shares"] + " @ $" +\
                      str(cost) + " " + str(record["user_id"]) + "\n"
    client_socket.send(toSend.encode())

def handle_market(client_socket):
    """
    Responsible for displaying the list of currently available stocks to purchase on the market
    :param client_socket:
    :return:
    """
    print("Received: MARKET")
    client_socket.send("200 OK\n".encode())

    #Create string of all stocks available for purchase
    toSend = "The current market has these stocks available:\n"
    for record in market_records:
        cost = locale.currency(float(record["stock_price"]), grouping=True)
        toSend += str(record["ID"]) + "  " + record["stock_symbol"] + " " + record["stock_name"] + " - $" +\
                  str(cost) + "\n"
    client_socket.send(toSend.encode())

def handle_buy(client_socket, params):
    pass


def handle_sell(client_socket, params):
    pass

def handle_invalid(client_socket, command, details):
    print(f"Received: Invalid command {command}")
    client_socket.send(f"403 Message Format Error\n{details}".encode())

def handle_unknownCommand(client_socket, command):
    print("Received Unknown Command: " + command)
    client_socket.send("400 Invalid Command\n".encode())


def find_stock(stockToBuy):
    for record in market_records:
        if record["stock_symbol"] == stockToBuy:
            return record


def validateCommand(client_socket, command, fullCommand):
    """
    Makes sure the given command, BUY or SELL is in the correct format, while also ensuring the user can
    actually buy or sell whatever it is they're trying to buy or sell.
    :param client_socket:
    :param command: string
    :param fullCommand: array
    :return: True if buy or sell command CAN be performed
    """
    #Check for valid # of params (should be 4)
    if (len(fullCommand)) != 4:
        command = "INVALID"
        details = f"Invalid {command} command. Please format as: 'BUY STK 3 1' \n " +\
                  f"Where {command} is the command, STK is the symbol, 3 is # of shares, and 1 is your user ID."
        handle_invalid(client_socket, command, details)
        return False

    #Check each parameter-------
    #Check stock symbol
    stockToBuy = fullCommand[1]
    if not isValidStock(stockToBuy):
        command = "INVALID"
        details = f"Invalid {command} command. Stock {fullCommand[1]} does not exist."
        handle_invalid(client_socket, command, details)
        return False

    #Check share count purchase
    try:
        shares = int(fullCommand[2])
    except:
        command = "INVALID"
        details = f"Invalid {command} command. Enter valid # of shares to purchase."
        handle_invalid(client_socket, command, details)
        return False
    #Check valid user
    try:
        user = int(fullCommand[3])
        if not isValidUser(user):
            command = "INVALID"
            details = f"Invalid {command} command. User {user} does not exist."
            handle_invalid(client_socket, command, details)
            return False
    except:
        command = "INVALID"
        details = f"Invalid {command} command. Enter valid # for the user."
        handle_invalid(client_socket, command, details)
        return False

    #For buy, ensure buyer has enough money
    if fullCommand[0] == "BUY":
        current_stock = find_stock(stockToBuy)
        moneyRequired = shares * float(current_stock["stock_price"])
        val = user_records[user - 1]["usd_balance"]
        if  val < moneyRequired:
            command = "INVALID"
            details = f"Invalid {command} command. User does not have enough $."
            handle_invalid(client_socket, command, details)
            return False

    #For sell, ensure the user actually owns that stock and that amount of shares
    if fullCommand[0] == "SELL":
        numSharesOwned = 0
        for transaction in stock_records:
            if transaction["stock_symbol"] == stockToBuy and transaction["user_id"] == user:
                numSharesOwned += 1
        if numSharesOwned == 0:
            command = "INVALID"
            details = f"Invalid {command} command. User does not have any shares of {stockToBuy}."
            handle_invalid(client_socket, command, details)
            return False
        return True



def isValidStock(stockToCheck):
    """
    Checks if the given stock symbol exists in the market (market csv)
    :param stockToCheck: string symbol "AAPL"
    :return: True if the ticker is in the market csv
    """
    for stock in market_records:
        if stock["stock_symbol"] == stockToCheck:
            return True
    return False

def isValidUser(userToCheck):
    """
    Checks if the given user exists in the users database)
    :param user: int user #
    :return: True if the user is in the users csv
    """
    for user in user_records:
        #Convert to string in order to compare
        strUser = str(userToCheck)
        if user["ID"] == userToCheck:
            return True
    return False


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
