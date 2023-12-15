import socket

IP = socket.gethostbyname(socket.gethostname())
PORT = 1234
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 4096

def put(client, filename):
    try:
        with open("client_data/" + filename, "rb") as file:
            data = file.read()

        client.send("PUT".encode(FORMAT))
        client.send(filename.encode(FORMAT))
        msg = client.recv(SIZE).decode(FORMAT)
        print(f"[SERVER]: {msg}")

        client.sendall(data)
        msg = client.recv(SIZE).decode(FORMAT)
        print(f"[SERVER]: {msg}")

    except FileNotFoundError:
        print(f"[CLIENT]: File '{filename}' not found.")

def get(client, filename):
    client.send(f"GET {filename}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)

    if response == "FileExists":
        file_data = client.recv(SIZE)
        with open("client_data/" + filename, "wb") as file:
            file.write(file_data)
        print(f"[CLIENT]: File '{filename}' received and saved.")
    else:
        print(f"[CLIENT]: File '{filename}' does not exist on the server.")

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

    client.close()

if __name__ == "__main__":
    main()
