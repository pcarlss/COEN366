import socket
import threading
import os

IP = socket.gethostbyname(socket.gethostname())
PORT = 1234
ADDR = (IP, PORT)
SIZE = 4096

def handle_client_connection(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    while True:
        data = conn.recv(SIZE).decode()
        if not data:
            break

        parts = data.split()
        command = parts[0]

        if command == "GET":
            if len(parts) == 2:
                filename = parts[1]
                file_path = "database/" + filename
                if os.path.exists(file_path):
                    conn.send("FileExists".encode())
                    with open(file_path, "rb") as file:
                        file_data = file.read()
                        conn.sendall(file_data)
                else:
                    conn.send("FileNotExists".encode())
            else:
                conn.send("InvalidCommand".encode())
        elif command == "PUT":
            filename = conn.recv(SIZE).decode()
            conn.send("FilenameReceived".encode())

            file_data = conn.recv(SIZE)
            with open("database/" + filename, "wb") as file:
                file.write(file_data)
            conn.send("FileReceived".encode())

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
