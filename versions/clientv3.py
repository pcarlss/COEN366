import socket

IP = socket.gethostbyname(socket.gethostname())
PORT = 1234
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024

import os

def put(client, filename):
    try:
        client.send("PUT".encode(FORMAT))
        client.send(filename.encode(FORMAT))
        
        file_path = "client_data/" + filename

        # Get the total size of the file
        file_size = os.path.getsize(file_path)
        client.send(str(file_size).encode(FORMAT))
        total_bytes_sent = 0

        with open(file_path, "rb") as file:
            while total_bytes_sent < file_size:
                # Read a chunk of data
                data = file.read(1024)

                # Send the chunk
                client.sendall(data)
                
                # Update the total bytes sent
                total_bytes_sent += len(data)

        # Check if the total bytes sent match the file size
        if total_bytes_sent == file_size:
            print("File sent successfully.")
        else:
            print("File sending incomplete.")

        # Receive acknowledgement from the server
        msg = client.recv(SIZE).decode(FORMAT)
        print(f"[SERVER]: {msg}")

    except FileNotFoundError:
        print(f"[CLIENT]: File '{filename}' not found.")


def get(client, filename):
    client.send(f"GET {filename}".encode(FORMAT))
    response = client.recv(SIZE).decode(FORMAT)

    if response == "FileExists":
        file_size = int(client.recv(SIZE).decode())  # Receive file size from server

        received_data = b""
        total_bytes_received = 0

        while total_bytes_received < file_size:
            data = client.recv(SIZE)
            received_data += data
            total_bytes_received += len(data)

        with open("client_data/" + filename, "wb") as file:
            file.write(received_data)
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
