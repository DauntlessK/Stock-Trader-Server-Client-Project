# StockTrader
Networking Project 2 - Stock Trading: Multiple clients with threads and select

#Student Info
Alexis Chavez-Guzman: alexiz@umich.edu
Kyle Breen-Bondie: kylebb@umich.edu

#Introduction:
Program implements a stock trading network that work on TCP sockets wth an upgraded multiple client to server architecture.
Program is implemented in a Windows platform. The server handles client inputs which are predefined. The commands added to the previous existing roster are LOOKUP, WHO, DEPOSIT, LOGIN, LOGOUT, and changes to previous commands.
Implements a CSV file for the stock market data and user data. Program has small changes such as including the concept of shares, as well as a market which holds a list of stocks that can be bought and their prices. 
Server is implemented in a localhost with a designated port.

#Instructions
Install python3 if not already installed.
Run the server script first.
Run the client script next.
Run the second client script next.
Log in into both clients using a username and password.
After succesfull connection, interaction can begin.
To disconnect from server, enter QUIT or LOGOUT.
To shutdown server, root user must enter SHUTDOWN.

#Student's Role

#Alexis Chavez-Guzman:
Implemented the following features: Method handling of the commands LOOKUP, WHO, and DEPOSIT. Added error handling and testing for these commands on both server and client.
Other Responsibilities: Responsible for implementing a multiple client functions using threads and select.

#Kyle Breen-Bondie:
Implemented the following features: Method handling for the LOGIN and LOGOUT commands while changing to older commands to fit requirements and a multiple client structure.
Other Responsibilities: Responsible for major debugging of the system and issues with commands, both old and new commands.

#Bugs
Only one bug found: 
Client crashes when ran before the server, the server must run first as the client doesn't connect.

#Youtube link to video
https://youtu.be/yGv214VkX54