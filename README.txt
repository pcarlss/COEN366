# COEN366
simple FTP via Python sockets

Authors:
Philip Carlsson-Coulombe 40208572
Qian Yi Wang 40211303

Please open the `server.py` and `client.py` in your preferred IDE or command line environment.
Run the `server.py` script first followed by the `client.py` script.




Server.py: 
--------------------------------------------------
On the server side you should see the following:

	[STARTING] Server is starting.


Client.py: 
--------------------------------------------------
On the client side you should see the following:

	Enter IP address (leave empty for default):





On the client side, press Enter twice to use default values for the IP and Port numbers.
You'll then be prompted to choose between TCP and UDP; enter your choice accordingly.

After that, you should receive a message on the server side acknowledging the connection, which allows the client side to start inputting commands, as shown below:




Server.py: 
--------------------------------------------------
[LISTENING] Server is listening on: ('X.X.X.X', 5555)

[NEW CONNECTION] ('X.X.X.X', 5555) connected.



Client.py: 
--------------------------------------------------
Enter command: 




Use the following commands to interact with the script:
------------------------------------------------------------
1. put <filename>                        | upload file
2. get <filename>                        | retrieve file
3. summary <filename>                    | statistical summary
4. change <oldfilename> <newfilename>    | rename file
5. bye                                   | disconnect
------------------------------------------------------------


When the "bye" command is used, server.py will continue running and listen for any new connections.
If you wish to reconnect, you'll need to rerun the client.py script for each new connection.


