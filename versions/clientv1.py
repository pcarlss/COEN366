import socket

IP = socket.gethostbyname(socket.gethostname())
PORT = 1234
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024

def put(client, filename):
    """ Opening and reading the file data. """
    file = open("client_data/"+filename, "r")
    data = file.read()

    """ Sending the command, filename, and file data to the server. """
    client.send("PUT".encode(FORMAT))
    client.send(filename.encode(FORMAT))
    msg = client.recv(SIZE).decode(FORMAT)
    print(f"[SERVER]: {msg}")

    """ Sending the file data to the server. """
    client.send(data.encode(FORMAT))
    msg = client.recv(SIZE).decode(FORMAT)
    print(f"[SERVER]: {msg}")

    """ Closing the file. """
    file.close()

def get(client, filename):
    """ Sending the command and filename to the server to retrieve the file. """
    client.send(f"GET {filename}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)

    if response == "FileExists":
        """ Receiving the file data from the server. """
        file_data = client.recv(SIZE).decode(FORMAT)

        """ Saving the received file data to a new file. """
        with open("client_data/" + filename, "w") as file:
            file.write(file_data)
        print(f"[CLIENT]: File '{filename}' received and saved.")
    else:
        print(f"[CLIENT]: File '{filename}' does not exist on the server.")

def main():
    """ Staring a TCP socket. """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    """ Connecting to the server. """
    client.connect(ADDR)

    while True:
        command = input("Enter your choice (put/get/quit/help): ").lower()

        if command.startswith("put"):
            parts = command.split()
            if len(parts) == 2:
                filename = parts[1]
                put(client, filename)
            else:
                print("Invalid input format. Example: put test.txt")


        elif command.startswith("get"):
            parts = command.split()
            if len(parts) == 2:
                filename = parts[1]
                get(client, filename)
            else:
                print("Invalid input format. Example: get test.txt")

        elif command == "quit":
            client.send("quit".encode(FORMAT))
            client.close()
            print("Connection closed.")
            break

        elif command == "help":
            print("\n\n------------------------------------------------------------")
            print("1. put <filename>                        | upload file")
            print("2. get <filename>                        | retrieve file")
            print("3. summary <filename>                    | statistical summary")
            print("4. change <oldfilename> <newfilename>    | rename file")
            print("5. quit                                  | disconnect")
            print("------------------------------------------------------------\n\n")

        else:
            print("Invalid choice. Please choose again.")

    """ Closing the connection from the server. """
    client.close()

if __name__ == "__main__":
    main()
