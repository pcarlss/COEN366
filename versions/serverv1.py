import socket
import threading
import os

IP = socket.gethostbyname(socket.gethostname())
PORT = 1234
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"

def handle_client_connection(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        if not data:
            break

        parts = data.split()
        command = parts[0]

        if command == "GET":
            if len(parts) == 2:  # Ensure the command format is correct
                filename = parts[1]
                if os.path.exists("database/" + filename):
                    conn.send("FileExists".encode(FORMAT))
                    with open("database/" + filename, "r") as file:
                        file_data = file.read()
                        conn.send(file_data.encode(FORMAT))
                else:
                    conn.send("FileNotExists".encode(FORMAT))
            else:
                conn.send("InvalidCommand".encode(FORMAT))  # Send an error response for incorrect command format
        elif command == "PUT":
            filename = conn.recv(SIZE).decode(FORMAT)
            conn.send("FilenameReceived".encode(FORMAT))

            file_data = conn.recv(SIZE).decode(FORMAT)
            with open("database/" + filename, "w") as file:
                file.write(file_data)
            conn.send("FileReceived".encode(FORMAT))

    conn.close()
    print(f"[DISCONNECTED] {addr} disconnected.")

def main():
    print("[STARTING] Server is starting.")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print("[LISTENING] Server is listening.")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client_connection, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    main()
