# StockTrader
Networking Project 1 - Stock Trading

#Student Info
Alexis Chavez-Guzman: alexiz@umich.edu
Kyle Breen-Bondie: kylebb@umich.edu

#Introduction:
Program implements a stock trading network that work on TCP sockets wth a client-server architecture.
Program is implemented in a Windows platform. The server handles client inputs which are predefined. These commands are from BUY, SELL, LIST, BALANCE, and MARKET.
Implements a CSV file for the stock market data and user data. Program has small changes such as including the concept of shares, as well as a market which holds a list of stocks that can be bought and their prices. 
Server is implemented in a localhost with a designated port.

#Instructions
Install python3 if not already installed.
Run the server script first.
Run the client script next.
After succesfull connection, interaction can begin.
To disconnect from server, enter QUIT.
To shutdown server, enter SHUTDOWN.

#Student's Role

#Alexis Chavez-Guzman:
Implemented the following features: The connection to the server from client, predefined command inputs, client closing and disconnecting, 
and small error handling for the commands. 
Other Responsibilities: Responsible for general debugging and code fixing on both server and client side.
#Kyle Breen-Bondie:
Implemented the following features: The establishment of server and handling of client, handling of commands in the server, csv files where data is stored,
error handling for BUY and SELL commands, csv file reading, and csv file storing.
Other Responsibilities: Responsible for debugging server issues and other bug fixes.

#Bugs
Two bugs that were not fully fixed.
Forceful detachment from server crashes the server. Terminating the client early causes an execption.
Client crashes when ran before the server, the server must run first as the client doesn't connect.

#Youtube link to video
https://youtu.be/aCvJo9Zev0c?si=23uMeIv2MTBTGAzg
