import socket
import csv
import locale
import sys
import threading
import select
from pickle import GLOBAL

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

SERVER_PORT = 7715  # Chosen port number
STOCK_RECORDS_FILE = "stocks.csv"
USER_RECORDS_FILE = "users.csv"
MARKET_RECORDS_FILE = "market.csv"

stock_records = []          #List of stocks owned by users
user_records = []           #List of users
market_records = []         #List of stocks available to buy
active_connect = {}         #Track active connections
lock = threading.Lock()     #For safe thread activities
serverIndex = 0

def run_server():
    """
    Creates a loop that runs endlessly, waiting for connections.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #to allow reuse of address
    server_socket.bind(("localhost", SERVER_PORT))
    server_socket.listen(10) #Set liston to 10 for max of 10 connections
    print("Server is running on port", SERVER_PORT)
    global stock_records, user_records, market_records, active_connect, serverIndex, lock
    stock_records = loadRecords(STOCK_RECORDS_FILE)
    user_records = loadRecords(USER_RECORDS_FILE)
    market_records = loadRecords(MARKET_RECORDS_FILE)

    #Creating a thread pool of 10
    semaphore = threading.BoundedSemaphore(10)
    sockets_list = [server_socket]

    while True:

        if serverIndex == 0:
            #Read multiple sockets
            read_sockets,_,_ = select.select(sockets_list, [],[], 1)
            for soc in read_sockets:
                if soc == server_socket:
                    client_socket, client_address = server_socket.accept()
                    print("Accepted connection from:", client_address)
                    if semaphore.acquire(blocking=False):
                        with lock:
                            #Sets the connection to empty stds and not logged in for future checking
                            active_connect[client_socket] = {"logged_in": False, "user": None, "ip": client_address[0]}
                        #create a thread that will the function to handle the client with set params
                        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, semaphore))
                        client_thread.start()
                    else:
                        client_socket.close()
        else:
            break

    print("Shutting Down Server")
    #sys.exit()
    quit()


def handle_client(client_socket, client_address, semaphore):
    """
    Called when a client connection is accepted.
    Loops continuiously waiting for commands from the client, then performs the command.
    :param semaphore:
    :param client_socket:
    """
    global active_connect
    global lock

    try:
        userpass = (client_socket.recv(1024).decode().strip()).split()
        user_name = userpass[0]
        pass_word = userpass[1]
        print(f"Recieved {user_name} and {pass_word}")
        if isValidSignIn(user_name, pass_word):
            client_socket.send("200 OK\n".encode())
            activeUser = getUserByUsername(user_name)
        else:
            client_socket.send("401 Invalid Username / Password".encode())
            raise ValueError("Invalid username / password")
    except ValueError as e:
        print("Invalid username / password received, Disconnected")
    except:
        print("No username and password recieved, Disconencted")

    try:
        while True:
            try:
                command = client_socket.recv(1024).decode().strip()
                fullCommand = command.split()
                command = fullCommand[0]
            except:
                print("Connection disconnected from:", client_address)
                break

            #Split sent command into array of words and make command variable the first word


            # Ensure BUY and SELL is formatted correctly - ensure 3 parameters
            if command == "BUY" or command == "SELL":
                if not validCommand(client_socket, activeUser, command, fullCommand):
                    #TODO does a message need to be sent to client here?
                    continue

            match (command):
                case "MSGGET":
                    handle_msgget(client_socket)
                case "MSGSTORE":
                    handle_msgstore(client_socket)
                case "BALANCE":
                    handle_balance(client_socket, activeUser)
                case "LIST":
                    handle_list(client_socket, activeUser)
                case "MARKET":
                    handle_market(client_socket)
                case "BUY":
                    handle_buy(client_socket, activeUser, fullCommand)
                case "SELL":
                    handle_sell(client_socket, activeUser, fullCommand)
                case "SHUTDOWN":
                    handle_shutdown(client_socket)
                    break
                case _:
                    handle_unknownCommand(client_socket, command)
    finally:
        with lock:
            if client_socket in active_connect:
                del active_connect[client_socket]
        client_socket.close()
        semaphore.release()


def handle_msgget(client_socket):
    """
    Responsible for handling the MSGGET command from the client.
    Sends response "200 OK"
    :param client_socket:
    """
    response = "200 OK\n"
    client_socket.send(response.encode())

def handle_msgstore(client_socket):
    """
    Responsible for handling the MSGSTORE command from the client.
    Sends the response "200 OK" to the client to signal message can be sent.
    Then, the message is received from the client using the client socket and prints the message.
    :param client_socket:
    """
    client_socket.send("200 OK\n".encode())
    new_message = client_socket.recv(1024).decode().strip()
    print("Received new message:", new_message)

def handle_balance(client_socket, user):
    """
    Responsible for displaying the balance in USD for the user.
    :param client_socket:
    """
    print("Received: BALANCE")
    client_socket.send("200 OK\n".encode())

    fullName = user["first_name"] + " " + user["last_name"]
    formatted_balance = locale.currency(user["usd_balance"], grouping=True)
    bal = str(formatted_balance)
    client_socket.send(f"Balance for user {fullName}: {bal}\n".encode())

def handle_list(client_socket, user):
    """
    Responsible for displaying the list of stocks the user owns.
    :param client_socket:
    """
    print("Received: LIST")
    client_socket.send("200 OK\n".encode())

    #Create string of all records of owned stocks in database
    toSend = f"The list of records in the Stocks database for {user['first_name']} {user['last_name']}:\n"
    count = 0
    for record in stock_records:
        if (record["user_id"] == user["ID"]):
            count += 1
            cost = locale.currency(record["stock_balance"], grouping=True)
            toSend += str(count) + "  " + record["stock_symbol"] + " " + str(record["shares"]) + " @ " +\
                      str(cost) + " " + str(record["user_id"]) + "\n"
    client_socket.send(toSend.encode())

def handle_market(client_socket):
    """
    Responsible for displaying the list of currently available stocks to purchase on the market
    :param client_socket:
    """
    print("Received: MARKET")
    client_socket.send("200 OK\n".encode())

    #Create string of all stocks available for purchase
    toSend = "The current market has these stocks available:\n"
    for record in market_records:
        cost = locale.currency(float(record["stock_price"]), grouping=True)
        toSend += str(record["ID"]) + "  " + record["stock_symbol"] + " " + record["stock_name"] + " - " +\
                  str(cost) + "\n"
    client_socket.send(toSend.encode())

def handle_buy(client_socket, user, params, stock_str=None):
    """
    Handles BUY command. Finds the record in stocks, and adds the shares. Adds record if no record exists.
    :param client_socket:
    :param params: Array of original command from client
    """
    stock_symbol = params[1]
    shares = int(params[2])
    stock = find_stock(stock_symbol)
    print(f"Received: BUY {stock_symbol} {shares}")

    # First, check to see if the user already owns at least one share of that stock
    # If so, simply add more shares to that record
    recordCreated = False
    for record in stock_records:
        if record["stock_symbol"] == stock_symbol and record["user_id"] == user:
            number_shares = record["shares"]
            total_shares = shares + number_shares
            record["shares"] = total_shares
            recordCreated = True
    # create array of stock info to insert if existing record was not created
    if not recordCreated:
        stockToBuy = {
        "ID": len(stock_records) + 1,
        "stock_symbol": stock["stock_symbol"],
        "stock_name": stock["stock_name"],
        "shares": shares,
        "stock_balance": stock["stock_price"],
        "user_id": user["ID"]
        } #  len(stock_records) + 1, stock["stock_symbol"], stock["stock_name"], shares, stock["stock_price"], user}
        # insert into stock
        stock_records.append(stockToBuy)

    #update user's usd balance
    moneyRequired = shares * stock["stock_price"]
    newBalance = changeFunds("SUBTRACT", moneyRequired, user)
    newBalance = locale.currency(newBalance, grouping=True)
    newBalance = str(newBalance)
    shares = str(shares)

    #Send success message
    client_socket.send(f"200 OK\nBOUGHT {shares} SHARES OF {stock_symbol}. New balance: {newBalance}".encode())


def handle_sell(client_socket, user, params):
    """
    Handles SELL command. Finds the record in stocks, and deducts the shares. Removes record
    if at 0 shares.
    :param client_socket:
    :param params: Array of original command from client
    """
    stock_symbol = params[1]
    shares = int(params[2])
    stock = find_stock(stock_symbol)
    print(f"Received: SELL {stock_symbol} {shares}")

    # find record
    recordFound = False
    for record in stock_records:
        #Find record to remove stocks from
        if record["stock_symbol"] == stock_symbol and record["user_id"] == user["ID"]:
            total_shares = record["shares"]
            current_shares = total_shares - shares
            record["shares"] = current_shares
        #after removal, check to see if any shares remain. If not, remove record entirely
        if record["shares"] == 0:
            indexToDelete = record["ID"] - 1
            del stock_records[indexToDelete]
            #Need to renumber records since one was deleted, assuming not the last record
            if record["ID"] != len(stock_records):
                newID = 1
                for newRecord in stock_records:
                    newRecord["ID"] = newID
                    newID += 1
        if recordFound:
            break

    #update user's usd balance
    moneyOwed = shares * stock["stock_price"]
    newBalance = changeFunds("ADD", moneyOwed, user)
    newBalance = locale.currency(newBalance, grouping=True)
    newBalance = str(newBalance)
    shares = str(shares)

    #Send success message
    client_socket.send(f"200 OK\nSOLD {shares} SHARES OF {stock_symbol}. New balance: {newBalance}".encode())


def changeFunds(type, cost, user):
    """
    Changes a given user's money balance
    :param type: string, "ADD" or "SUBTRACT"
    :param cost: float, amount to add or subtract
    :param user: user record
    :return: float, new balance
    """
    currentMoney = user["usd_balance"]
    if (type == "SUBTRACT"):
        user["usd_balance"] = currentMoney - cost
    else:
        user["usd_balance"] = currentMoney + cost
    return user["usd_balance"]

def handle_invalid(client_socket, command, details):
    """
    Handles a command that starts with a valid command (BUY, SELL) but is not formatted correctly.
    :param client_socket:
    :param command: string - What the client sent
    :param details: string - Specific issue with the format
    """
    print(f"Received: Invalid command {command}")
    client_socket.send(f"403 Message Format Error\n{details}".encode())

def handle_unknownCommand(client_socket, command):
    """
    Handles unknown command
    :param client_socket:
    :param command: string - Command originally sent
    """
    print("Received Unknown Command: " + command)
    client_socket.send("400 Invalid Command\n".encode())


def find_stock(stockToBuy):
    """
    Finds a given stock in the market list based on the ticker
    :param stockToBuy: string symbol "("GOOG"
    :return: the array of the stock
    """
    for record in market_records:
        if record["stock_symbol"] == stockToBuy:
            return record


def validCommand(client_socket, user, command, fullCommand):
    """
    Makes sure the given command, BUY or SELL is in the correct format, while also ensuring the user can
    actually buy or sell whatever it is they're trying to buy or sell.
    :param client_socket:
    :param command: string
    :param fullCommand: array
    :return: True if buy or sell command CAN be performed
    """
    #Check for valid # of params (should be 4)
    if (len(fullCommand)) != 3:
        command = "INVALID"
        details = f"Invalid {command} command. Please format as: 'BUY STK 3' \n " +\
                  f"Where {command} is the command, STK is the symbol, and 3 is # of shares."
        handle_invalid(client_socket, command, details)
        return False

    #Check each parameter===============================
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

    #For buy, ensure buyer has enough money
    if fullCommand[0] == "BUY":
        current_stock = find_stock(stockToBuy)
        moneyRequired = shares * float(current_stock["stock_price"])
        wallet = user["usd_balance"]
        if  wallet < moneyRequired:
            command = "INVALID"
            details = f"Invalid {command} command. User does not have enough $."
            handle_invalid(client_socket, command, details)
            return False

    #For sell, ensure the user actually owns that stock and that amount of shares
    if fullCommand[0] == "SELL":
        numSharesOwned = 0
        #Count shares
        for stockRecord in stock_records: #for loop goes through stock list, but how they're stored doesn't really need to be loop
            if stockRecord["stock_symbol"] == stockToBuy and stockRecord["user_id"] == user["ID"]:
                numSharesOwned += stockRecord["shares"]
        #Check if user doesn't own shares at all of that stock
        if numSharesOwned == 0:
            command = "INVALID"
            details = f"Invalid {command} command. You do not have any shares of {stockToBuy}."
            handle_invalid(client_socket, command, details)
            return False
        #Also check if trying to sell more shares than owned
        elif shares > numSharesOwned:
            command = "INVALID"
            details = f"Invalid {command} command. You only have {numSharesOwned} shares. Cannot sell {shares}"
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

def getUserByUsername(username):
    """
    Gets a user's info by username and returns it (entire dictionary line)
    Assumes user is valid
    :param username:
    :return: user file
    """
    for user in user_records:
        if user["user_name"] == username:
            return user

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

def isValidSignIn(userToCheck, pw):
    """
    Checks if the user (which is attempting to log in) is valid, with an existing username and matching password
    :return: true if a username with matching password is found
    """
    for user in user_records:
        if user["user_name"] == userToCheck and user["password"] == pw:
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
            if f == USER_RECORDS_FILE:
                row["usd_balance"] = float(row["usd_balance"])
            elif f == STOCK_RECORDS_FILE:
                row["stock_balance"] = float(row["stock_balance"])
                row["shares"] = int(row["shares"])
                row["user_id"] = int(row["user_id"])
            elif f == MARKET_RECORDS_FILE:
                row["stock_price"] = float(row["stock_price"])

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
    return data

def handle_shutdown(client_socket):
    """
    Handles shutdown request from client. Will write back stocks and user files to their csv then close.
    :param client_socket:
    """
    print("Received: SHUTDOWN")
    global serverIndex

    #Write to file. Currently writing to stocks2 to debug. Needs to change to original filename: STOCK_RECORDS_FILE
    #Since this will write rows, we set for newline, Then writes to the rows into csvfile using writer
    with open('stocks.csv', 'w', newline='') as out_file:
        writer = csv.writer(out_file)
        writer.writerow(["ID", "stock_symbol", "stock_name", "shares", "stock_balance", "user_id"])  # Write header
        for record in stock_records:
            writer.writerow(
                [record["ID"], record["stock_symbol"], record["stock_name"], record["shares"], record["stock_balance"],
                 record["user_id"]])

    # Write user records using the same method as stocks
    with open('users.csv', 'w', newline='') as out_file:
        writer = csv.writer(out_file)
        writer.writerow(["ID", "first_name", "last_name", "user_name", "password", "usd_balance"])  # Write header
        for record in user_records:
            writer.writerow(
                [record["ID"], record["first_name"], record["last_name"], record["user_name"], record["password"],
                    record["usd_balance"]])

    client_socket.send("200 OK\n".encode())
    serverIndex = 1
    #sys.exit()


run_server()
